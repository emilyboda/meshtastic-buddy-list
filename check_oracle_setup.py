#!/usr/bin/env python3
"""
Quick Oracle Setup Verification
Verify prerequisites before running the single record test
"""

import os
import sys
import subprocess

def check_prerequisites():
    """Check if all prerequisites are met for Oracle testing."""
    
    print("=" * 50)
    print("Oracle Setup Prerequisites Check")
    print("=" * 50)
    
    checks_passed = 0
    total_checks = 5
    
    # Check 1: Python oracledb module
    print("\n1. Checking oracledb installation...")
    try:
        import oracledb
        print(f"   ✅ oracledb version: {oracledb.version}")
        checks_passed += 1
    except ImportError:
        print("   ❌ oracledb not installed")
        print("   Fix: pip install oracledb")
    
    # Check 2: Configuration file
    print("\n2. Checking database configuration...")
    if os.path.exists('db_config.ini'):
        print("   ✅ db_config.ini found")
        
        # Read and validate config
        try:
            import configparser
            config = configparser.ConfigParser()
            config.read('db_config.ini')
            
            required_keys = ['USERNAME', 'PASSWORD', 'HOST', 'PORT', 'SERVICE_NAME']
            missing_keys = []
            
            for key in required_keys:
                if not config.has_option('DATABASE', key):
                    missing_keys.append(key)
            
            if missing_keys:
                print(f"   ⚠️  Missing configuration keys: {missing_keys}")
            else:
                print("   ✅ Configuration appears complete")
                checks_passed += 1
                
        except Exception as e:
            print(f"   ❌ Error reading config: {e}")
    else:
        print("   ❌ db_config.ini not found")
        print("   Fix: Ensure db_config.ini exists with database credentials")
    
    # Check 3: Oracle wallet (optional but recommended)
    print("\n3. Checking Oracle wallet...")
    wallet_path = '/home/pi/oracle_wallet'
    if os.path.exists(wallet_path):
        wallet_files = os.listdir(wallet_path)
        if any(f.endswith('.ora') for f in wallet_files):
            print(f"   ✅ Oracle wallet found at {wallet_path}")
            checks_passed += 1
        else:
            print(f"   ⚠️  Wallet directory exists but no .ora files found")
    else:
        print(f"   ⚠️  Oracle wallet not found at {wallet_path}")
        print("   Note: Wallet is recommended for secure connections")
        print("   You may still be able to connect without it")
        checks_passed += 0.5  # Partial credit since it might still work
    
    # Check 4: Oracle client libraries
    print("\n4. Checking Oracle client libraries...")
    try:
        result = subprocess.run(['ldconfig', '-p'], capture_output=True, text=True)
        if 'libclntsh.so' in result.stdout:
            print("   ✅ Oracle client libraries found")
            checks_passed += 1
        else:
            print("   ❌ Oracle client libraries not found")
            print("   Fix: Run install_oracle_deps.sh")
    except:
        print("   ⚠️  Could not check Oracle client libraries")
        print("   This may still work depending on your setup")
    
    # Check 5: Network connectivity (basic check)
    print("\n5. Checking network connectivity...")
    try:
        import socket
        host = "g42be45e0f16617-uohbbhgq5avhicao.adb.us-ashburn-1.oraclecloudapps.com"
        port = 1521
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"   ✅ Can reach Oracle host {host}:1521")
            checks_passed += 1
        else:
            print(f"   ❌ Cannot reach Oracle host {host}:1521")
            print("   Check your internet connection and firewall settings")
            
    except Exception as e:
        print(f"   ⚠️  Network check failed: {e}")
    
    # Summary
    print("\n" + "=" * 50)
    print("Prerequisites Summary")
    print("=" * 50)
    
    percentage = (checks_passed / total_checks) * 100
    
    if checks_passed >= 4:
        print(f"🎉 Ready to test! ({checks_passed}/{total_checks} checks passed - {percentage:.0f}%)")
        print("\nNext steps:")
        print("1. python3 setup_database_schema.py")
        print("2. python3 test_single_record.py")
        return True
    elif checks_passed >= 2:
        print(f"⚠️  Partial setup ({checks_passed}/{total_checks} checks passed - {percentage:.0f}%)")
        print("You may still be able to test, but some issues should be resolved.")
        print("\nTry running: python3 test_single_record.py")
        return True
    else:
        print(f"❌ Setup incomplete ({checks_passed}/{total_checks} checks passed - {percentage:.0f}%)")
        print("Please resolve the issues above before testing.")
        return False

if __name__ == "__main__":
    success = check_prerequisites()
    sys.exit(0 if success else 1)