"""
Receives Automatic Dependent Surveillance–Broadcast (ADS-B) data from the OpenSky via a RabbitMQ queue,
and adds a new record to a sqlite database.
"""
import json
import logging
import os
import sqlite3
from sqlite3 import Error
from lib.constants import *
from dotenv import load_dotenv
from lib.models import Adsb
from lib.rabbitmq import RabbitMQService

load_dotenv()

# Load environment variables
DATABASE = os.getenv("DATABASE_NAME")
HOST = os.getenv("RABBIT_HOST")
QUEUE = os.getenv("ADSB_QUEUE")

# Validate environment variables
def validate_env_variables():
    if not all([DATABASE, HOST, QUEUE]):
        raise EnvironmentError("One or more environment variables are missing.")

validate_env_variables()


# Set up logging configuration
log_file = os.path.splitext(os.path.basename(__file__))[0] + '.log'
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def create_connection(db_file: str) -> sqlite3.Connection:
    """
    Establish a connection to the database.

    Args:
        db_file (str): The path to the database file.

    Returns:
        sqlite3.Connection: The database connection object.

    Raises:
        ValueError: If the database name is None.
        Error: If there is an error connecting to the database.
    """
    try:
        if db_file is None:
            logging.error("No database name specified.")
            raise ValueError("Database name cannot be None.")

        conn = sqlite3.connect(db_file)
        logging.info(f"Connected to {db_file}")
        return conn
    except Error as e:
        logging.error(f"Error connecting to database: {e}")
        raise

def create_table(conn: sqlite3.Connection) -> None:
    """
    Create the aircraft table in the database if it doesn't already exist.

    Args:
        conn (sqlite3.Connection): The database connection object.

    Raises:
        Error: If there is an error creating the table.
    """
    try:
        with conn:
            conn.execute(CREATE_TABLE_ADSB)
        logging.info("Table created successfully")
    except Error as e:
        logging.error(f"Error creating table: {e}")
        raise

def update_aircraft_states(data: dict, conn: sqlite3.Connection):
    """
    Update aircraft states in the database based on the provided ADS-B data.

    Args:
        data (dict): The ADS-B data containing aircraft states.
        conn (sqlite3.Connection): The database connection object.

    Raises:
        Error: If there is an error updating aircraft states.
    """
    try:
        with conn:
            for state in data.get('states', []):
                aircraft_state = Adsb(**{
                    "icao24": state[0].strip(),
                    "callsign": state[1].strip(),
                    "origin_country": state[2].strip(),
                    "time_position": state[3],
                    "last_contact": state[4],
                    "longitude": state[5],
                    "latitude": state[6],
                    "baro_altitude": state[7],
                    "on_ground": bool(state[8]),
                    "velocity": state[9],
                    "true_track": state[10],
                    "vertical_rate": state[11],
                    "sensors": state[12],
                    "geo_altitude": state[13],
                    "squawk": state[14],
                    "spi": bool(state[15]),
                    "position_source": state[16]
                })

                insert_values = (
                    aircraft_state.icao24,
                    aircraft_state.callsign,
                    aircraft_state.origin_country,
                    aircraft_state.time_position,
                    aircraft_state.last_contact,
                    aircraft_state.longitude,
                    aircraft_state.latitude,
                    aircraft_state.baro_altitude,
                    aircraft_state.on_ground,
                    aircraft_state.velocity,
                    aircraft_state.true_track,
                    aircraft_state.vertical_rate,
                    aircraft_state.sensors,
                    aircraft_state.geo_altitude,
                    aircraft_state.squawk,
                    aircraft_state.spi,
                    aircraft_state.position_source
                )
                conn.execute(INSERT_ADSB_SQL, insert_values)
    except Error as e:
        logging.error(f"Error updating aircraft states: {e}")
        raise    

def update_db(queue_service: RabbitMQService, queue_name: str, conn: sqlite3.Connection):
    """
    Consume messages from the RabbitMQ queue and update the database with the received ADS-B data.

    Args:
        queue_service (RabbitMQService): The RabbitMQ service instance for message consumption.
        queue_name (str): The name of the queue to consume from.
        conn (sqlite3.Connection): The database connection object.
    """
    def callback(ch, method, properties, body):
        """
        Callback function to process each message from the RabbitMQ queue.

        Args:
            ch: The channel object.
            method: The method frame.
            properties: The properties frame.
            body: The message body received from the queue.

        Raises:
            json.JSONDecodeError: If the message body is not valid JSON.
        """
        try:
            data = json.loads(body)
            logging.info("Received data: %s", data)
            update_aircraft_states(data, conn)
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON received: {body}")

    queue_service.start_consuming(queue_name=queue_name, callback=callback)

def main():
    """
    Main entry point of the application.

    Establishes a database connection, creates the necessary tables, 
    and starts consuming messages from the RabbitMQ queue.
    """
    with create_connection(DATABASE) as conn:
        create_table(conn)
        queue_service = RabbitMQService(HOST)
        update_db(queue_service, QUEUE, conn)

if __name__ == "__main__":
    main()
