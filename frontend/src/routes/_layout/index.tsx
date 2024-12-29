import { Box, CircularProgress, CircularProgressLabel, Container, Grid, GridItem, Heading, Stack, Table, Tbody, Td, Text, Tr } from '@chakra-ui/react';
import { useQuery } from "@tanstack/react-query";
import { createFileRoute } from "@tanstack/react-router";
import { MachinesService } from "../../client";

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
})

interface CircularIndicatorProps {
  label: string;
  value: number; // Percentage value (0-100)
}

function CircularIndicator({ label, value }: CircularIndicatorProps) {
  return (
    <Stack align="center">
      <CircularProgress value={value} color="ui.main" size="100px" thickness="12px">
        <CircularProgressLabel >{`${value}%`}</CircularProgressLabel>
      </CircularProgress>
      <Text >{label}</Text>
    </Stack>
  );
};

function Dashboard() {
  // const { user: currentUser } = useAuth()
  // const bgColor = useColorModeValue("ui.light", "ui.dark")
  const { data: machines, isLoading, isError } = useQuery({
    queryKey: ['machines'],
    queryFn: () => MachinesService.readMachines(),
  });

  // Select the first machine
  let firstMachine = machines?.data[0];

  if (isLoading || !firstMachine) {
    firstMachine = {
      id: '...',
      name: '...',
      provider: '...',
      plc: '...',
      oee_availability: 0,
      oee_performance: 0,
      oee_quality: 0,
      oee: 0,
      owner_id: '...'
    };
  } else if (isError) {
    firstMachine = {
      id: 'Error',
      name: 'Error',
      provider: 'Error',
      plc: 'Error',
      oee_availability: 0,
      oee_performance: 0,
      oee_quality: 0,
      oee: 0,
      owner_id: 'Error',
    };
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
      >
        <GridItem rowSpan={1} colSpan={1}>
          <Box p={5} bg="ui.light" borderRadius="md" boxShadow="md">
            <Heading size="md" pb={4}>Machine</Heading>
            <Table size="sm">
              <Tbody>
                <Tr>
                  <Td>Id</Td>
                  <Td>{firstMachine.id}</Td>
                </Tr>
                <Tr>
                  <Td>Name</Td>
                  <Td>{firstMachine.name}</Td>
                </Tr>
                <Tr>
                  <Td>Provider</Td>
                  <Td>{firstMachine.provider}</Td>

                </Tr>
                <Tr>
                  <Td>PLC</Td>
                  <Td>{firstMachine.plc}</Td>

                </Tr>
              </Tbody>
            </Table>

          </Box>
        </GridItem>
        <GridItem rowSpan={1} colSpan={1} >
          <Box p={5} bg="ui.light" borderRadius="md" boxShadow="md">
            <Heading size="md" pb={4}>OEE</Heading>
            <Grid
              templateRows="repeat(2, 1fr)"
              templateColumns="repeat(3, 1fr)"
              gap={4}
            >
              <GridItem rowSpan={1} colSpan={3}>
                <CircularIndicator label="OEE" value={firstMachine.oee} />
              </GridItem>
              <GridItem rowSpan={1} colSpan={1}>
                <CircularIndicator label="Availability" value={firstMachine.oee_availability} />
              </GridItem>
              <GridItem rowSpan={1} colSpan={1}>
                <CircularIndicator label="Performance" value={firstMachine.oee_performance} />
              </GridItem>
              <GridItem rowSpan={1} colSpan={1}>
                <CircularIndicator label="Quality" value={firstMachine.oee_quality} />
              </GridItem>
            </Grid>
          </Box>
        </GridItem>
      </Grid>
    </Container>
  );
}