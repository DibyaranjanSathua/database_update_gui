"""
File:           dbhandler.py
Author:         Dibyaranjan Sathua
Created on:     03/12/21, 8:45 pm
"""
import json
from pathlib import Path
import psycopg2
import psycopg2.extras
import snowflake.connector
import pandas as pd


class DBHandler:
    """ Connect to DB and execute the SQL """

    def __init__(self, config):
        self.db_conn = None
        db_config = config.get("DB_Config", {})
        self.db_host = db_config.get("host", "")
        self.db_user = db_config.get("username", "")
        self.db_pass = db_config.get("password", "")
        self.db_name = db_config.get("db", "")
        self.db_port = db_config.get("port", "")
        self.db_account = db_config.get("account", "")
        self.db_warehouse = db_config.get("warehouse", "")
        self.db_schema = db_config.get("schema", "")
        self.db_protocol = db_config.get("protocol", "")
        self.db_use = config.get("DB_Use", "")

    def __del__(self):
        self.close_connection()

    def open_connection(self):
        # This connection is for Postgres DB. Comment out below lines if you want to use Snowflake
        if self.db_use == "postgres":
            self.db_conn = psycopg2.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_pass,
            )
        else:
            # This connect is for Snowflake. Uncomment below lines if you want to use with Snowflake
            self.db_conn = snowflake.connector.connect(
                host=self.db_host,
                user=self.db_user,
                password=self.db_pass,
                account=self.db_account,
                warehouse=self.db_warehouse,
                database=self.db_name,
                schema=self.db_schema,
                protocol=self.db_protocol,
                port=self.db_port
            )

    def close_connection(self):
        if self.db_conn:
            self.db_conn.close()

    def fetch_all(self, query):
        self.open_connection()
        if self.db_use == "postgres":
            # This is to get rows from Postgres DB.
            cursor = self.db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        else:
            # This is to get rows from Snowflake DB.
            cursor = self.db_conn.cursor(snowflake.connector.DictCursor)
        cursor.execute(query)
        query_results = cursor.fetchall()
        cursor.close()
        self.close_connection()
        return query_results

    def create_pandas_table(self, query, args=None):
        """ Return pandas dataframe """
        self.open_connection()
        # This is to get rows from Postgres DB. Comment out below line if you want to use Snowflake
        df = pd.read_sql_query(query, self.db_conn)
        # This is to get rows from Snowflake. Uncomment it.
        # cursor = self.db_conn.cursor()
        # cursor.execute(query)
        # df = cursor.fetch_pandas_all()
        self.close_connection()
        return df

    def bulk_update(self, query, records):
        """ Bulk update list of records """
        self.open_connection()
        # Cursor is same for both Postgres and Snowflake DB
        cursor = self.db_conn.cursor()
        cursor.executemany(query, records)
        self.db_conn.commit()
        row_count = cursor.rowcount
        cursor.close()
        self.close_connection()
        return row_count

    @classmethod
    def from_config_file(cls, file):
        """ Read the config file to get DB data """
        config_file = Path(file)
        if not config_file.is_file():
            raise FileNotFoundError(f"DB config file {config_file} doesn't exist")
        with open(config_file, mode="r") as fp:
            config_data = json.load(fp)
        return cls(config_data)


if __name__ == "__main__":
    db_config_file = "/Users/dibyaranjan/Upwork/client_soujanya_gui/database_update_gui/config/db_config.json"
    dbhandler = DBHandler.from_config_file(db_config_file)
    query = "SELECT * FROM div_contact_list_audit LIMIT 20;"
    # results = dbhandler.fetch_all(query=query)
    df = dbhandler.create_pandas_table(query)
    print(df)
    breakpoint()
