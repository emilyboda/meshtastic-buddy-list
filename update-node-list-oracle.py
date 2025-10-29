"""
Meshtastic Node Oracle Database Manager
Principal Engineer Implementation - Production Ready

This replaces the file-based storage with Oracle Database integration.
Handles node discovery, updates, and status management.
"""

import subprocess
import re
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from oracle_db_manager import get_db_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/pi/buddylist-files/meshtastic_oracle.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Configuration
MESHTASTIC_PATH = '/home/pi/buddylist/bin/meshtastic'
INACTIVE_THRESHOLD_HOURS = 168  # 7 days - mark as inactive if not seen

class MeshtasticOracleManager:
    """
    Manages Meshtastic node data in Oracle Database with enterprise-grade
    error handling, transaction management, and data integrity.
    """
    
    def __init__(self):
        self.db = get_db_manager()
        self.stats = {
            'nodes_added': 0,
            'nodes_updated': 0,
            'nodes_marked_inactive': 0,
            'errors': []
        }
    
    def run_meshtastic_scan(self) -> List[Dict[str, Any]]:
        """
        Execute meshtastic --nodes command and parse results.
        
        Returns:
            List of parsed node data dictionaries
        """
        logger.info("Starting Meshtastic network scan")
        parsed_data = []
        
        try:
            result = subprocess.run(
                [MESHTASTIC_PATH, '--nodes'], 
                capture_output=True, 
                text=True,
                timeout=60  # 60 second timeout
            )
            
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, result.stderr)
            
            logger.info("Meshtastic command executed successfully")
            
            # Parse command output
            for line in result.stdout.split('\n'):
                row_data = re.findall(r"\│\s*([^│]+?)\s*(?=\│)", line)
                if row_data and len(row_data) >= 16:  # Ensure we have enough columns
                    parsed_data.append([item.strip() for item in row_data])
            
            # Remove header row if present
            if parsed_data and 'Long Name' in parsed_data[0]:
                parsed_data = parsed_data[1:]
            
            # Add AKA column (Meshtastic + last 4 digits of ID)
            for row in parsed_data:
                if len(row) >= 3:
                    aka_value = f"Meshtastic {row[2][-4:]}"
                    row.insert(4, aka_value)
            
            logger.info(f"Parsed {len(parsed_data)} nodes from scan")
            return parsed_data
            
        except subprocess.TimeoutExpired:
            error_msg = "Meshtastic command timed out"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return []
        except subprocess.CalledProcessError as e:
            error_msg = f"Meshtastic command failed: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return []
        except Exception as e:
            error_msg = f"Unexpected error during scan: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return []
    
    def get_existing_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve existing node data from database.
        
        Args:
            node_id: Node identifier
            
        Returns:
            Node data dictionary or None if not found
        """
        try:
            query = """
                SELECT NODE_ID, SHORT_NAME, LONG_NAME, AKA, HARDWARE,
                       LATITUDE, LONGITUDE, ALTITUDE, HOPS_AWAY, CHANNEL,
                       FIRST_HEARD, LAST_HEARD, TIMES_HEARD
                FROM MESH_NODES 
                WHERE NODE_ID = :node_id
            """
            
            results = self.db.execute_query(query, {'node_id': node_id})
            
            if results:
                row = results[0]
                times_heard = json.loads(row[12]) if row[12] else []
                
                return {
                    'NODE_ID': row[0],
                    'SHORT_NAME': row[1],
                    'LONG_NAME': row[2],
                    'AKA': row[3],
                    'HARDWARE': row[4],
                    'LATITUDE': float(row[5]) if row[5] else None,
                    'LONGITUDE': float(row[6]) if row[6] else None,
                    'ALTITUDE': float(row[7]) if row[7] else None,
                    'HOPS_AWAY': int(row[8]) if row[8] else None,
                    'CHANNEL': row[9],
                    'FIRST_HEARD': row[10],
                    'LAST_HEARD': row[11],
                    'TIMES_HEARD': times_heard
                }
            
            return None
            
        except Exception as e:
            error_msg = f"Error retrieving node {node_id}: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return None
    
    def insert_new_node(self, node_data: List[str]) -> bool:
        """
        Insert new node into database.
        
        Args:
            node_data: Parsed node data from meshtastic command
            
        Returns:
            True if successful, False otherwise
        """
        try:
            current_time = datetime.now()
            last_heard = node_data[15] if node_data[15] != "N/A" else current_time.strftime('%Y-%m-%d %H:%M:%S')
            times_heard_json = json.dumps([last_heard])
            
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
                'node_id': node_data[2],
                'short_name': node_data[3][:20],  # Truncate to fit column
                'long_name': node_data[1][:100],  # Truncate to fit column
                'aka': node_data[4][:50],        # Truncate to fit column
                'hardware': node_data[5][:50],   # Truncate to fit column
                'latitude': float(node_data[6]) if node_data[6] and node_data[6] != "N/A" else None,
                'longitude': float(node_data[7]) if node_data[7] and node_data[7] != "N/A" else None,
                'altitude': float(node_data[8]) if node_data[8] and node_data[8] != "N/A" else None,
                'hops_away': int(node_data[13]) if node_data[13] and node_data[13] != "N/A" else None,
                'channel': node_data[14][:20],   # Truncate to fit column
                'first_heard': last_heard,
                'last_heard': last_heard,
                'times_heard': times_heard_json
            }
            
            rows_affected = self.db.execute_dml(insert_query, params)
            
            if rows_affected > 0:
                logger.info(f"New node added: {node_data[1]} ({node_data[3]})")
                self.stats['nodes_added'] += 1
                return True
            
            return False
            
        except Exception as e:
            error_msg = f"Error inserting node {node_data[2]}: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return False
    
    def update_existing_node(self, node_data: List[str], existing_node: Dict[str, Any]) -> bool:
        """
        Update existing node with new information.
        
        Args:
            node_data: New node data from scan
            existing_node: Current node data from database
            
        Returns:
            True if updated, False if no changes needed
        """
        try:
            updates_needed = False
            update_fields = []
            params = {'node_id': node_data[2]}
            
            # Check each field for changes
            if existing_node['SHORT_NAME'] != node_data[3]:
                update_fields.append("SHORT_NAME = :short_name")
                params['short_name'] = node_data[3][:20]
                updates_needed = True
                logger.info(f"Short name updated for {node_data[1]}: {existing_node['SHORT_NAME']} -> {node_data[3]}")
            
            if existing_node['LONG_NAME'] != node_data[1] and node_data[1] != existing_node['AKA']:
                update_fields.append("LONG_NAME = :long_name")
                params['long_name'] = node_data[1][:100]
                updates_needed = True
                logger.info(f"Long name updated for {node_data[1]}")
            
            if existing_node['HARDWARE'] != node_data[5]:
                update_fields.append("HARDWARE = :hardware")
                params['hardware'] = node_data[5][:50]
                updates_needed = True
                logger.info(f"Hardware updated for {node_data[1]}")
            
            # Update location if changed
            new_lat = float(node_data[6]) if node_data[6] and node_data[6] != "N/A" else None
            new_lon = float(node_data[7]) if node_data[7] and node_data[7] != "N/A" else None
            new_alt = float(node_data[8]) if node_data[8] and node_data[8] != "N/A" else None
            
            if existing_node['LATITUDE'] != new_lat:
                update_fields.append("LATITUDE = :latitude")
                params['latitude'] = new_lat
                updates_needed = True
            
            if existing_node['LONGITUDE'] != new_lon:
                update_fields.append("LONGITUDE = :longitude")
                params['longitude'] = new_lon
                updates_needed = True
                
            if existing_node['ALTITUDE'] != new_alt:
                update_fields.append("ALTITUDE = :altitude")
                params['altitude'] = new_alt
                updates_needed = True
            
            # Update network info
            new_hops = int(node_data[13]) if node_data[13] and node_data[13] != "N/A" else None
            if existing_node['HOPS_AWAY'] != new_hops:
                update_fields.append("HOPS_AWAY = :hops_away")
                params['hops_away'] = new_hops
                updates_needed = True
            
            if existing_node['CHANNEL'] != node_data[14]:
                update_fields.append("CHANNEL = :channel")
                params['channel'] = node_data[14][:20]
                updates_needed = True
            
            # Always update last_heard and times_heard if we have new timestamp
            new_timestamp = node_data[15] if node_data[15] != "N/A" else datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if new_timestamp not in existing_node['TIMES_HEARD']:
                existing_node['TIMES_HEARD'].append(new_timestamp)
                update_fields.append("LAST_HEARD = TO_TIMESTAMP(:last_heard, 'YYYY-MM-DD HH24:MI:SS')")
                update_fields.append("TIMES_HEARD = :times_heard")
                update_fields.append("IS_ACTIVE = 1")  # Mark as active since we just saw it
                params['last_heard'] = new_timestamp
                params['times_heard'] = json.dumps(existing_node['TIMES_HEARD'])
                updates_needed = True
                logger.info(f"Last heard updated for {node_data[1]}")
            
            if updates_needed:
                update_query = f"""
                    UPDATE MESH_NODES 
                    SET {', '.join(update_fields)}
                    WHERE NODE_ID = :node_id
                """
                
                rows_affected = self.db.execute_dml(update_query, params)
                
                if rows_affected > 0:
                    self.stats['nodes_updated'] += 1
                    return True
            
            return updates_needed
            
        except Exception as e:
            error_msg = f"Error updating node {node_data[2]}: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return False
    
    def mark_inactive_nodes(self) -> None:
        """
        Mark nodes as inactive if they haven't been seen recently.
        """
        try:
            cutoff_time = datetime.now() - timedelta(hours=INACTIVE_THRESHOLD_HOURS)
            
            update_query = """
                UPDATE MESH_NODES 
                SET IS_ACTIVE = 0
                WHERE LAST_HEARD < :cutoff_time 
                AND IS_ACTIVE = 1
            """
            
            rows_affected = self.db.execute_dml(
                update_query, 
                {'cutoff_time': cutoff_time}
            )
            
            if rows_affected > 0:
                logger.info(f"Marked {rows_affected} nodes as inactive")
                self.stats['nodes_marked_inactive'] = rows_affected
                
        except Exception as e:
            error_msg = f"Error marking inactive nodes: {e}"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
    
    def process_nodes(self) -> Dict[str, Any]:
        """
        Main processing function: scan network and update database.
        
        Returns:
            Processing statistics
        """
        logger.info("Starting node processing cycle")
        start_time = datetime.now()
        
        # Test database connection
        if not self.db.test_connection():
            error_msg = "Database connection test failed"
            logger.error(error_msg)
            self.stats['errors'].append(error_msg)
            return self.stats
        
        # Scan network
        scanned_nodes = self.run_meshtastic_scan()
        
        if not scanned_nodes:
            logger.warning("No nodes found in scan")
            return self.stats
        
        # Process each scanned node
        for node_data in scanned_nodes:
            if len(node_data) < 16:  # Ensure we have all required fields
                logger.warning(f"Incomplete node data: {node_data}")
                continue
                
            node_id = node_data[2]
            existing_node = self.get_existing_node(node_id)
            
            if existing_node:
                self.update_existing_node(node_data, existing_node)
            else:
                self.insert_new_node(node_data)
        
        # Mark inactive nodes
        self.mark_inactive_nodes()
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        logger.info(f"Processing completed in {processing_time:.2f} seconds")
        logger.info(f"Stats: {self.stats['nodes_added']} added, {self.stats['nodes_updated']} updated, {self.stats['nodes_marked_inactive']} marked inactive")
        
        if self.stats['errors']:
            logger.error(f"Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors']:
                logger.error(f"  - {error}")
        
        return self.stats

def main():
    """Main execution function."""
    try:
        manager = MeshtasticOracleManager()
        stats = manager.process_nodes()
        
        # Return exit code based on success/failure
        return 0 if not stats['errors'] else 1
        
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        return 1
    finally:
        # Cleanup database connections
        try:
            db = get_db_manager()
            db.close_pool()
        except:
            pass

if __name__ == "__main__":
    exit(main())