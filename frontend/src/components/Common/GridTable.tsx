import { Box, Button, Flex, Input } from '@chakra-ui/react';
import { useMemo, useState } from 'react';
import { FiPlus, FiTrash2 } from 'react-icons/fi';

type Row = {
    [key: string]: string | number;
    id: number;
};

interface GridTableProps {
    inputData: string;
}

function GridTable({ inputData }: GridTableProps) {
    const { headers, initialRows } = useMemo(() => {
        const lines = inputData.trim().split('\n');
        const headers = lines[0].split(';');

        const rows = lines.slice(1).map((line, index) => {
            const values = line.split(';');
            const row: Record<string, string> = {};

            headers.forEach((header, i) => {
                row[header] = values[i] || '';
            });

            return {
                id: index + 1,
                ...row
            };
        });

        return { headers, initialRows: rows };
    }, [inputData]);

    const [rows, setRows] = useState<Row[]>(initialRows);

    const updateCell = (id: number, key: string, value: string) => {
        setRows(r =>
            r.map(row =>
                row.id === id ? { ...row, [key]: value } : row
            )
        );
    };

    const addRow = (afterId?: number) => {
        setRows(r => {
            const newId = Math.max(0, ...r.map(x => x.id)) + 1;
            const newRow: Row = {
                id: newId,
                ...Object.fromEntries(headers.map(header => [header, '']))
            };

            if (afterId === undefined) {
                return [...r, newRow];
            }

            const index = r.findIndex(row => row.id === afterId);
            if (index === -1) return [...r, newRow];

            return [
                ...r.slice(0, index + 1),
                newRow,
                ...r.slice(index + 1)
            ];
        });
    };

    const deleteRow = (id: number) =>
        setRows(r => r.filter(row => row.id !== id));

    return (
        <Box
            width="100%"
            overflowX="auto"
            borderWidth="1px"
            borderColor="gray.200"
            borderRadius="md"
            bg="white"
        >
            <Box
                display="grid"
                gridTemplateColumns={`80px repeat(${headers.length}, minmax(120px, 1fr))`}
                position="relative"
                width="100%"
            >
                {/* Headers */}
                <Box
                    gridColumn="1/-1"
                    display="grid"
                    gridTemplateColumns="subgrid"
                    borderBottomWidth="2px"
                    borderColor="gray.200"
                    position="sticky"
                    top={0}
                    bg="gray.50"
                    zIndex={1}
                >
                    <Box p={2} fontWeight="bold" textAlign="center">
                        Acciones
                    </Box>
                    {headers.map((header) => (
                        <Box
                            key={header}
                            p={2}
                            fontWeight="bold"
                            borderLeftWidth="1px"
                            borderColor="gray.200"
                            textAlign="left"
                        >
                            {header}
                        </Box>
                    ))}
                </Box>

                {/* Empty State */}
                {rows.length === 0 && (
                    <Box
                        gridColumn="1/-1"
                        display="grid"
                        gridTemplateColumns="subgrid"
                    >
                        <Box p={2} textAlign="center">
                            <Button
                                variant="ghost"
                                size="sm"
                                colorScheme="blue"
                                onClick={() => addRow()}
                            >
                                <FiPlus />
                            </Button>
                        </Box>
                        {headers.map((header) => (
                            <Box
                                key={header}
                                p={2}
                                borderLeftWidth="1px"
                                borderColor="gray.200"
                            />
                        ))}
                    </Box>
                )}

                {/* Data Rows */}
                {rows.map((row) => (
                    <Box
                        key={row.id}
                        gridColumn="1/-1"
                        display="grid"
                        gridTemplateColumns="subgrid"
                        borderTopWidth="1px"
                        borderColor="gray.200"
                        _hover={{ bg: "gray.50" }}
                    >
                        <Box p={1} textAlign="center">
                            <Flex gap={1} justify="center">
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    colorScheme="red"
                                    onClick={() => deleteRow(row.id)}
                                    p={1}
                                >
                                    <FiTrash2 />
                                </Button>
                                <Button
                                    variant="ghost"
                                    size="sm"
                                    colorScheme="blue"
                                    onClick={() => addRow(row.id)}
                                    p={1}
                                >
                                    <FiPlus />
                                </Button>
                            </Flex>
                        </Box>
                        {headers.map((header) => (
                            <Box
                                key={header}
                                borderLeftWidth="1px"
                                borderColor="gray.200"
                                p={0}
                            >
                                <Input
                                    value={row[header]?.toString() || ''}
                                    onChange={e => updateCell(row.id, header, e.target.value)}
                                    size="md"
                                    variant="flushed"
                                    px={2}
                                    py={1}
                                    height="36px"
                                    borderRadius={0}
                                    width="100%"
                                    border="none"
                                    _focus={{
                                        bg: "blue.50",
                                        outline: "2px solid",
                                        outlineColor: "blue.500",
                                        outlineOffset: "-2px",
                                        borderColor: "transparent"
                                    }}
                                    _hover={{
                                        bg: "gray.50"
                                    }}
                                />
                            </Box>
                        ))}
                    </Box>
                ))}
            </Box>
        </Box>
    );
}

export default GridTable;
