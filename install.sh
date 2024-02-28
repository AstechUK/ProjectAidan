#!/bin/bash

# Update and Upgrade the Pi, just in case
sudo apt-get update
sudo apt-get upgrade -y

# Install necessary libraries
sudo apt-get install -y python3-pyqt5
sudo apt-get install -y git

# Clone your repository
cd /home/pi
git clone https://github.com/AstechUK/ProjectAidan.git

# Navigate to the project directory
cd ProjectAidan

# Set up GPIO pin for power button
# Assuming GPIO3 (Pin 5) for demonstration purposes; replace with your actual pin
echo "dtoverlay=gpio-shutdown,gpio_pin=3" | sudo tee -a /boot/config.txt

# Install the driver for the RPi 3.5" LCD
cd /home/pi
git clone https://github.com/waveshare/LCD-show.git
cd LCD-show/
chmod +x LCD35-show
sudo ./LCD35-show 90  # This also rotates the display; adjust rotation as needed

# Add your application to the startup
# Creating a systemd service for your app
cat > /home/pi/ProjectAidan/projectaidan.service <<EOF
[Unit]
Description=Project Aidan Application Service
After=multi-user.target

[Service]
Type=idle
User=pi
ExecStart=/usr/bin/python3 /home/pi/ProjectAidan/main.py

[Install]
WantedBy=multi-user.target
EOF

# Move the service file and enable the service
sudo mv /home/pi/ProjectAidan/projectaidan.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable projectaidan.service
sudo systemctl start projectaidan.service

# Reboot to apply all changes
echo "Installation complete, rebooting now..."
sudo reboot
