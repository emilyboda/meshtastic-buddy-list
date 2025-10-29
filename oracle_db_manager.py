"""
Oracle Database Connection Module for Meshtastic Node Management
Principal Engineer Implementation - Production Ready
"""

import oracledb
import configparser
import os
import logging
from contextlib import contextmanager
from typing import Optional, Dict, Any

class OracleDBManager:
    """
    Database manager with connection pooling,
    error handling, and transaction management.
    """
    
    def __init__(self, config_file: str = 'db_config.ini', wallet_location: str = None):
        """
        Initialize database manager with configuration.
        
        Args:
            config_file: Path to database configuration file
            wallet_location: Path to Oracle wallet directory (for Autonomous DB)
        """
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        self.wallet_location = wallet_location or '/home/pi/oracle_wallet'
        self.connection_pool = None
        self.logger = logging.getLogger(__name__)
        
        # Initialize connection pool
        self._create_connection_pool()
    
    def _create_connection_pool(self):
        """Create Oracle connection pool for efficient connection management."""
        try:
            # Use thin mode for cross-platform compatibility (no Oracle client needed)
            # For production on Raspberry Pi, you can switch to thick mode with Oracle client
            
            # Create connection string for Oracle Autonomous Database
            # Format: (description= (retry_count=20)(retry_delay=3)...)
            connection_string = f"""(description= (retry_count=20)(retry_delay=3)
                (address=(protocol=tcps)(port=1521)
                (host={self.config['DATABASE']['HOST']}))
                (connect_data=(service_name={self.config['DATABASE']['SERVICE_NAME']}))
                (security=(ssl_server_cert_dn=
                "CN=adwc.uscom-east-1.oraclecloud.com, OU=Oracle BMCS US, O=Oracle Corporation, L=Redwood City, ST=California, C=US")))"""
            
            self.connection_pool = oracledb.ConnectionPool(
                user=self.config['DATABASE']['USERNAME'],
                password=self.config['DATABASE']['PASSWORD'],
                dsn=connection_string,
                min=2,      # Minimum connections
                max=10,     # Maximum connections
                increment=1, # Connection increment
                encoding="UTF-8"
            )
            
            self.logger.info("Oracle connection pool created successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to create connection pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections with automatic cleanup.
        
        Yields:
            Oracle database connection
        """
        connection = None
        try:
            connection = self.connection_pool.acquire()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            self.logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if connection:
                self.connection_pool.release(connection)
    
    def test_connection(self) -> bool:
        """
        Test database connectivity.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1 FROM DUAL")
                result = cursor.fetchone()
                return result[0] == 1
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> list:
        """
        Execute SELECT query and return results.
        
        Args:
            query: SQL SELECT statement
            params: Query parameters
            
        Returns:
            List of query results
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or {})
            return cursor.fetchall()
    
    def execute_dml(self, query: str, params: Optional[Dict[str, Any]] = None) -> int:
        """
        Execute DML (INSERT, UPDATE, DELETE) statement.
        
        Args:
            query: SQL DML statement
            params: Query parameters
            
        Returns:
            Number of affected rows
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params or {})
            conn.commit()
            return cursor.rowcount
    
    def close_pool(self):
        """Close connection pool gracefully."""
        if self.connection_pool:
            self.connection_pool.close()
            self.logger.info("Connection pool closed")

# Global database manager instance
db_manager = None

def get_db_manager() -> OracleDBManager:
    """
    Get singleton database manager instance.
    
    Returns:
        OracleDBManager instance
    """
    global db_manager
    if db_manager is None:
        db_manager = OracleDBManager()
    return db_manager