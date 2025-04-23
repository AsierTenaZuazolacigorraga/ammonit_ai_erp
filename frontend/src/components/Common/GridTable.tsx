import { Box, Button, Flex, Input } from '@chakra-ui/react';
import { useEffect, useMemo, useState } from 'react';
import { FiPlus, FiTrash2 } from 'react-icons/fi';

type Row = {
    [key: string]: string | number;
    id: number;
};

interface GridTableProps {
    inputData: string;
    onDataChange?: (csvData: string) => void;
    readOnly?: boolean;
}

function GridTable({ inputData, onDataChange, readOnly = false }: GridTableProps) {
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

    // Convert rows to CSV string
    const convertToCSV = (rows: Row[], headers: string[]): string => {
        if (rows.length === 0) return headers.join(';');

        const headerRow = headers.join(';');
        const dataRows = rows.map(row =>
            headers.map(header => row[header]?.toString() || '').join(';')
        );

        return [headerRow, ...dataRows].join('\n');
    };

    // Call onDataChange whenever rows change
    useEffect(() => {
        if (onDataChange) {
            const csvData = convertToCSV(rows, headers);
            onDataChange(csvData);
        }
    }, [rows, headers, onDataChange]);

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
            borderWidth="1px"
            borderColor="gray.200"
            borderRadius="md"
            overflow="auto"
        >
            <table style={{
                width: '100%',
                borderCollapse: 'collapse',
                tableLayout: 'fixed'
            }}>
                <thead>
                    <tr>
                        {!readOnly && (
                            <th
                                style={{
                                    padding: '8px',
                                    borderBottom: '2px solid #E2E8F0',
                                    borderRight: '1px solid #E2E8F0',
                                    backgroundColor: '#F7FAFC',
                                    textAlign: 'center',
                                    width: readOnly ? '0' : '100px'
                                }}
                            >
                                Acciones
                            </th>
                        )}
                        {headers.map((header, index) => (
                            <th
                                key={header}
                                style={{
                                    padding: '8px',
                                    borderBottom: '2px solid #E2E8F0',
                                    borderRight: index < headers.length - 1 ? '1px solid #E2E8F0' : 'none',
                                    backgroundColor: '#F7FAFC',
                                    textAlign: 'left'
                                }}
                            >
                                {header}
                            </th>
                        ))}
                    </tr>
                </thead>
                <tbody>
                    {rows.length === 0 && (
                        <tr>
                            {!readOnly && (
                                <td
                                    style={{
                                        padding: '8px',
                                        borderBottom: '1px solid #E2E8F0',
                                        borderRight: '1px solid #E2E8F0',
                                        textAlign: 'center'
                                    }}
                                >
                                    <Button
                                        size="sm"
                                        colorScheme="blue"
                                        variant="ghost"
                                        onClick={() => addRow()}
                                    >
                                        <FiPlus />
                                    </Button>
                                </td>
                            )}
                            {headers.map((header, index) => (
                                <td
                                    key={header}
                                    style={{
                                        padding: '8px',
                                        borderBottom: '1px solid #E2E8F0',
                                        borderRight: index < headers.length - 1 ? '1px solid #E2E8F0' : 'none'
                                    }}
                                />
                            ))}
                        </tr>
                    )}
                    {rows.map((row) => (
                        <tr key={row.id}>
                            {!readOnly && (
                                <td
                                    style={{
                                        padding: '4px',
                                        borderBottom: '1px solid #E2E8F0',
                                        borderRight: '1px solid #E2E8F0',
                                        textAlign: 'center'
                                    }}
                                >
                                    <Flex justifyContent="center" gap="4px">
                                        <Button
                                            size="sm"
                                            colorScheme="red"
                                            variant="ghost"
                                            onClick={() => deleteRow(row.id)}
                                        >
                                            <FiTrash2 />
                                        </Button>
                                        <Button
                                            size="sm"
                                            colorScheme="blue"
                                            variant="ghost"
                                            onClick={() => addRow(row.id)}
                                        >
                                            <FiPlus />
                                        </Button>
                                    </Flex>
                                </td>
                            )}
                            {headers.map((header, index) => (
                                <td
                                    key={header}
                                    style={{
                                        padding: '2px',
                                        borderBottom: '1px solid #E2E8F0',
                                        borderRight: index < headers.length - 1 ? '1px solid #E2E8F0' : 'none'
                                    }}
                                >
                                    <Input
                                        value={row[header]?.toString() || ''}
                                        onChange={e => updateCell(row.id, header, e.target.value)}
                                        size="sm"
                                        variant="outline"
                                        border="none"
                                        paddingX="6px"
                                        height="32px"
                                        width="100%"
                                        readOnly={readOnly}
                                        _focus={{
                                            bg: "blue.50",
                                        }}
                                    />
                                </td>
                            ))}
                        </tr>
                    ))}
                </tbody>
            </table>
        </Box>
    );
}

export default GridTable;
