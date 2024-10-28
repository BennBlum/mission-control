"use client";

import { useState } from "react";
import {
    Table,
    TableHeader,
    TableBody,
    TableRow,
    TableHead,
    TableCell,
} from "@/components/ui/table"; // Ensure the path is correct

export const description = "A collection of flight data charts.";

// Define the MissionControl component to accept flightData as a prop
export default function MissionControl({ flightData = [] }) {
    const [sortConfig, setSortConfig] = useState(null);
    const [filter, setFilter] = useState("");

    const sortedData = flightData.length > 0
        ? [...flightData].sort((a, b) => {
            if (sortConfig !== null) {
                const { key, direction } = sortConfig;
                // Ensure a and b are defined and have the key
                if (a[key] !== undefined && b[key] !== undefined) {
                    if (a[key] < b[key]) {
                        return direction === "ascending" ? -1 : 1;
                    }
                    if (a[key] > b[key]) {
                        return direction === "ascending" ? 1 : -1;
                    }
                }
            }
            return 0;
        })
        : []; // Return an empty array if flightData is empty

    const filteredData = sortedData.filter((data) =>
        data.callsign.toLowerCase().includes(filter.toLowerCase())
    );

    const requestSort = (key) => {
        let direction = "ascending";
        if (sortConfig && sortConfig.key === key && sortConfig.direction === "ascending") {
            direction = "descending";
        }
        setSortConfig({ key, direction });
    };

    return (
        <div>
            <input
                type="text"
                placeholder="Filter by callsign"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                className="mb-4 p-2 border border-gray-300"
            />
            <Table>
                <TableHeader>
                    <TableRow>
                        <TableHead onClick={() => requestSort("callsign")} className="cursor-pointer">
                            Callsign
                        </TableHead>
                        <TableHead onClick={() => requestSort("velocity")} className="cursor-pointer">
                            Velocity (m/s)
                        </TableHead>
                        <TableHead onClick={() => requestSort("longitude")} className="cursor-pointer">
                            Longitude
                        </TableHead>
                        <TableHead onClick={() => requestSort("latitude")} className="cursor-pointer">
                            Latitude
                        </TableHead>
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {filteredData.map((data, index) => (
                        <TableRow key={index}>
                            <TableCell>{data.callsign}</TableCell>
                            <TableCell>{data.velocity}</TableCell>
                            <TableCell>{data.longitude}</TableCell>
                            <TableCell>{data.latitude}</TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            </Table>
        </div>
    );
}
