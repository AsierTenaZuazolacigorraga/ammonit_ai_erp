import { Box, Heading, Table, Tbody, Td, Tr } from '@chakra-ui/react';

interface MachineDetailsProps {
    machine: any;
}

const MachineDetails = ({ machine }: MachineDetailsProps) => {
    return (
        <Box p={5} bg="ui.light" borderRadius="md" boxShadow="md" height="100%">
            <Heading size="md" pb={4}>Machine</Heading>
            <Table size="sm">
                <Tbody>
                    <Tr>
                        <Td>Id</Td>
                        <Td>{machine.id}</Td>
                    </Tr>
                    <Tr>
                        <Td>Name</Td>
                        <Td>{machine.name}</Td>
                    </Tr>
                    <Tr>
                        <Td>Provider</Td>
                        <Td>{machine.provider}</Td>
                    </Tr>
                    <Tr>
                        <Td>PLC</Td>
                        <Td>{machine.plc}</Td>
                    </Tr>
                </Tbody>
            </Table>
        </Box>
    );
};

export default MachineDetails;