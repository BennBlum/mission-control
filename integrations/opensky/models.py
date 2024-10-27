from pydantic import BaseModel

class Region(BaseModel):
    lamin: float
    lomin: float
    lamax: float
    lomax: float

