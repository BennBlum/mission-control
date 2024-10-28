"""
This FastAPI application serves as a backend for a Next.js dashboard that displays real-time aircraft positions on a map. 

The API handles requests for aircraft data within specific map regions:
1. Receives requests from the dashboard for ADS-B data in designated map areas.
2. Queues each request for a backend service to process, which retrieves ADS-B data and places it back in the queue.
3. A separate database updater service retrieves this ADS-B data from the queue and updates an SQLite database.
4. The dashboard polls the API's flight data endpoint, which fetches the latest aircraft positions from the database and returns them in a response.

This setup provides an asynchronous, near real-time flow of flight data between the backend and dashboard.
"""

import os
import json
import logging
from typing import List
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from lib.rabbitmq import RabbitMQService
from lib.models import (
    BoundingBoxesRequest,
    RegionResponse,
    FlightDataResponse,
    Adsb,
)
from api.services.adsb_service import AdsbService

# Configure logging
logging.basicConfig(level=logging.INFO)

load_dotenv()

# Load and validate environment variables
DATABASE = os.getenv("DATABASE_NAME")
HOST = os.getenv("RABBIT_HOST")
QUEUE = os.getenv("REGIONS_QUEUE")
ORGINS = os.getenv("ORIGINS")


def validate_env_variables():
    if not all([DATABASE, HOST, QUEUE]):
        raise EnvironmentError("One or more environment variables are missing.")


validate_env_variables()

app = FastAPI()

# Configure CORS for trusted origins
origins = os.getenv("ORIGINS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
adbs_service = AdsbService(DATABASE)
rabbit_service = RabbitMQService(HOST)


def get_adsb_service() -> AdsbService:
    """
    Get the ADS-B service instance.

    Returns:
        AdsbService: The initialized ADS-B service instance used for fetching flight data.
    """
    return adbs_service


def get_rabbit_service() -> RabbitMQService:
    """
    Get the RabbitMQ service instance.

    Returns:
        RabbitMQService: The initialized RabbitMQ service instance used for message queuing.
    """
    return rabbit_service


@app.get("/")
def index() -> dict:
    return {"version": os.getenv("API_VERSION", "0.0.0")}


@app.post("/api/setregions", response_model=RegionResponse)
def set_regions(
    request: BoundingBoxesRequest,
    rabbit_service: RabbitMQService = Depends(get_rabbit_service),
) -> RegionResponse:
    """
    Set the bounding regions for aircraft tracking.

    Args:
        request (BoundingBoxesRequest): The request containing bounding box coordinates.
        rabbit_service (RabbitMQService): The RabbitMQ service for queue management.

    Raises:
        HTTPException: If no bounding boxes are provided or if an error occurs during processing.

    Returns:
        RegionResponse: A response message indicating success or failure.
    """
    try:
        if not request.bounding_boxes:
            logging.warning("Received an empty bounding box list.")
            raise HTTPException(status_code=400, detail="No bounding boxes provided.")

        for box in request.bounding_boxes:
            regions = {
                "lamin": min(box.northEast.lat, box.southWest.lat),
                "lomin": min(box.northEast.lng, box.southWest.lng),
                "lamax": max(box.northEast.lat, box.southWest.lat),
                "lomax": max(box.northEast.lng, box.southWest.lng),
            }
            rabbit_service.push_to_queue(QUEUE, json.dumps(regions))
        return RegionResponse(message="Bounding boxes processed successfully")
    except Exception as e:
        logging.error(f"Error processing regions: {e}")
        raise HTTPException(
            status_code=422, detail=f"Error processing regions: {str(e)}"
        )

@app.get("/api/flights")
def flight_data(
    adbs_service: AdsbService = Depends(get_adsb_service),
) :
    """
    Retrieve the current flight data for all tracked aircraft.

    This endpoint fetches the latest aircraft positions and states from the database.

    Args:
        adbs_service (AdsbService): The ADS-B service for fetching aircraft data.

    Raises:
        HTTPException: If an error occurs while fetching flight data, a 500 Internal Server Error is raised.

    Returns:
        FlightDataResponse: A response object containing a list of aircraft states.
    """
    try:
        adbs_data = adbs_service.fetch_all_aircraft_states()
        flights: List[Adsb] = [
            Adsb(
                **{k: getattr(flight, k) for k in Adsb.model_fields.keys()}
            )
            for flight in adbs_data
        ]
        flights_dumped  = [flight.model_dump() for flight in flights]
        return flights_dumped
    except Exception as e:
        logging.error(f"Error fetching flight data: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
