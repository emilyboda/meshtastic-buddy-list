#!/bin/bash
# Install Oracle dependencies on Raspberry Pi

# Update system
sudo apt update

# Install required system packages
sudo apt install -y libaio1 unzip wget

# Download Oracle Instant Client for ARM64 (Raspberry Pi 4)
cd /tmp
wget https://download.oracle.com/otn_software/linux/instantclient/1923000/instantclient-basic-linux.arm64-19.23.0.0.0dbru.zip
wget https://download.oracle.com/otn_software/linux/instantclient/1923000/instantclient-sqlplus-linux.arm64-19.23.0.0.0dbru.zip

# Create Oracle directory
sudo mkdir -p /opt/oracle
cd /opt/oracle

# Extract Oracle Instant Client
sudo unzip /tmp/instantclient-basic-linux.arm64-19.23.0.0.0dbru.zip
sudo unzip /tmp/instantclient-sqlplus-linux.arm64-19.23.0.0.0dbru.zip

# Set up environment variables
echo 'export LD_LIBRARY_PATH=/opt/oracle/instantclient_19_23:$LD_LIBRARY_PATH' | sudo tee -a /etc/environment
echo 'export PATH=/opt/oracle/instantclient_19_23:$PATH' | sudo tee -a /etc/environment

# Install Python Oracle driver
pip3 install cx_Oracle

# Clean up
rm /tmp/instantclient-*.zip

echo "Oracle client installation complete!"
echo "Please reboot the system or run: source /etc/environment"