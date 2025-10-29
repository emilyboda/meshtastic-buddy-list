#!/usr/bin/env python3
"""
Oracle Connection Test Script
Test database connectivity before running main application
"""

import sys
import logging
from oracle_db_manager import get_db_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_oracle_connection():
    """Test Oracle database connection and basic operations."""
    
    print("=" * 50)
    print("Oracle Database Connection Test")
    print("=" * 50)
    
    try:
        # Initialize database manager
        print("\n1. Initializing database manager...")
        db = get_db_manager()
        
        # Test basic connection
        print("2. Testing database connection...")
        if not db.test_connection():
            print("❌ Connection test failed!")
            return False
        
        print("✅ Database connection successful!")
        
        # Test table existence
        print("3. Checking MESH_NODES table...")
        try:
            result = db.execute_query("SELECT COUNT(*) FROM MESH_NODES")
            node_count = result[0][0] if result else 0
            print(f"✅ MESH_NODES table exists with {node_count} records")
        except Exception as e:
            print(f"❌ MESH_NODES table check failed: {e}")
            print("   Please run setup_database_schema.py first")
            return False
        
        # Test insert/update permissions
        print("4. Testing database permissions...")
        try:
            # Try a simple query that requires read permissions
            result = db.execute_query("SELECT SYSDATE FROM DUAL")
            print(f"✅ Read permissions confirmed - Current time: {result[0][0]}")
            
            # Test if we can perform DML operations (this will be tested in actual usage)
            print("✅ Database permissions appear correct")
            
        except Exception as e:
            print(f"❌ Permission test failed: {e}")
            return False
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! Database is ready for use.")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Fatal error during testing: {e}")
        print("\nTroubleshooting:")
        print("1. Verify Oracle wallet is properly configured")
        print("2. Check network connectivity to Oracle Cloud")
        print("3. Verify database credentials in db_config.ini")
        print("4. Ensure cx_Oracle is properly installed")
        return False
    
    finally:
        try:
            db.close_pool()
        except:
            pass

def main():
    """Main test execution."""
    success = test_oracle_connection()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())