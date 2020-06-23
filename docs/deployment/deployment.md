# Deployment


## Backend
Our apps runs as a service on the ec2

Location of the service:

    /etc/systemd/system/multi-user.target.wants/infinitag.service

Start stop restart the service:

    sudo systemctl <start/stop/restart> infinitag

When you change the service file run:

    sudo systemctl daemon-reload

To debug the app output of the service:

    sudo journalctl -u infinitag

## Frontend

Build the master on your machine

    cd frontend
    npm run build:ci # builds frontend with --prod

Push the frontend to ec2

    export INFINITAG_PEM=~/.ssh/infinitag-org.pem
    export INFINITAG_FRONTEND_SRC=<INFINITAG_ROOT_YOUR_MACHINE>/frontend/dist/frontend/
    export INFINITAG_FRONTEND_DST=/home/ubuntu/infinitag/frontend/dist/frontend/
    export INFINITAG_EC2=ubuntu@ec2-3-84-34-102.compute-1.amazonaws.com

    rsync $INFINITAG_FRONTEND_SRC -e "ssh -i $INFINITAG_PEM" $INFINITAG_EC2:$INFINITAG_FRONTEND_DST -r --delete


