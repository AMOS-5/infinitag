
![Build](https://travis-ci.com/AMOS-5/infinitag.svg?branch=master)

# Table of Contents
1. [InfiniTag](#infinitag)
2. [User Documentation](#user-documentation)
3. [Architecture](#architecture)
4. [Getting Started](#getting-started)
    1. [Front End](#frontend)
    2. [Back End](#backend)
5. [Running Software](#running-software)
    1. [Front End](#running-software-frontend)
    2. [REST Server](#running-backend)
6. [Start Script](#start-script)
    1. [Linux / Mac](#start-script-linux)
    2. [Windows](#start-script-windows)

<a name="infinitag"></a>
# InfiniTag
The repository for the AMOS Team 5 Project for tagging
documents using the power of machine learning!

<a name="user-documentation"></a>
# User Documentation
Please find the PDF for the user documentation in `docs/user/user_manual.pdf`

<a name="architecture"></a>
# Architecture
Please find the PDF for the architecture of the project in `docs/architecture/Software-Architecture-Description-AMOS.pdf`

<a name="getting-started"></a>
## Getting Started

<a name="frontend"></a>
### Front End
- Install Node & npm (https://nodejs.org/en/)
- Install angular-cli  `npm install -g @angular/cli`
- Do `npm install` in `./frontend`

<a name="backend"></a>
### Back End
- Install Python3
- pip install -r requirements.txt

<a name="running-software"></a>
## Running Software

<a name="running-software-frontend"></a>
### Front End
#### Prerequisites:
Make sure the correct server URL is set in `frontend/src/environments/environment.ts` or `environment.prod.ts`
if you are going to build the front end with the `--prod` flag. If you are
running the flask server on localhost with the default port (5000) this
should not be an issue. Otherwise you will not be able to connect
to the server.

### Commands

- `cd frontend`
- `npm ci`
- `ng serve`

<a name="running-backend"></a>
### Rest Server
- `python app.py`

<a name="start-script"></a>
# Start Script
This script is meant to make it quicker to get up and running. It is
however necessary to have the following installed:
- python3
- pip
- npm
- node

On `Windows` the following commands must be available in the command line:
- `py`
- `npm`
- `node`

On `Linux / Mac` the following commands must be available in the shell
- `python3` or `python`
- `pip` or `pip3`
- `node`
- `npm`

The default operation of this script is:
- Start flask server in the background with host `http://0.0.0.0:5000`
- Start angular application at `http://localhost:4200`

<a name="start-script-linux"></a>
## Linux / Mac
- Make sure the script can be executed
- `chmod +x start.h`
- Because our software requires `python 3.7`, you may have to export your
desired python version as an environment variable. For example:
    - `export python=/home/user/anaconda3/bin/python`

this will then cause the script to use this version instead of the default
version in the path.
- You can either simply run `./start.sh` or you can use the following arguments:
    - `-h` prints usage
    - `-i` will install dependencies and start the software
    - `-p` will build the front end for production mode and start the rest server

<a name="start-script-windows"></a>
## Windows
- You can either simply run `start.bat`, either by executing it in the command line or by clicking on it,
or you can use the following arguments:
    - `/h` prints usage
    - `/i` will install dependencies and start the software
    - `/p` will build the front end for production mode and start the rest server
