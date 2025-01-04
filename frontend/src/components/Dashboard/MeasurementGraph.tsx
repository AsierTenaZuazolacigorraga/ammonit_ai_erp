import { Box, Heading } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import ReactApexChart from "react-apexcharts";


interface MeasurementGraphProps {
    measurements: any;
}

function MeasurementGraph({ measurements }: MeasurementGraphProps) {

    const generateDataset = (timestamps_data: number[], temperature_data: number[], power_usage_data: number[]) => ({
        options: {
            chart: {
                toolbar: {
                    show: false
                },
                zoom: {
                    enabled: false // Disable zoom
                }
            },
            tooltip: {
                theme: "dark"
            },
            dataLabels: {
                enabled: false
            },
            stroke: {
                curve: "smooth" as "smooth",
                width: 3, // Thicker lines for better visibility
                colors: ["#4FD1C5", "#2D3748"] // Vibrant colors for the lines
            },
            xaxis: {
                type: "datetime" as "datetime",
                categories: timestamps_data,
                labels: {
                    style: {
                        colors: "#c8cfca",
                        fontSize: "12px"
                    }
                }
            },
            yaxis: {
                labels: {
                    style: {
                        colors: "#c8cfca",
                        fontSize: "12px"
                    }
                }
            },
            legend: {
                show: true // Display legend for better clarity
            },
            grid: {
                strokeDashArray: 5,
                yaxis: {
                    lines: {
                        show: false
                    }
                },
                xaxis: {
                    lines: {
                        show: true
                    }
                }
            },
            fill: {
                type: "solid", // Change gradient to solid fill
                colors: ["#4FD1C5", "#2D3748"] // Match the stroke colors
            },
            colors: ["#4FD1C5", "#2D3748"] // Use the same colors for consistency
        },
        data: [
            {
                name: "Temperature (°C)",
                data: temperature_data,
            },
            {
                name: "Power Usage (kW)",
                data: power_usage_data,
            },
        ]
    });

    const [graphData, setGraphData] = useState(generateDataset([], [], []));

    useEffect(() => {

        console.log("useEffect triggered");

        if (measurements) {
            console.log("Updating graph data with new measurements");

            const timestamps = measurements.data.map((measurement: any) => {
                const date = new Date(measurement.timestamp);
                return isNaN(date.getTime()) ? null : date.toISOString();
            }).filter((timestamp: string | null) => timestamp !== null);
            // const timestamps = measurements.data.map((measurement: any) => measurement.timestamps.toISOString());
            const temperatures = measurements.data.map((measurement: any) => measurement.temperature);
            const powerUsages = measurements.data.map((measurement: any) => measurement.power_usage);

            setGraphData(generateDataset(timestamps, temperatures, powerUsages));
        }

        else {
            console.log("No measurements data available");
        }

    }, [measurements]);

    return (
        <Box p={5} bg="ui.light" borderRadius="md" boxShadow="md" height="100%">
            <Heading size="md" pb={4}>Measurement Graph</Heading>
            {/* <Line data={graphData} options={options} /> */}
            <ReactApexChart
                options={graphData.options}
                series={graphData.data}
                type='line'
                width='100%'
                height='100%'
            />
        </Box >
    );
}

export default MeasurementGraph;
