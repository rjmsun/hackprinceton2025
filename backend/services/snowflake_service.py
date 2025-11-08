import snowflake.connector
from typing import Optional, Dict, List, Any
import os
import json
from datetime import datetime

class SnowflakeService:
    def __init__(
        self,
        account: Optional[str] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        authenticator: Optional[str] = None,
        role: Optional[str] = None,
        database: Optional[str] = None,
        schema: Optional[str] = None,
        warehouse: Optional[str] = None
    ):
        self.account = account or os.getenv("SNOWFLAKE_ACCOUNT")
        self.user = user or os.getenv("SNOWFLAKE_USER")
        self.password = password or os.getenv("SNOWFLAKE_PASSWORD")
        self.authenticator = authenticator or os.getenv("SNOWFLAKE_AUTHENTICATOR", "password")
        self.role = role or os.getenv("SNOWFLAKE_ROLE", "ACCOUNTADMIN")
        self.database = database or os.getenv("SNOWFLAKE_DATABASE")
        self.schema = schema or os.getenv("SNOWFLAKE_SCHEMA")
        self.warehouse = warehouse or os.getenv("SNOWFLAKE_WAREHOUSE")
        self.conn = None
    
    def _get_connection(self):
        """Get or create Snowflake connection"""
        if not all([self.account, self.user]):
            return None
        
        try:
            # Account format: remove https:// and .snowflakecomputing.com if present
            account_clean = self.account.replace('https://', '').replace('.snowflakecomputing.com', '')
            
            # Build connection parameters
            conn_params = {
                "account": account_clean,
                "user": self.user,
                "role": self.role
            }
            
            # Handle authentication
            if self.authenticator == "password" or not self.authenticator or self.authenticator == "externalbrowser":
                # Default to password authentication (don't specify authenticator)
                if self.password:
                    conn_params["password"] = self.password
            else:
                # For other authenticators (SSO, etc.)
                conn_params["authenticator"] = self.authenticator
            
            # Add optional parameters if provided
            if self.database and self.database != "<none selected>":
                conn_params["database"] = self.database
            if self.schema and self.schema != "<none selected>":
                conn_params["schema"] = self.schema
            if self.warehouse and self.warehouse != "<none selected>":
                conn_params["warehouse"] = self.warehouse
            
            conn = snowflake.connector.connect(**conn_params)
            return conn
        except Exception as e:
            raise Exception(f"Snowflake connection failed: {str(e)}")
    
    def store_transcript(self, user_id: str, transcript: str, summary: Dict, tasks: List[Dict]) -> bool:
        """Store transcript and extracted data in Snowflake"""
        conn = self._get_connection()
        if not conn:
            return False
        
        try:
            cursor = conn.cursor()
            
            # Create table if it doesn't exist
            cursor.execute(f"""
                CREATE TABLE IF NOT EXISTS {self.database}.{self.schema}.conversations (
                    id VARCHAR(36) DEFAULT UUID_STRING(),
                    user_id VARCHAR(255),
                    transcript TEXT,
                    summary TEXT,
                    tasks TEXT,
                    created_at TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                    PRIMARY KEY (id)
                )
            """)
            
            # Insert data
            cursor.execute(f"""
                INSERT INTO {self.database}.{self.schema}.conversations 
                (user_id, transcript, summary, tasks)
                VALUES (%s, %s, %s, %s)
            """, (
                user_id,
                transcript,
                json.dumps(summary),
                json.dumps(tasks)
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except Exception as e:
            raise Exception(f"Failed to store transcript: {str(e)}")
    
    def get_user_conversations(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Retrieve user's conversation history"""
        conn = self._get_connection()
        if not conn:
            return []
        
        try:
            cursor = conn.cursor()
            
            cursor.execute(f"""
                SELECT id, transcript, summary, tasks, created_at
                FROM {self.database}.{self.schema}.conversations
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (user_id, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": row[0],
                    "transcript": row[1],
                    "summary": json.loads(row[2]) if row[2] else {},
                    "tasks": json.loads(row[3]) if row[3] else [],
                    "created_at": row[4].isoformat() if row[4] else None
                })
            
            cursor.close()
            conn.close()
            return results
        except Exception as e:
            raise Exception(f"Failed to retrieve conversations: {str(e)}")
    
    def test_connection(self) -> bool:
        """Test Snowflake connection"""
        try:
            conn = self._get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT CURRENT_VERSION()")
                version = cursor.fetchone()
                cursor.close()
                conn.close()
                return True
            return False
        except Exception as e:
            return False

