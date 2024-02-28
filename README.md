# ProjectAidan
Repository for Project Aidan parts washer system.

# Software Installation Guide for Project Aidan


  # Introduction

This guide provides step-by-step instructions for installing and setting up Project Aidan on a Raspberry Pi Zero using Raspberry Pi OS Lite. The project is designed to control a NEMA17 motor for mechanical operations, utilizing a user-friendly interface on a Raspberry Pi with an attached 3.5-inch touchscreen.

 # Prerequisites (Equipment needed)

    Raspberry Pi Zero W/WH (with internet connectivity)
    3.5-inch RPi LCD (A) touchscreen
    Micro SD card (8 GB or larger recommended)  
    External computer with SD card slot or adapter
    Power supply for Raspberry Pi
    Nema 17
    TMC2208 driver

 # Step 1: Download & Flash Raspberry Pi OS Lite with Wi-Fi Configuration

Download and Install Raspberry Pi Imager: Visit the official Raspberry Pi Imager download page 
and download the imager for your operating system. Install the imager following the 
provided instructions.

Flash Raspberry Pi OS Lite and Configure Wi-Fi:

Open Raspberry Pi Imager and click "CHOOSE OS".
Select "Raspberry Pi OS Lite (32-bit)" under "Raspberry Pi OS (other)".
Click "CHOOSE STORAGE" and select your micro SD card.
Before writing the image, click the gear icon to access advanced settings.
In the "Set hostname" field, you can optionally provide a custom hostname.
In the Wi-Fi network section, enter your network's SSID and password, and select your Wi-Fi country.
Enable SSH by checking the "Enable SSH" option and setting a password for the pi user.
Click "SAVE" to apply these settings, then click "WRITE" to flash the OS to the micro SD card.


 # Step 2: Install Project Aidan
 
Insert the flashed micro SD card into your Raspberry Pi and power it up.

Once the Raspberry Pi is connected to your network, you can access it via SSH. Use an SSH client from another computer on the same network:

For Windows, use PuTTY.
For macOS or Linux, use the terminal: ssh pi@raspberrypi.local (replace raspberrypi.local with the hostname you set if you changed it).
Download and run the installation script for Project Aidan:

bash
Copy code
wget https://raw.githubusercontent.com/AstechUK/ProjectAidan/main/install.sh
chmod +x install.sh
./install.sh
The script will automate the setup process, including installing necessary dependencies and configuring the system to launch Project Aidan on startup.

 # Step 3: Using Project Aidan

Once the installation completes and the Raspberry Pi reboots, Project Aidan will start automatically, displaying the user interface on the connected 3.5-inch touchscreen.
Troubleshooting
For any issues, ensure all connections are secure and verify the installation steps. Consult the Raspberry Pi troubleshooting guide for additional help.



