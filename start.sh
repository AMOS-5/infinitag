#!/bin/bash
shopt -s expand_aliases
install_flag='false'
production_flag='false'

python3_cmd=`which python3`
python_cmd=`which python`
node_cmd=`which node`
npm_cmd=`which npm`

BACKEND_PORT=5000
BACKEND_HOST="0.0.0.0"
FRONTEND_PORT=4200


if [ -z "$node_cmd" ]; then
    echo "Node not found. Cannot continue"
    exit 1
fi

if [ -z "$npm_cmd" ]; then
    echo "Npm not found. Cannot continue"
    exit 1
fi


if [ -n "$python3_cmd" ]; then
    alias p='python3'
    alias pp='pip3'
elif [ -z "$python3_cmd" ] && [ -n "$python_cmd" ]; then
    alias p='python'
    alias pp='pip'
else
    echo "No python found. Exiting."
    exit 1
fi

python_version=`p -c "import sys;print('{v[0]}'.format(v=list(sys.version_info[:1])))";`
if [ "$python_version" -lt 3 ]; then
    echo "This software requires at least python version 3 to run. Please upgrade as soon as possible"
    exit 1
fi


print_usage() {
  echo "Arguments: "
  echo "-i install all dependencies for front end and backend. Useful if they have not already been installed"
  echo "-p Start the REST server but only build the front end for production deployment. Useful if you are deploying to a server and don't need the interactive front end."
  echo "-h Get help"
}

cleanup() {
    printf "\nKilling python server...\n"
    curl http://$BACKEND_HOST:$BACKEND_PORT/stopServer
    printf "\nKilling angular instance...\n"
}

while getopts 'ihp' flag; do
  case "${flag}" in
    i) install_flag='true' ;;
    p) production_flag='true' ;;
    h) print_usage
        exit 1;;
    *) print_usage
       exit 1 ;;
  esac
done

echo "============== Starting InfiniTag =================="

trap cleanup EXIT

if [ "$install_flag" = "true" ]; then
    echo "Installing dependencies..."
    pp install -r requirements.txt
    cd frontend || exit
    npm ci
    cd ../
    echo "Dependencies installed. Continuing..."
fi

echo "Starting REST Server...."
p -u app.py --debug=False --host=$BACKEND_HOST --port=$BACKEND_PORT &

echo "Rest Server running at"
printf "http://$BACKEND_HOST:$BACKEND_PORT\n"

if [ "$production_flag" = "true" ]; then
    echo "Building Frontend for production deployment..."
    cd frontend || exit
    node node_modules/@angular/cli/bin/ng build --prod
    cd ../

    printf "Front end built and server is running...\n"
    read -p 'Press enter to kill the server.'
else
    echo "Serving Frontend at: "
    echo "http://localhost:$FRONTEND_PORT"
    cd frontend || exit
    node node_modules/@angular/cli/bin/ng serve --port=$FRONTEND_PORT -o
fi





