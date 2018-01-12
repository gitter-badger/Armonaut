# Configuring the Build

## Example `.armonaut.yml` file used by Armonaut

```yaml
services:
  redis: latest
  postgresql: 9.6
  rabbitmq: latest
  
env:
  global:
    - ARMONAUT_ENV=development
    - SECRET_KEY=notasecret
    - DATABASE_URL=postgresql://postgres@localhost:5432/armonaut
    - REDIS_URL=redis://localhost:6379/0
    - AMQP_URL=amqp://guest@localhost:5672//

matrix:
  include:
    # Code quality
    - python: 3.6-dev
      install:
        - python -m pip install -r dev-requirements.txt
      script:
        - flake8

    # Unit tests
    - python: 3.6-dev
      install:
        - python -m pip install -r requirements.txt -r dev-requirements.txt
      script:
        - pytest tests/unit/
      after_success:
        - codecov

    # Integration tests
    - python: 3.6-dev
      node: 8
      install:
        - python -m pip install -r requirements.txt -r dev-requirements.txt
        - npm install -g gulp-cli
        - npm install
        - gulp
      script:
        - pytest tests/integration/
      after_success:
        - codecov
```
