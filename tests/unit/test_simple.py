def test_index(webtest):
    resp = webtest.get('/')

    assert resp.status_code == 200
    assert resp.content_type == 'text/html'


def test_not_found(webtest):
    resp = webtest.get('/asdasdasd')

    assert resp.status_code == 404
