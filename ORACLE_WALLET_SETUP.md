# Oracle Autonomous Database Wallet Setup Instructions

## Step 1: Download Wallet from Oracle Cloud Console

1. Log into Oracle Cloud Console
2. Navigate to your Autonomous Database instance
3. Click "DB Connection" 
4. Download the wallet file (Instance Wallet)
5. Save the zip file as `wallet.zip`

## Step 2: Extract and Configure Wallet on Raspberry Pi

```bash
# Create wallet directory
sudo mkdir -p /home/pi/oracle_wallet
cd /home/pi/oracle_wallet

# Copy and extract wallet (replace with your actual wallet file path)
sudo unzip /path/to/your/downloaded/wallet.zip

# Set proper permissions
sudo chmod 600 /home/pi/oracle_wallet/*
sudo chown -R pi:pi /home/pi/oracle_wallet

# Edit sqlnet.ora to use absolute path
sudo nano sqlnet.ora
```

## Step 3: Update sqlnet.ora file

Change the DIRECTORY parameter to use absolute path:
```
WALLET_LOCATION = (SOURCE = (METHOD = file) (METHOD_DATA = (DIRECTORY="/home/pi/oracle_wallet")))
SSL_SERVER_DN_MATCH=yes
```

## Step 4: Test Connection

```bash
# Test with sqlplus (if installed)
sqlplus DEVELOPMENT/"q$xc2NnvJco@G#"@uohbbhgq5avhicao_high

# Or test with Python script
python3 test_oracle_connection.py
```

## Alternative: Connection String Method (Less Secure)

If wallet setup fails, you can use direct connection string:
```python
# In oracle_db_manager.py, modify the DSN:
dsn = "(description= (retry_count=20)(retry_delay=3)(address=(protocol=tcps)(port=1521)(host=g42be45e0f16617-uohbbhgq5avhicao.adb.us-ashburn-1.oraclecloudapps.com))(connect_data=(service_name=g42be45e0f16617_uohbbhgq5avhicao_high.adb.oraclecloud.com))(security=(ssl_server_cert_dn=\"CN=adwc.uscom-east-1.oraclecloud.com, OU=Oracle BMCS US, O=Oracle Corporation, L=Redwood City, ST=California, C=US\")))"
```

## Security Notes:
- Never commit wallet files to version control
- Set restrictive file permissions (600)
- Consider using Oracle Cloud Infrastructure vault for production credentials