import { Container, Grid, GridItem, Heading } from '@chakra-ui/react';
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { useEffect } from 'react';
import { MachinePublic, MachinesService, MeasurementsPublic, MeasurementsService } from "../../client";
import MachineDetails from '../../components/Dashboard/MachineDetails';
import MeasurementGraph from '../../components/Dashboard/MeasurementGraph';
import OEEIndicators from '../../components/Dashboard/OEEIndicators';

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

function Dashboard() {

  // Obtain machines data
  const { data: machinesData, isLoading: machinesIsLoading, isError: machinesIsError } = useQuery({
    queryKey: ['machines'],
    queryFn: () => MachinesService.readMachines(),
  });

  let machine: MachinePublic = {
    id: '...',
    owner_id: '...',
    name: '...',
    provider: '...',
    plc: '...',
    oee_availability: 0,
    oee_performance: 0,
    oee_quality: 0,
    oee: 0,
  };
  if (machinesIsLoading) {
    // Keep the default loading state
  } else if (machinesIsError) {
    machine = {
      id: 'Error',
      owner_id: 'Error',
      name: 'Error',
      provider: 'Error',
      plc: 'Error',
      oee_availability: 0,
      oee_performance: 0,
      oee_quality: 0,
      oee: 0,
    };
  } else if (machinesData?.data[0]) {
    machine = machinesData.data[0];
  }

  // Obtain measurements data
  const { data: measurementsData, isLoading: measurementsIsLoading, isError: measurementsIsError } = useQuery({
    queryKey: ["measurements"],
    queryFn: () => MeasurementsService.readLatestMeasurements({ machineId: machine.id }),
  });

  // Polling mechanism to refresh measurements data
  const queryClient = useQueryClient();
  useEffect(() => {
    const interval = setInterval(() => {
      queryClient.invalidateQueries({ queryKey: ["measurements"] });
    }, 5000); // Poll every 5 seconds

    return () => clearInterval(interval);
  }, [queryClient]);

  let measurements: MeasurementsPublic = {
    data: [{
      "id": "...",
      "owner_id": "...",
      "timestamp": "...",
      "temperature": 0,
      "power_usage": 0,
    }],
    count: 0,
  };
  if (measurementsIsLoading) {
    // Keep the default loading state
  } else if (measurementsIsError) {
    measurements = {
      data: [{
        "id": "Error",
        "owner_id": "Error",
        "timestamp": "Error",
        "temperature": 0,
        "power_usage": 0,
      }],
      count: 0,
    };
  } else if (measurementsData?.data) {
    measurements = measurementsData;
  }

  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} py={12}>
        Dashboard
      </Heading>
      <Grid
        templateRows="repeat(1, 1fr)"
        templateColumns="repeat(2, 1fr)"
        gap={4}
        alignItems="stretch"
      >
        <GridItem rowSpan={1} colSpan={1}>
          <MachineDetails machine={machine} />
        </GridItem>
        <GridItem rowSpan={1} colSpan={1}>
          <OEEIndicators machine={machine} />
        </GridItem>
        <GridItem rowSpan={2} colSpan={2} pb={4}>
          <MeasurementGraph measurements={measurements} />
        </GridItem>
      </Grid>
    </Container>
  );
}