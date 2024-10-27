"""
Fetches Automatic Dependent Surveillance–Broadcast (ADSB) data on demand 
from the OpenSky API (https://openskynetwork.github.io/opensky-api/rest.html) 
and pushes the data to a queue for downstream processing.
"""
import os
import json
import aiohttp
import asyncio
import logging
from dotenv import load_dotenv
from lib.rabbitmq import RabbitMQService

load_dotenv()

# Load environment variables
HOST = os.getenv("RABBIT_HOST")
REGIONS_QUEUE = os.getenv("REGIONS_QUEUE")
ADSB_QUEUE = os.getenv("ADSB_QUEUE")
OPENSKY_API_URL = os.getenv("OPENSKY_API_URL")

# Validate environment variables
def validate_env_variables():
    if not all([HOST, REGIONS_QUEUE, ADSB_QUEUE, OPENSKY_API_URL]):
        raise EnvironmentError("One or more environment variables are missing.")

validate_env_variables()

# Set up logging configuration
log_file = os.path.splitext(os.path.basename(__file__))[0] + '.log'
logging.basicConfig(filename=log_file, level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class OpenSkyService:
    def __init__(self, queue_service: RabbitMQService) -> None:        
        """
        Initialize the OpenSkyService with a RabbitMQ service instance.

        Args:
            queue_service (RabbitMQService): The RabbitMQ service for managing queues.
        """
        self.queue_service = queue_service
        self.api_url = OPENSKY_API_URL

    async def fetch_data(self, regions: dict) -> dict:
        """
        Fetch ADS-B data from the OpenSky API for the specified regions.

        Args:
            regions (dict): A dictionary containing region parameters for the API request.

        Returns:
            dict: The JSON response containing ADS-B data.

        Raises:
            HTTPError: If the request to the OpenSky API fails.
        """
        url = f"{self.api_url}/states/all"
        logging.info(f"Requesting URL: {url} with params: {regions}")

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=regions) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logging.error(f"Failed to fetch data: {response.status} {response.reason} for regions: {regions}")
                    response.raise_for_status()        

    def get_messages(self, in_queue: str, out_queue: str) -> None:
        """
        Start consuming messages from the specified input queue and fetch data for each message.

        Args:
            in_queue (str): The name of the input queue to consume messages from.
            out_queue (str): The name of the output queue to push fetched data to.
        """
        def callback(ch, method, properties, body):   
            """
            Callback function to process each message from the input queue.

            Args:
                ch: The channel object.
                method: The method frame.
                properties: The properties frame.
                body: The message body received from the queue.

            Raises:
                json.JSONDecodeError: If the message body is not valid JSON.
            """
            try:   
                regions = json.loads(body)  
                flight_data = asyncio.run(self.fetch_data(regions))  
                self.queue_service.push_to_queue(out_queue, json.dumps(flight_data))
            except json.JSONDecodeError as e:
                logging.error(f"Invalid JSON received: {body} | Exception: {e}")
            except Exception as e:
                logging.error(f"Error processing message: {e}")

        self.queue_service.start_consuming(queue_name=in_queue, callback=callback)
    

if __name__ == "__main__":
    queue_service = RabbitMQService(HOST)
    service = OpenSkyService(queue_service=queue_service)
    service.get_messages(REGIONS_QUEUE, ADSB_QUEUE)
