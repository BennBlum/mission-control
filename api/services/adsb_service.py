import sqlite3
from typing import List
from lib.constants import *
from lib.models import AdsbTable

class AdsbService:
    """
    Service class to connect to a SQLite database and retrieve the latest ADS-B records.
    """
    def __init__(self, db_file: str):
        self.db_file = db_file

    def _get_connection(self) -> sqlite3.Connection:
        """
        Establishes and returns a connection to the SQLite database with row access by column name.

        Returns:
            sqlite3.Connection: A database connection object.
        """
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def fetch_all_aircraft_states(self) -> List[AdsbTable]:
        """
        Retrieves all ADS-B aircraft state records from the database that match the most recent update batch.

        Returns:
            list[AdsbTable]: List of validated aircraft state records.
        """       
        flights = []
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"""
                    WITH MaxBatch AS (
                        SELECT MAX(update_batch) AS max_batch
                        FROM {TABLE_ADSB}
                    )
                    SELECT *
                    FROM {TABLE_ADSB}
                    WHERE update_batch = (SELECT max_batch FROM MaxBatch);

                """)
                column_names = [desc[0] for desc in cursor.description]
                records = cursor.fetchall()

                if records:
                    flights = [
                        AdsbTable.model_validate(dict(zip(column_names, record)))
                        for record in records
                    ]

        except sqlite3.Error as e:
            flights = []
            raise Exception(f"Database error: {e}")

        return flights

