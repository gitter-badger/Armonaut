# Contributing to Armonaut

Thanks for considering contributing to Armonaut! Before contributing make sure you
are capable of and willing for your work being released under the
[Apache-2.0 license](https://github.com/SethMichaelLarson/Armonaut/blob/master/LICENSE)
such as if you're currently working for a client or corporation.

## Setting up your Tools and Workspace

This guide is written for Ubuntu 17.10 but the workflow will be similar compared to other Linux platforms.
Development is going to be tough on Windows systems because of Docker-Compose so I sadly can't recommend Windows
for anything beyond small changes. Sorry! (I use VirtualBox to virtualize Ubuntu 17.10 on my desktop)

**NOTE:** Ubuntu 17.10 packages Python 3.6 by default. Armonaut requires Python 3.6+.
If you're using a different platform you must install Python 3.6 along with virtualenv
and pip another way.  Google is your friend!

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
npm install --global gulp-cli
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

### Building all Docker images with Docker-Compose

Run the following command to pull all containers required for running
Armonaut locally in development mode.

**NOTE:** This command should take a *LONG* time to execute the first time.
Any time your run this command after this will be much faster due to caching of containers and their layers.
Every time you modify code should only take a few seconds to run the next time.

```bash
docker-compose up
# To stop hosting locally use Ctrl+C
```

Whenever you make modifications to the Armonaut codebase run the following commands to update the container:

```bash
docker-compose build
docker-compose up
```

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

**TODO**

### Using the Pyramid Debugtoolbar

See additional [documentation about the toolbar](https://docs.pylonsproject.org/projects/pyramid_debugtoolbar/en/latest/#usage) for more information.

### Running unit tests

**TODO**

### Running integration tests

**TODO**

## Additional Reading

- [Pyramid](https://trypyramid.com/)
- [Pyramid Debugtoolbar](https://docs.pylonsproject.org/projects/pyramid_debugtoolbar/en/latest)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Selenium](http://www.seleniumhq.org/)
- [Bok-Choy](http://bok-choy.readthedocs.io/en/latest)
- [Needle](https://needle.readthedocs.io/en/latest/)
- [Docker](https://docs.docker.com/)
- [npm](https://docs.npmjs.com/)
- [Sass](http://sass-lang.com/documentation/file.SASS_REFERENCE.html)
- [Gulp](https://github.com/gulpjs/gulp/blob/master/docs/API.md)
