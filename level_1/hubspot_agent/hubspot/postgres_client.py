import psycopg2
from psycopg2 import pool


class PostgresClient:
    """Class to handle PostgreSQL database operations"""

    def __init__(self, db_name, db_user, db_password, db_host, db_port, min_conn=1, max_conn=10):
        self.conn_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=min_conn,
            maxconn=max_conn,
            database=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        self._init_db()

    def _init_db(self):
        """Initialize database tables if they don't exist"""
        conn = self.conn_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS hubspot_leads (
                        id SERIAL PRIMARY KEY,
                        hubspot_id VARCHAR(255) NOT NULL UNIQUE,
                        email VARCHAR(255) NOT NULL,
                        firstname VARCHAR(255),
                        lastname VARCHAR(255),
                        phone VARCHAR(255),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS hubspot_meetings (
                        id SERIAL PRIMARY KEY,
                        hubspot_id VARCHAR(255) NOT NULL UNIQUE,
                        lead_id VARCHAR(255) NOT NULL,
                        title VARCHAR(255),
                        start_time TIMESTAMP WITH TIME ZONE,
                        end_time TIMESTAMP WITH TIME ZONE,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        FOREIGN KEY (lead_id) REFERENCES hubspot_leads(hubspot_id)
                    )
                """)
                conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"Database initialization error: {e}")
        finally:
            self.conn_pool.putconn(conn)

    def store_lead(self, hubspot_id, lead_data):
        """Store a new lead in the database"""
        conn = self.conn_pool.getconn()
        email = lead_data['properties']['email']
        firstname = lead_data['properties'].get('firstname') # Use .get for optional fields
        lastname = lead_data['properties'].get('lastname')
        phone = lead_data['properties'].get('phone')
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO hubspot_leads (hubspot_id, email, firstname, lastname, phone)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (hubspot_id, email, phone, firstname, lastname)
                )
                result = cursor.fetchone()
                conn.commit()
                return result[0] if result else None
        except Exception as e:
            conn.rollback()
            print(f"Error storing lead: {e}")
            return None
        finally:
            self.conn_pool.putconn(conn)

    def store_meeting(self, hubspot_id, lead_id, title, start_time, end_time):
        """Store a new meeting in the database"""
        conn = self.conn_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO hubspot_meetings (hubspot_id, lead_id, title, start_time, end_time)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (hubspot_id, lead_id, title, start_time, end_time)
                )
                result = cursor.fetchone()
                conn.commit()
                return result[0] if result else None
        except Exception as e:
            conn.rollback()
            print(f"Error storing meeting: {e}")
            return None
        finally:
            self.conn_pool.putconn(conn)

    def find_lead_by_email(self, email_id):
        """Retrieve a lead by email ID"""
        conn = self.conn_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM hubspot_leads WHERE email = %s
                    """,
                    (email_id,)
                )
                result = cursor.fetchone()
                return result
        finally:
            self.conn_pool.putconn(conn)


    def get_lead_by_hubspot_id(self, hubspot_id):
        """Retrieve a lead by HubSpot ID"""
        conn = self.conn_pool.getconn()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT * FROM hubspot_leads WHERE hubspot_id = %s
                    """,
                    (hubspot_id,)
                )
                result = cursor.fetchone()
                return result
        finally:
            self.conn_pool.putconn(conn)

    def close(self):
        """Close the connection pool"""
        if self.conn_pool:
            self.conn_pool.closeall()