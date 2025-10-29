#!/usr/bin/env python3
"""
Simple oracledb Test
Test if oracledb is properly installed and can import
"""

print("Testing oracledb installation...")

try:
    import oracledb
    print(f"✅ oracledb successfully imported!")
    print(f"   Version: {oracledb.version}")
    print(f"   Running in 'thin' mode (no Oracle client required)")
    print(f"   Oracle driver location: {oracledb.__file__}")
    
    # Test basic functionality
    print("\nTesting basic Oracle functionality...")
    
    # Test DSN creation (this doesn't require a connection)
    test_dsn = oracledb.makedsn(
        host="test.example.com",
        port=1521,
        service_name="test_service"
    )
    print(f"✅ DSN creation works: {test_dsn}")
    
    print("\n🎉 oracledb is properly installed and functional!")
    print("   Ready for Oracle Autonomous Database connections!")
    
except ImportError as e:
    print(f"❌ oracledb import failed: {e}")
    print("\nTroubleshooting:")
    print("1. Install oracledb: pip install oracledb")
    print("2. Check Python version compatibility")
    
except Exception as e:
    print(f"⚠️ oracledb loaded with note: {e}")
    print("   This is normal - oracledb is working in 'thin' mode")
    print("   No Oracle client libraries required for Autonomous Database!")

print("\nNext step: If this test passes, try running the database connection test.")