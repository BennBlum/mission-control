"use client";

import React, { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, FeatureGroup } from 'react-leaflet';
import { EditControl } from "react-leaflet-draw";
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';

const Map = ({ onDrawCreated }) => {
    const mapRef = useRef();
    const drawnItemsRef = useRef(L.featureGroup());
    let markers = null;

    const updateAircraftPosition = () => {
        fetch(`${process.env.NEXT_PUBLIC_ATC_API_URL}`)
            .then((response) => response.json())
            .then((flightPaths) => {
                const map = mapRef.current;

                if (markers != null)
                    markers.remove();

                markers = new L.FeatureGroup();
                flightPaths.forEach(flight => {
                    const { icao24, latitude, longitude, callsign } = flight;

                    // Create a new marker
                    const aircraft = L.marker([latitude, longitude], {
                        icon: L.divIcon({
                            className: 'aircraft-icon',
                            html: `
                              <div class="aircraft-marker" style="display: flex; flex-direction: column; align-items: center;">
                                    <div class="flight-number">${callsign.trim()}</div>
                                    <div class="aircraft-circle"></div>
                              </div>
                            `,
                            iconSize: [30, 30],
                            iconAnchor: [15, 30],
                        }),
                    });
                    markers.addLayer(aircraft);
                });
                map.addLayer(markers);
            })
            .catch((error) => console.error('Error updating aircraft position:', error));
    };

    useEffect(() => {
        const intervalId = setInterval(() => {
            updateAircraftPosition();
        }, process.env.NEXT_PUBLIC_FETCH_INTERVAL);

        return () => clearInterval(intervalId);
    }, []);

    const handleDrawCreated = (event) => {
        drawnItemsRef.current.clearLayers();
        const layer = event.layer;
        drawnItemsRef.current.addLayer(layer);

        if (onDrawCreated) {
            onDrawCreated(event);
        }
    };

    return (
        <MapContainer
            center={[-25.0, 135.0]}
            zoom={4}
            style={{ height: "80vh", width: "100%" }}
            ref={mapRef} // Attach map reference
        >
            <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            <FeatureGroup>
                <EditControl
                    position="topleft"
                    onCreated={handleDrawCreated}
                    draw={{
                        rectangle: true,
                        polyline: false,
                        polygon: false,
                        circle: false,
                        marker: false,
                        circlemarker: false,
                    }}
                />
            </FeatureGroup>
        </MapContainer>
    );
};

export default Map;
