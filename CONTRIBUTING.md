# Contributing to Armonaut

Thanks for considering contributing to Armonaut! Before contributing make sure you
are capable of and willing for your work being released under the
[Apache-2.0 license](https://github.com/SethMichaelLarson/Armonaut/blob/master/LICENSE)
such as if you're currently working for a client or corporation.

## Setting up your Tools and Workspace

This guide is written for Ubuntu 17.10 but the workflow will be similar compared to other Linux platforms.
Development is going to be tough on Windows systems because of Docker-Compose so I sadly can't recommend Windows
for anything beyond small changes. Sorry! (I use VirtualBox to virtualize Ubuntu 17.10 on my desktop)

Ensure that when you execute `python3 --version` the output is similar to the following:
```bash
$ python3 --version
Python 3.6.4
```

**NOTE:** Ubuntu 17.10 packages Python 3.6 by default. Armonaut requires Python 3.6+.
If you're using a different platform you must install Python 3.6 along with virtualenv
and pip another way.  I suggest [`pyenv`](https://github.com/pyenv/pyenv) but there are
other ways as well. Google is your friend!

### Installing Dependencies

```bash
sudo apt-get update
sudo apt-get install -y git \
                        build-essential \
                        apt-transport-https \
                        ca-certificates \
                        curl \
                        software-properties-common \
                        python3-venv \
                        python3-pip
```

### Installing Docker Community Edition

```bash
# Installing Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce

# Starting the dockerd service and making it auto-start on boot.
sudo service docker start
sudo systemctl enable docker

# Create the docker group and add the current user to the group.
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker # This command logs you into the docker group
```

After installing everything you should be able to run the following command:

**NOTE:** At the time of writing this the version of Docker CE was 17.12.0

```bash
$ docker --version
Docker version 17.12.0-ce, build c97c6d6
```

### Installing Docker-Compose

```bash
sudo curl -L https://github.com/docker/compose/releases/download/1.18.0/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

After installing this you should be able to run the following command:

**NOTE:** At the time of writing this the version of Docker CE was 1.18.0

```bash
docker-compose --version
```

### Installing Node, npm, and Gulp

We use Node, npm, and Gulp to build our static JavaScript and SCSS
files for Armonaut. If you're only modifying Python code you don't
need to take these steps, they're taken care of within Dockerfiles.

```bash
# Installing Node 8.x
curl -sL https://deb.nodesource.com/setup_8.x | sudo -E bash -
sudo apt-get install nodejs

# Installing Gulp and dependencies
sudo npm install --global gulp-cli
npm install
```

### Creating a Fork of Armonaut

Sign in with your GitHub account and click the [fork] button for Armonaut.
This should create a repository in your GitHub account named `[YOUR ACCOUNT]/Armonaut`.

Open a terminal and `cd` to a directory where you'd like your fork to reside.
Run the following command in the terminal:

```bash
git clone https://github.com/[YOUR ACCOUNT]/Armonaut
```

After this completes there should be a directory in your current working directory
named `Armonaut`. Use `cd` to go into this directory.

### Setting up a Virtualenv

```bash
python3 -m venv venv/
source venv/bin/activate
python -m pip install -r requirements.txt -r dev-requirements.txt
```

From here  you should have a functional fork for Armonaut. You can make sure you've
got everything configured properly by running the unit tests and integration tests (see below) 

To update all your dependencies use the following command:

```bash
python3 -m venv venv/
source venv/bin/activate
python -m pip install -U -r requirements.txt -r dev-requirements.txt
```

To deactivate that virtualenv use the following command:

```bash
deactivate
```

### Building all Docker images with Docker-Compose

Run the following command to pull all containers required for running
Armonaut locally in development mode.

**NOTE:** This command will take a while to execute the first time.
Any time your run this command after this will be much faster due to caching of containers and their layers.
Every time you modify code should only take a few seconds to run the next time.

```bash
docker-compose up
# To stop hosting locally use Ctrl+C
```

Whenever you make modifications to the Armonaut codebase run the following commands to update the container:

```bash
docker-compose build
```

### Building static resources with Gulp, Sass, and Uglify

When you make modifications to static resources make sure to build them again with Gulp.

```bash
# Build all static resources
gulp

# Watch static resources and build automatically when changes are detected
gulp watch
```

All stylesheets are found in `armonaut/static/scss/*` and all JavaScript is found
in  `armonaut/static/js/*`.

### Syncing your Fork with the latest `master` branch

When your local fork becomes out of date with other changes that have been merged into `master`
you must update your local fork in order to make merging future Pull Requests from your fork go smoothly.

```bash
# Checkout the `master` branch
git checkout master

# Reset hard against HEAD to make sure you have no local changes
git reset --hard HEAD

# Pull the latest changes from `upstream/master`
git pull upstream master

# Push the latest changes to GitHub for your fork
git push origin master
```

### Installing PyCharm (Optional)

PyCharm (created by JetBrains) is the IDE that I use to develop Armonaut.
I highly suggest it for people who don't already have a workflow solidified.

```bash
sudo apt-get install -y ubuntu-make
umake ide pycharm
```

**NOTE:** If you're using Ubuntu <=17.04 then you must add the following repository before installing `umake`.
```bash
sudo add-apt-repository -y ppa:ubuntu-desktop/ubuntu-make
sudo apt-get update
```

Once you launch and open Armonaut in your PyCharm IDE go into `File -> Settings -> Project: Armonaut -> Project Interpreter`
select the gear/cog to add a local virtual environment. Select `Existing Environment` and choose your `.../Armonaut/venv/bin/python`.
This will allow you to use hinting and auto-complete for all your installed modules.

## Making changes to Armonaut

### Using the Pyramid Debugtoolbar

The debug toolbar can be found by clicking the red box on the right side of
any page rendered on the web application running in `DEVELOPMENT` mode.
After clicking this button you will be brought to a menu with many options
for debugging how the views and requests are processed by the web application.

Use this for initial performance testing and debugging purposes.

See additional [documentation about the toolbar](https://docs.pylonsproject.org/projects/pyramid_debugtoolbar/en/latest/#usage) for more information.

### Linting your code with Flake8

Armonaut uses [flake8](http://flake8.pycqa.org/en/latest/) as a code linting tool
in order to catch defects and to keep code maintainabily high. Our only modification
to flake8's default configuration is increasing maximum line length to 99 characters
instead of 79 due to modern IDEs and screen sizes.

```bash
flake8  # You can run this command anytime with the virtualenv active
```

### Running unit tests

Unit tests are smaller and faster running tests that only test specific sub-components
of the system instead of the system as a whole.

Unit tests are run and must pass for each commit that is submitted to GitHub.

```bash
docker-compose run web pytest tests/unit/
```

### Running integration tests

Integration tests are longer tests that test the full functionality of the system
and launch browsers to ensure that the web application renders correctly on
all major browsers. Only run integration tests once all unit tests are passing.

Integration tests are run and must pass for each commit that is submitted to GitHub.

```bash
docker-compose run web pytest tests/integration/
```

### Running render tests

Render tests are tests that use Needle+Selenium in order to take pictures of the
user interface in order to detect changes. When changing the user interface you
will see these tests sometimes fail and that's okay! It just means the test
detected a change that you made and a new baseline should be created.

```bash
docker-compose run web pytest tests/render/
```

## Additional Reading

- [Pyramid](https://trypyramid.com/)
- [Pyramid Debugtoolbar](https://docs.pylonsproject.org/projects/pyramid_debugtoolbar/en/latest)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Selenium](http://www.seleniumhq.org/)
- [PyCharm](https://www.jetbrains.com/pycharm/documentation/)
- [Bok-Choy](http://bok-choy.readthedocs.io/en/latest)
- [Needle](https://needle.readthedocs.io/en/latest/)
- [Docker](https://docs.docker.com/)
- [npm](https://docs.npmjs.com/)
- [Sass](http://sass-lang.com/documentation/file.SASS_REFERENCE.html)
- [Gulp](https://github.com/gulpjs/gulp/blob/master/docs/API.md)
- [Flake8](http://flake8.pycqa.org/en/latest/)
