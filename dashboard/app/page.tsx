"use client";

import React, { useEffect, useState } from 'react';
import dynamic from 'next/dynamic';
import MissionControl from '@/components/ui/mission-control';

const Map = dynamic(() => import('@/components/ui/Map'), {
    ssr: false, // Disable server-side rendering for this component
});

const MapPage = () => {
    const [allBoundingBoxes, setAllBoundingBoxes] = useState([]);
    const [flightData, setFlightData] = useState([]);

    // Fetch flight data from the API
    const fetchFlightData = () => {
        fetch(`${process.env.NEXT_PUBLIC_MC_API_URL}/flights`)
            .then((response) => response.json())
            .then((data) => setFlightData(data))
            .catch((error) => console.error('Error fetching flight data:', error));
    };

    useEffect(() => {
        fetchFlightData(); // Fetch flight data on component mount
        const intervalId = setInterval(fetchFlightData, 5000); // Refresh flight data every 5 seconds
        return () => clearInterval(intervalId); // Cleanup the interval on unmount
    }, []);

   const onDrawCreated = (event) => {
        const layer = event.layer;
        const bounds = layer.getBounds();
        const northEast = bounds.getNorthEast();
        const southWest = bounds.getSouthWest();

        const newBoundingBox = {
            northEast: {
                lat: northEast.lat,
                lng: northEast.lng,
            },
            southWest: {
                lat: southWest.lat,
                lng: southWest.lng,
            },
        };

        setAllBoundingBoxes([newBoundingBox]);

        // POST request with bounding box data
        fetch(`${process.env.NEXT_PUBLIC_MC_API_URL}/setregions`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ bounding_boxes: [newBoundingBox] }),
        })
            .then((response) => response.json())
            .then((data) => console.log('Success:', data))
            .catch((error) => console.error('Error:', error));
    };

    return (
        <div style={{ position: 'relative', width: '100vw', height: '100vh' }}>
        <h1 style={{ position: 'absolute', zIndex: 1000, top: '10px', left: '10px', color: 'white' }}>Air Traffic Controller Simulation</h1>

        {/* Map section - full screen */}
        <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}>
            <Map onDrawCreated={onDrawCreated} />
        </div>

        {/* Overlapping panel at the bottom */}
        <div style={{ position: 'absolute', bottom: 0, left: 0, width: '100%', height: '30vh', backgroundColor: 'rgba(255, 255, 255, 0.9)', zIndex: 1000, overflowY: 'auto' }}>
            <MissionControl flightData={flightData} />
        </div>
    </div>
    );
};

export default MapPage;