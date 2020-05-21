### Deployment

Our apps runs as a service on the ec2

Location of the service:

    /etc/systemd/system/multi-user.target.wants/infinitag.service

Start stop restart the service:

    sudo systemctl <start/stop/restart> infinitag

When you change the service file run:

    sudo systemctl daemon-reload

To debug the app output of the service:

    sudo journalctl -u infinitag
