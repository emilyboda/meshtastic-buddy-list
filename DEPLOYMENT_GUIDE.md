# Oracle Database Migration Deployment Guide

## Prerequisites Setup on Raspberry Pi

### 1. Install Oracle Dependencies
```bash
chmod +x install_oracle_deps.sh
sudo ./install_oracle_deps.sh
sudo reboot
```

### 2. Download and Configure Oracle Wallet
1. Log into Oracle Cloud Console
2. Navigate to your Autonomous Database
3. Download the Instance Wallet
4. Transfer to Raspberry Pi:
```bash
# On your computer (replace with actual paths)
scp wallet.zip pi@your-pi-ip:/home/pi/

# On Raspberry Pi
cd /home/pi
sudo mkdir -p /home/pi/oracle_wallet
sudo unzip wallet.zip -d /home/pi/oracle_wallet
sudo chmod 600 /home/pi/oracle_wallet/*
sudo chown -R pi:pi /home/pi/oracle_wallet

# Edit sqlnet.ora
sudo nano /home/pi/oracle_wallet/sqlnet.ora
# Change DIRECTORY path to: /home/pi/oracle_wallet
```

### 3. Install Python Dependencies
```bash
pip3 install cx_Oracle configparser
```

## Database Setup

### 1. Create Database Schema
```bash
python3 setup_database_schema.py
```

### 2. Test Connection
```bash
python3 test_oracle_connection.py
```

## Migration Process

### 1. Backup Existing Data (Optional)
```bash
# Create backup of existing file-based data
cp /home/pi/buddylist-files/node-archive.txt /home/pi/buddylist-files/node-archive-backup-$(date +%Y%m%d).txt
```

### 2. Migrate Existing Data (Optional)
Create a one-time migration script if you want to preserve existing data:

```python
# migrate_existing_data.py
import json
from oracle_db_manager import get_db_manager
from datetime import datetime

def migrate_file_data():
    """Migrate existing file data to Oracle database."""
    db = get_db_manager()
    
    try:
        with open('/home/pi/buddylist-files/node-archive.txt', 'r') as f:
            node_list = json.load(f)
        
        for node_id, node_data in node_list.items():
            times_heard = node_data.get('Times Heard', [])
            first_heard = times_heard[0] if times_heard else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            last_heard = times_heard[-1] if times_heard else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            insert_query = """
                INSERT INTO MESH_NODES (
                    NODE_ID, SHORT_NAME, LONG_NAME, AKA, HARDWARE,
                    LATITUDE, LONGITUDE, ALTITUDE, HOPS_AWAY, CHANNEL,
                    FIRST_HEARD, LAST_HEARD, TIMES_HEARD, IS_ACTIVE
                ) VALUES (
                    :node_id, :short_name, :long_name, :aka, :hardware,
                    :latitude, :longitude, :altitude, :hops_away, :channel,
                    TO_TIMESTAMP(:first_heard, 'YYYY-MM-DD HH24:MI:SS'),
                    TO_TIMESTAMP(:last_heard, 'YYYY-MM-DD HH24:MI:SS'),
                    :times_heard, 1
                )
            """
            
            params = {
                'node_id': node_data['ID'],
                'short_name': node_data.get('Short Name', '')[:20],
                'long_name': node_data.get('Long Name', '')[:100],
                'aka': node_data.get('AKA', '')[:50],
                'hardware': node_data.get('Hardware', '')[:50],
                'latitude': float(node_data.get('Latitude', 0)) if node_data.get('Latitude') and node_data.get('Latitude') != "N/A" else None,
                'longitude': float(node_data.get('Longitude', 0)) if node_data.get('Longitude') and node_data.get('Longitude') != "N/A" else None,
                'altitude': float(node_data.get('Altitude', 0)) if node_data.get('Altitude') and node_data.get('Altitude') != "N/A" else None,
                'hops_away': int(node_data.get('Hops Away', 0)) if node_data.get('Hops Away') and node_data.get('Hops Away') != "N/A" else None,
                'channel': node_data.get('Channel', '')[:20],
                'first_heard': first_heard,
                'last_heard': last_heard,
                'times_heard': json.dumps(times_heard)
            }
            
            db.execute_dml(insert_query, params)
            print(f"Migrated: {node_data.get('Long Name', 'Unknown')}")
    
    except Exception as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    migrate_file_data()
```

### 3. Update Cron Job
Replace the existing cron job with the Oracle version:

```bash
# Edit crontab
crontab -e

# Replace old entry with:
*/5 * * * * cd /home/pi/buddylist && python3 update-node-list-oracle.py >> /home/pi/buddylist-files/cron.log 2>&1
```

### 4. Update Display Script (if needed)
The `update-buddy-list.py` script will need modification to read from Oracle instead of files. This can be done in a follow-up phase.

## Security Hardening

### 1. Secure Configuration Files
```bash
chmod 600 db_config.ini
```

### 2. Set Up Log Rotation
```bash
sudo nano /etc/logrotate.d/meshtastic-oracle

# Add this content:
/home/pi/buddylist-files/meshtastic_oracle.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 pi pi
}
```

### 3. Monitor Database Performance
Set up monitoring for:
- Connection pool usage
- Query performance
- Database space utilization
- Error rates

## Verification Steps

1. **Test new script manually:**
```bash
python3 update-node-list-oracle.py
```

2. **Check database contents:**
```sql
SELECT NODE_ID, LONG_NAME, LAST_HEARD, IS_ACTIVE 
FROM MESH_NODES 
ORDER BY LAST_HEARD DESC;
```

3. **Monitor logs:**
```bash
tail -f /home/pi/buddylist-files/meshtastic_oracle.log
```

4. **Verify cron execution:**
```bash
tail -f /home/pi/buddylist-files/cron.log
```

## Rollback Plan

If issues occur, you can quickly rollback:

1. **Restore original cron job:**
```bash
crontab -e
# Change back to: */5 * * * * cd /home/pi/buddylist && python3 update-node-list.py
```

2. **Restore file-based data:**
```bash
cp /home/pi/buddylist-files/node-archive-backup-*.txt /home/pi/buddylist-files/node-archive.txt
```

## Next Steps (Future Enhancements)

1. **Logging Infrastructure (Step 2):**
   - Oracle Application Performance Monitoring (APM)
   - Oracle Management Cloud integration
   - Custom alerting for node network issues

2. **Display Script Migration:**
   - Modify `update-buddy-list.py` to read from Oracle
   - Add caching layer for display performance
   - Real-time refresh capabilities

3. **Analytics and Reporting:**
   - Network topology analysis
   - Node availability trends
   - Geographic clustering insights