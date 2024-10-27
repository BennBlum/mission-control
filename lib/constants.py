TABLE_ADSB = "adsb"
CREATE_TABLE_ADSB = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_ADSB} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        icao24 TEXT NOT NULL,
        callsign TEXT NOT NULL,
        origin_country TEXT NOT NULL,
        time_position INTEGER,
        last_contact INTEGER,
        longitude REAL,
        latitude REAL,
        baro_altitude REAL,
        on_ground BOOLEAN,
        velocity REAL,
        true_track REAL,
        vertical_rate REAL,
        sensors TEXT,
        geo_altitude REAL,
        squawk TEXT,
        spi BOOLEAN,
        position_source INTEGER,
        update_batch TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""

COLUMN_ICAO24 = "icao24"
COLUMN_CALLSIGN = "callsign"
COLUMN_ORIGIN_COUNTRY = "origin_country"
COLUMN_TIME_POSITION = "time_position"
COLUMN_LAST_CONTACT = "last_contact"
COLUMN_LONGITUDE = "longitude"
COLUMN_LATITUDE = "latitude"
COLUMN_BARO_ALTITUDE = "baro_altitude"
COLUMN_ON_GROUND = "on_ground"
COLUMN_VELOCITY = "velocity"
COLUMN_TRUE_TRACK = "true_track"
COLUMN_VERTICAL_RATE = "vertical_rate"
COLUMN_SENSORS = "sensors"
COLUMN_GEO_ALTITUDE = "geo_altitude"
COLUMN_SQUAWK = "squawk"
COLUMN_SPI = "spi"
COLUMN_POSITION_SOURCE = "position_source"
COLUMN_UPDATE_BATCH = "update_batch"


INSERT_AIRCRAFT_SQL = f"""
    INSERT INTO {TABLE_ADSB} (
        icao24, callsign, origin_country, time_position,
        last_contact, longitude, latitude, baro_altitude,
        on_ground, velocity, true_track, vertical_rate, sensors,
        geo_altitude, squawk, spi, position_source
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

SELECT_LATEST_ADSB_RECORD = f"""
    WITH MaxBatch AS (
    SELECT MAX(update_batch) AS max_batch
    FROM {TABLE_ADSB}
    )
    SELECT *
    FROM {TABLE_ADSB}
    WHERE update_batch = (SELECT max_batch FROM MaxBatch);

"""