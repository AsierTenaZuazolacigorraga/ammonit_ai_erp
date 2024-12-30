import { Box, Heading } from "@chakra-ui/react";
import { CategoryScale, Chart as ChartJS, Legend, LinearScale, LineElement, PointElement, Title, Tooltip } from "chart.js";
import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";

// Register Chart.js modules
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

interface MeasurementGraphProps {
    measurements: any;
}

function MeasurementGraph({ measurements }: MeasurementGraphProps) {

    const generateDataset = (labels: number[], temperature_data: number[], power_usage_data: number[]) => ({
        labels: labels,
        datasets: [
            {
                label: "Temperature (°C)",
                data: temperature_data,
                borderColor: "rgba(255, 99, 132, 1)",
                backgroundColor: "rgba(255, 99, 132, 0.2)",
                fill: false,
                tension: 0.1,
            },
            {
                label: "Power Usage (kW)",
                data: power_usage_data,
                borderColor: "rgba(54, 162, 235, 1)",
                backgroundColor: "rgba(54, 162, 235, 0.2)",
                fill: false,
                tension: 0.1,
            },
        ],
    });

    const [graphData, setGraphData] = useState(generateDataset([], [], []));

    useEffect(() => {

        console.log("useEffect triggered");

        if (measurements) {
            const timestamps = measurements.data.map((measurement: any) => new Date(measurement.timestamp).toLocaleTimeString());
            const temperatures = measurements.data.map((measurement: any) => measurement.temperature);
            const powerUsages = measurements.data.map((measurement: any) => measurement.power_usage);

            setGraphData(generateDataset(timestamps, temperatures, powerUsages));
        }

        else {
            console.log("No measurements data available");
        }

    }, [measurements]);

    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: "top" as const,
            },
            title: {
                display: true,
                text: "Measurements Over Time",
            },
        },
        scales: {
            x: {
                title: {
                    display: true,
                    text: "Time",
                },
            },
            y: {
                title: {
                    display: true,
                    text: "Values",
                },
            },
        },
    };

    return (
        <Box p={5} bg="ui.light" borderRadius="md" boxShadow="md" height="100%">
            <Heading size="md" pb={4}>Measurement Graph</Heading>
            <Line data={graphData} options={options} />
        </Box >
    );
}

export default MeasurementGraph;
