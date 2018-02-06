# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added GitHub OAuth service.
- Added Object Storage support with DigitalOcean Spaces.
- Added Projects, Roles, and Accounts.
- Added GitHub webhook service.
- Added basic login template.
- Added BasicAuth and Session-based authentication.
- Added password reset token service.
- Added default XSS protection via headers.
- Added logging framework.
- Added a Changelog.
- Added Sentry integration support.
- Added HTTP cache control and conditional responses.
- Added sessions support via Redis.
- Added a Code of Conduct.
- Added `Content-Security-Policy` support.
- Added CSRF protections for views.
- Added static resource serving with Whitenoise.
- Added emailing SMTP server for development
- Added Alembic migration support.
- Added support for rate-limiting.
- Added Jinja2 rendering of templates.
- Added Pyramid debug toolbar for development.
- Added Gulp configuration for compiling static resources.
- Added Dockerfile and Docker-Compose setup for testing and development.

### Developer Tools

- Added `armonaut db ...` tools for managing migrations via Alembic.
- Added `armonaut ctrl ...` tool for controlling `docker-compose` commands and
  running all tests against the local build.
- Added symlinks within the `Dockerfile` for mapping `python3` -> `python` along
  with all other tools suffixed with 3 for ease-of-use.

[Unreleased]: https://github.com/SethMichaelLarson/Armonaut/compare/0d5db69a6fe58fcf21caef3b3ee89777796aaa6d...HEAD
