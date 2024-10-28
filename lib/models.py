from pydantic import BaseModel, Field 
from typing import Optional, List
from datetime import datetime

class Region(BaseModel):
    """
    Represents a geographical region defined by minimum and 
    maximum latitude and longitude coordinates.
    
    Attributes:
        lamin (float): Minimum latitude.
        lomin (float): Minimum longitude.
        lamax (float): Maximum latitude.
        lomax (float): Maximum longitude.
    """
    lamin: float
    lomin: float
    lamax: float
    lomax: float

class Adsb(BaseModel):
    """
   Represents the state of an aircraft, including its position, 
    flight parameters, and transponder details.

    Attributes:
        icao24 (str): Unique ICAO 24-bit address of the transponder in hex.
        callsign (str): Vehicle callsign (up to 8 chars), can be null.
        origin_country (str): Country name inferred from the ICAO address.
        time_position (Optional[int]): Unix timestamp for the last position update.
        last_contact (Optional[int]): Unix timestamp for the last update.
        longitude (Optional[float]): WGS-84 longitude in decimal degrees.
        latitude (Optional[float]): WGS-84 latitude in decimal degrees.
        baro_altitude (Optional[float]): Barometric altitude in meters.
        on_ground (Optional[bool]): Indicates if the position was from a surface report.
        velocity (Optional[float]): Velocity over ground in m/s.
        true_track (Optional[float]): True track in degrees clockwise from north.
        vertical_rate (Optional[float]): Vertical rate in m/s (positive for climbing).
        sensors (Optional[List[int]]): IDs of receivers contributing to this state.
        geo_altitude (Optional[float]): Geometric altitude in meters.
        squawk (Optional[str]): Transponder code (Squawk).
        spi (Optional[bool]): Indicates special purpose indicator status.
        position_source (Optional[int]): Source of the position (0 = ADS-B, etc.).
        category (Optional[int]): Aircraft category (e.g., 0 = No info, 2 = Light).

        Reference: https://openskynetwork.github.io/opensky-api/rest.html
    """
    icao24: str  
    callsign: str 
    origin_country: str  
    time_position: Optional[int] = Field(default=None)
    last_contact: Optional[int] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    latitude: Optional[float] = Field(default=None)
    baro_altitude: Optional[float] = Field(default=None)
    on_ground: Optional[bool] = Field(default=None)
    velocity: Optional[float] = Field(default=None, ge=0) 
    true_track: Optional[float] = Field(default=None)
    vertical_rate: Optional[float] = Field(default=None)
    sensors: Optional[List[int]] = Field(default=None)
    geo_altitude: Optional[float] = Field(default=None)
    squawk: Optional[str] = Field(default=None)
    spi: Optional[bool] = Field(default=None)
    position_source: Optional[int] = Field(default=None)

    class Config:
        str_strip_whitespace = True

class AdsbTable(Adsb):
    """
    Extends the Adsb model to include fields 
    for database operations.

    Attributes:
        id (Optional[int]): Unique identifier for the 
            aircraft state entry.
        update_batch (Optional[datetime]): Timestamp of the 
            last update.
    """
    id: Optional[int] = Field(default=None)
    update_batch: Optional[datetime] = None

class Coordinates(BaseModel):
    """
    Represents a pair of geographical coordinates 
    (latitude and longitude).

    Attributes:
        lat (float): Latitude of the coordinates.
        lng (float): Longitude of the coordinates.
    """
    lat: float
    lng: float

class BoundingBox(BaseModel):
    """
    Defines a rectangular area using two Coordinates 
    representing the northeast and southwest corners.

    Attributes:
        northEast (Coordinates): Coordinates of the northeast 
            corner.
        southWest (Coordinates): Coordinates of the southwest 
            corner.
    """
    northEast: Coordinates
    southWest: Coordinates

class BoundingBoxesRequest(BaseModel):
    """
    Represents a request containing multiple bounding 
    boxes for querying flight data.

    Attributes:
        bounding_boxes (List[BoundingBox]): List of bounding 
            boxes to be queried.
    """
    bounding_boxes: List[BoundingBox]
    
class RegionResponse(BaseModel):
    """
    A simple response model to return messages 
    related to geographical regions.

    Attributes:
        message (str): Response message.
    """
    message: str

class FlightDataResponse(BaseModel):
    """
    Contains a list of Adsb objects, 
    representing the current state of all tracked flights.

    Attributes:
        flights (List[Adsb]): List of aircraft states.
    """
    flights: List[Adsb]
