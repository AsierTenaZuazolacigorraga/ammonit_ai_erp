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
  const firstMachine = machines?.data[0];
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
            {isLoading ? (
              <Text>Loading...</Text>
            ) : isError ? (
              <Text>Error loading</Text>
            ) : (
              <>
                {firstMachine ? (
                  <Table size="sm">
                    <Tbody>
                      <Tr>
                        <Td>{firstMachine.id}</Td>
                        <Td>...</Td>
                      </Tr>
                      <Tr>
                        <Td>{firstMachine.name}</Td>
                        <Td>...</Td>
                      </Tr>
                      <Tr>
                        <Td>{firstMachine.provider}</Td>
                        <Td>...</Td>
                      </Tr>
                      <Tr>
                        <Td>{firstMachine.plc}</Td>
                        <Td>...</Td>
                      </Tr>
                    </Tbody>
                  </Table>
                ) : (
                  <Table size="sm">
                    <Tbody>
                      <Tr>
                        <Td>Id</Td>
                        <Td>...</Td>
                      </Tr>
                      <Tr>
                        <Td>Name</Td>
                        <Td>...</Td>
                      </Tr>
                      <Tr>
                        <Td>Provider</Td>
                        <Td>...</Td>
                      </Tr>
                      <Tr>
                        <Td>PLC</Td>
                        <Td>...</Td>
                      </Tr>
                    </Tbody>
                  </Table>
                )}
              </>
            )}
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
                <CircularIndicator label="OEE" value={74} />
              </GridItem>
              <GridItem rowSpan={1} colSpan={1}>
                <CircularIndicator label="Availability" value={85} />
              </GridItem>
              <GridItem rowSpan={1} colSpan={1}>
                <CircularIndicator label="Performance" value={90} />
              </GridItem>
              <GridItem rowSpan={1} colSpan={1}>
                <CircularIndicator label="Quality" value={97} />
              </GridItem>
            </Grid>
          </Box>
        </GridItem>
      </Grid>
    </Container>
  )
}