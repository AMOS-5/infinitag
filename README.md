
![Build](https://travis-ci.com/AMOS-5/infinitag.svg?branch=master)

# InfiniTag
The repository for the AMOS Team 5 Project for tagging
documents using the power of machine learning!


## Getting Started
### Front End
- Install Node & npm (https://nodejs.org/en/)
- Install angular-cli  `npm install -g @angular/cli`
- Do `npm install` in `./frontend`
### Back End
- Install Python3
- pip install -r requirements.txt

## Running Software
### Front End
- `cd frontend`
- `npm ci`
- `ng serve`

### Rest Server
- `python app.py`

# Start Script
- Make sure the script can be executed
- `chmod +x start.h`
- You can either simply run `./start.sh` or you can use the following arguments:
    - `-h` prints usage
    - `-i` will install dependencies and start the software
    - `-p` will build the front end for production mode and start the rest server
