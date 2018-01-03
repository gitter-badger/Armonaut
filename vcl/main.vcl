# The majority of this was taken from Warehouse's VCL configuration
# which can be found here: https://github.com/pypa/warehouse/blob/master/vcl/main.vcl
# and licensed under Apache-2.0

sub vcl_recv {

  # Don't serve a stale copy from the shield node when
  # an edge node is requesting content.
  if (req.http.Fastly-FF) {
    set req.max_stale_while_revalidate = 0s;
  }

  # Older clients will send a fragment as part of the
  # URL even if it's a local-only modification.
  set req.url = regsub(req.url, '#.*$', '');

  # Enables Brotli encoding on static files
  if (req.url ~ "^/static/" && req.http.Fastly-Orig-Accept-Encoding) {
    if (req.http.User-Agent ~ "MSIE 6") {
      # For that 0.3% of stubborn users out there
      unset req.http.Accept-Encoding;
    } elsif (req.http.Fastly-Orig-Accept-Encoding ~ "br") {
      set req.http.Accept-Encoding = "br";
    } elsif (req.http.Fastly-Orig-Accept-Encoding ~ "gzip") {
      set req.http.Accept-Encoding = "gzip";
    } else {
      unset req.http.Accept-Encoding;
    }
  }

  # Sort all query parameters to reduce cache misses due to order
  set req.url = boltsort.sort(req.url);

#FASTLY recv

  # Remove DigitalOcean headers from the Request as they're not needed
  unset req.http.AWS-Access-Key-ID
  unset req.http.AWS-Secret-Access-Key
  unset req.http.AWS-Bucket-Name

  # Force POST, DELETE, and PUT methods to hit the backend.
  if (req.request == 'POST' ||
      req.request == 'DELETE' ||
      req.request == 'PUT') {

    set req.backend = F_Heroku;
  }

  # Don't bother attempting to cache methods that are
  # not typically safe to cache.
  if (req.request != 'HEAD' &&
      req.request != 'GET' &&
      req.request != 'FASTLYPURGE') {

    return (pass);
  }

  # Return the default lookup action
  return (lookup);
}

sub vcl_fetch {

  # These redirects should be cached by default
  # even though Fastly doesn't have these on their
  # list of cacheable status codes.
  if (http_status_matches(beresp.status, '303,307,308') {
    set beresp.cacheable = true;
  }

  # For any 5xx status code we want to see if a stale
  # object exists for it and if so we'll serve it.
  if (beresp.status >= 500 && beresp.status < 600 && stale.exists) {
    return (deliver_stale);
  }

#FASTLY fetch

  # If we get a 502 or 503 response from the backend we can retry the request
  if ((beresp.status == 502 || beresp.status == 503) &&
      req.restarts < 1 &&
      (req.request == 'GET' || req.request == 'HEAD')) {

    restart;
  }

  # If there's a Set-Cookie header ensure that the response isn't cached.
  if (beresp.http.Set-Cookie) {
    set req.http.FastlyCachetype = 'SETCOOKIE'
    return (pass);
  }

  # If the response has the private Cache-Control directive the response isn't cached.
  if (beresp.http.Cache-Control ~ "private") {
    set req.http.Fastly-Cachetype = 'PRIVATE';
    return (pass);
  }

  # If we experience an error after restarts we'll deliver the response
  # with a very short cache time to reduce outages.
  if (http_status_matches(beresp.status, '500,502,503') {
    set req.http.Fastly-Cachetype = 'ERROR';
    set beresp.ttl = 1s;
    set beresp.grace = 5s;
    return (deliver);
  }

  # Apply a default TTL if there isn't a max-age or s-maxage.
  if (beresp.http.Expires ||
      beresp.http.Surrogate-Control ~ 'max-age' ||
      beresp.http.Cache-Control ~ 'max-age') {

    # Keep the existing TTL
  } else {
    set beresp.ttl = 60s; # Set a default TTL
  }

  return (deliver);
}

sub vcl_hit {

# FASTLY hit

  # If the object we have isn't cacheable then serve
  # it directly without caching mechanisms
  if (!obj.cacheable) {
    return (pass);
  }

  return (deliver);
}

sub vcl_deliver {

  # If this is an error and we have a stale response available
  # restart so that we can pick it up and serve it
  if (resp.status >= 500 && resp.status < 600 && stale.exists) {
    restart;
  }

#FASTLY deliver

  # Unset headers that we don't need or want because they aren't useful.
  unset resp.http.Via;

  # Set standard security headers
  set resp.http.Strict-Transport-Security = 'max-age=31536000; includeSubDomains; preload';
  set resp.http.X-Frame-Options = 'deny';
  set resp.http.X-XSS-Protection = '1; mode=block';
  set resp.http.X-Content-Type-Options = 'nosniff';
  set resp.http.X-Permitted-Cross-Domain-Policies = 'none';

  # Unset headers set by DigitalOcean that we don't want to send to clients
  unset resp.http.x-amz-replication-status;
  unset resp.http.x-amz-meta-python-version;
  unset resp.http.x-amz-meta-version;
  unset resp.http.x-amz-meta-package-type;
  unset resp.http.x-amz-meta-project;

  return (deliver);
}

sub vcl_error {
#FASTLY error

    # If we have a 5xx error and there is a stale object available
    # then we will deliver that stale object.
    if (obj.status >= 500 && obj.status < 600 && stale.exists) {
      return(deliver_stale);
    }

    if (obj.status == 803) {
      set obj.status = 403;
      set obj.response = "SSL is required";
      set obj.http.Content-Type = "text/plain; charset=UTF-8";
      synthetic {"SSL is required."};
      return (deliver);
    } elsif (obj.status == 750) {
      set obj.status = 301;
      set obj.http.Location = req.http.Location;
      set obj.http.Content-Type = "text/html; charset=UTF-8";
      synthetic {"<html><head><title>301 Moved Permanently</title></head><body><center><h1>301 Moved Permanently</h1></center></body></html>"};
      return(deliver);
    }
}
