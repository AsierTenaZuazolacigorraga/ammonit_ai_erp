import { Box, Heading } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import ReactApexChart from "react-apexcharts";


interface MeasurementGraphProps {
    measurements: any;
}

function MeasurementGraph({ measurements }: MeasurementGraphProps) {

    // const generateDataset = (labels: number[], temperature_data: number[], power_usage_data: number[]) => ({
    //     labels: labels,
    //     datasets: [
    //         {
    //             label: "Temperature (°C)",
    //             data: temperature_data,
    //             borderColor: "rgba(255, 99, 132, 1)",
    //             backgroundColor: "rgba(255, 99, 132, 0.2)",
    //             fill: false,
    //             tension: 0.1,
    //         },
    //         {
    //             label: "Power Usage (kW)",
    //             data: power_usage_data,
    //             borderColor: "rgba(54, 162, 235, 1)",
    //             backgroundColor: "rgba(54, 162, 235, 0.2)",
    //             fill: false,
    //             tension: 0.1,
    //         },
    //     ],
    // });

    // const options = {
    //     responsive: true,
    //     plugins: {
    //         legend: {
    //             position: "top" as const,
    //         },
    //         title: {
    //             display: true,
    //             text: "Measurements Over Time",
    //         },
    //     },
    //     scales: {
    //         x: {
    //             title: {
    //                 display: true,
    //                 text: "Time",
    //             },
    //         },
    //         y: {
    //             title: {
    //                 display: true,
    //                 text: "Values",
    //             },
    //         },
    //     },
    // };


    const generateDataset = (timestamps_data: number[], temperature_data: number[], power_usage_data: number[]) => ({
        options: {
            chart: {
                toolbar: {
                    show: false
                }
            },
            tooltip: {
                theme: "dark"
            },
            dataLabels: {
                enabled: false
            },
            stroke: {
                curve: "smooth" as "smooth"
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
                show: false
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
                type: "gradient",
                gradient: {
                    shade: "light",
                    type: "vertical",
                    shadeIntensity: 0.5,
                    gradientToColors: undefined, // optional, if not defined - uses the shades of same color in series
                    inverseColors: true,
                    opacityFrom: 0.8,
                    opacityTo: 0,
                    stops: []
                },
                colors: ["#4FD1C5", "#2D3748"]
            },
            colors: ["#4FD1C5", "#2D3748"]
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
            const timestamps = measurements.data.map((measurement: any) => {
                const date = new Date(measurement.timestamp);
                return isNaN(date.getTime()) ? null : date.toISOString();
            }).filter((timestamp: string | null) => timestamp !== null);
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
