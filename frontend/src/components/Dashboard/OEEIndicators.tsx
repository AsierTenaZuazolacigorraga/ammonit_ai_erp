import { Box, Grid, GridItem, Heading } from '@chakra-ui/react';

import { CircularProgress, CircularProgressLabel, Stack, Text } from '@chakra-ui/react';

interface CircularIndicatorProps {
    value: number;
    label: string;
}

const CircularIndicator = ({ value, label }: CircularIndicatorProps) => {
    return (
        <Stack align="center">
            <CircularProgress value={value} color="ui.main" size="80px" thickness="12px">
                <CircularProgressLabel>{`${value}%`}</CircularProgressLabel>
            </CircularProgress>
            <Text>{label}</Text>
        </Stack>
    );
};

interface OEEIndicatorsProps {
    machine: any;
}

const OEEIndicators = ({ machine }: OEEIndicatorsProps) => {
    return (
        <Box p={5} bg="ui.light" borderRadius="md" boxShadow="md" height="100%">
            <Heading size="md" pb={4}>OEE Indicators</Heading>
            <Grid
                templateRows="repeat(2, 1fr)"
                templateColumns="repeat(3, 1fr)"
                gap={4}
            >
                <GridItem rowSpan={1} colSpan={3}>
                    <CircularIndicator label="OEE" value={machine.oee} />
                </GridItem>
                <GridItem rowSpan={1} colSpan={1}>
                    <CircularIndicator label="Availability" value={machine.oee_availability} />
                </GridItem>
                <GridItem rowSpan={1} colSpan={1}>
                    <CircularIndicator label="Performance" value={machine.oee_performance} />
                </GridItem>
                <GridItem rowSpan={1} colSpan={1}>
                    <CircularIndicator label="Quality" value={machine.oee_quality} />
                </GridItem>
            </Grid>
        </Box>
    );
};

export default OEEIndicators;