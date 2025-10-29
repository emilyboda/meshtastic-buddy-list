#!/usr/bin/env python3
"""
Oracle Database Test - Insert Single Record
Test the database connection and insert functionality with sample data
"""

import json
import logging
from datetime import datetime
from oracle_db_manager import get_db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_single_record_insert():
    """Test inserting a single sample record to validate the database setup."""
    
    print("=" * 60)
    print("Oracle Database Single Record Test")
    print("=" * 60)
    
    try:
        # Initialize database manager
        print("\n1. Initializing database manager...")
        db = get_db_manager()
        
        # Test connection
        print("2. Testing database connection...")
        if not db.test_connection():
            print("❌ Database connection failed!")
            return False
        print("✅ Database connection successful!")
        
        # Sample test data (simulating a Meshtastic node)
        test_node_data = {
            'node_id': 'TEST001',
            'short_name': 'TestNode',
            'long_name': 'Test Node For Oracle',
            'aka': 'Meshtastic T001',
            'hardware': 'HELTEC_V3',
            'latitude': 40.7128,
            'longitude': -74.0060,
            'altitude': 10.5,
            'hops_away': 2,
            'channel': 'LongFast',
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        print(f"\n3. Inserting test record...")
        print(f"   Node ID: {test_node_data['node_id']}")
        print(f"   Name: {test_node_data['long_name']}")
        print(f"   Location: {test_node_data['latitude']}, {test_node_data['longitude']}")
        
        # Check if record already exists
        check_query = "SELECT COUNT(*) FROM MESH_NODES WHERE NODE_ID = :node_id"
        result = db.execute_query(check_query, {'node_id': test_node_data['node_id']})
        exists = result[0][0] > 0 if result else False
        
        if exists:
            print(f"   Record already exists - will update instead")
            
            # Update existing record
            update_query = """
                UPDATE MESH_NODES 
                SET SHORT_NAME = :short_name,
                    LONG_NAME = :long_name,
                    LAST_HEARD = TO_TIMESTAMP(:last_heard, 'YYYY-MM-DD HH24:MI:SS'),
                    TIMES_HEARD = :times_heard,
                    IS_ACTIVE = 1
                WHERE NODE_ID = :node_id
            """
            
            # Get existing times_heard and add new timestamp
            get_times_query = "SELECT TIMES_HEARD FROM MESH_NODES WHERE NODE_ID = :node_id"
            times_result = db.execute_query(get_times_query, {'node_id': test_node_data['node_id']})
            existing_times = json.loads(times_result[0][0]) if times_result and times_result[0][0] else []
            existing_times.append(test_node_data['timestamp'])
            
            update_params = {
                'node_id': test_node_data['node_id'],
                'short_name': test_node_data['short_name'],
                'long_name': test_node_data['long_name'],
                'last_heard': test_node_data['timestamp'],
                'times_heard': json.dumps(existing_times)
            }
            
            rows_affected = db.execute_dml(update_query, update_params)
            
        else:
            # Insert new record
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
            
            insert_params = {
                'node_id': test_node_data['node_id'],
                'short_name': test_node_data['short_name'],
                'long_name': test_node_data['long_name'],
                'aka': test_node_data['aka'],
                'hardware': test_node_data['hardware'],
                'latitude': test_node_data['latitude'],
                'longitude': test_node_data['longitude'],
                'altitude': test_node_data['altitude'],
                'hops_away': test_node_data['hops_away'],
                'channel': test_node_data['channel'],
                'first_heard': test_node_data['timestamp'],
                'last_heard': test_node_data['timestamp'],
                'times_heard': json.dumps([test_node_data['timestamp']])
            }
            
            rows_affected = db.execute_dml(insert_query, insert_params)
        
        if rows_affected > 0:
            action = "updated" if exists else "inserted"
            print(f"✅ Record {action} successfully! ({rows_affected} row affected)")
        else:
            print("❌ No rows were affected - operation may have failed")
            return False
        
        # Verify the record was inserted/updated
        print("\n4. Verifying record in database...")
        verify_query = """
            SELECT NODE_ID, SHORT_NAME, LONG_NAME, AKA, HARDWARE,
                   LATITUDE, LONGITUDE, ALTITUDE, HOPS_AWAY, CHANNEL,
                   TO_CHAR(FIRST_HEARD, 'YYYY-MM-DD HH24:MI:SS') as FIRST_HEARD,
                   TO_CHAR(LAST_HEARD, 'YYYY-MM-DD HH24:MI:SS') as LAST_HEARD,
                   TO_CHAR(CREATED_DATE, 'YYYY-MM-DD HH24:MI:SS') as CREATED_DATE,
                   TO_CHAR(UPDATED_DATE, 'YYYY-MM-DD HH24:MI:SS') as UPDATED_DATE,
                   IS_ACTIVE, TIMES_HEARD
            FROM MESH_NODES 
            WHERE NODE_ID = :node_id
        """
        
        verify_result = db.execute_query(verify_query, {'node_id': test_node_data['node_id']})
        
        if verify_result:
            row = verify_result[0]
            print(f"   ✅ Record found in database:")
            print(f"      Node ID: {row[0]}")
            print(f"      Short Name: {row[1]}")
            print(f"      Long Name: {row[2]}")
            print(f"      AKA: {row[3]}")
            print(f"      Hardware: {row[4]}")
            print(f"      Location: {row[5]}, {row[6]} (Alt: {row[7]})")
            print(f"      Network: {row[8]} hops, Channel: {row[9]}")
            print(f"      First Heard: {row[10]}")
            print(f"      Last Heard: {row[11]}")
            print(f"      Created: {row[12]}")
            print(f"      Updated: {row[13]}")
            print(f"      Active: {'Yes' if row[14] == 1 else 'No'}")
            
            # Parse and display times heard
            times_heard = json.loads(row[15]) if row[15] else []
            print(f"      Times Heard Count: {len(times_heard)}")
            if times_heard:
                print(f"      Latest: {times_heard[-1]}")
                if len(times_heard) > 1:
                    print(f"      Earliest: {times_heard[0]}")
        else:
            print("❌ Record not found after insert - verification failed")
            return False
        
        # Test querying all records
        print("\n5. Checking total records in database...")
        count_query = "SELECT COUNT(*) FROM MESH_NODES"
        count_result = db.execute_query(count_query)
        total_records = count_result[0][0] if count_result else 0
        print(f"   Total records in MESH_NODES: {total_records}")
        
        # Test querying active records
        active_query = "SELECT COUNT(*) FROM MESH_NODES WHERE IS_ACTIVE = 1"
        active_result = db.execute_query(active_query)
        active_records = active_result[0][0] if active_result else 0
        print(f"   Active records: {active_records}")
        
        print("\n" + "=" * 60)
        print("🎉 Single record test completed successfully!")
        print("   Database is ready for production use.")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        print(f"\nError details: {str(e)}")
        
        # Provide troubleshooting guidance
        print("\nTroubleshooting steps:")
        print("1. Verify Oracle wallet configuration")
        print("2. Check database credentials in db_config.ini")
        print("3. Ensure MESH_NODES table exists (run setup_database_schema.py)")
        print("4. Verify network connectivity to Oracle Cloud")
        print("5. Check Oracle client installation")
        
        return False
    
    finally:
        try:
            db.close_pool()
        except:
            pass

def clean_test_data():
    """Optional: Remove test data after testing."""
    try:
        db = get_db_manager()
        delete_query = "DELETE FROM MESH_NODES WHERE NODE_ID = 'TEST001'"
        rows_deleted = db.execute_dml(delete_query)
        if rows_deleted > 0:
            print(f"✅ Test record cleaned up ({rows_deleted} row deleted)")
        else:
            print("ℹ️  No test record found to clean up")
    except Exception as e:
        print(f"❌ Error cleaning up test data: {e}")
    finally:
        try:
            db.close_pool()
        except:
            pass

def main():
    """Main test execution."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--cleanup":
        clean_test_data()
        return 0
    
    success = test_single_record_insert()
    
    if success:
        print(f"\n💡 To clean up test data later, run:")
        print(f"   python3 {sys.argv[0]} --cleanup")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())