import { Box, Button, HStack } from '@chakra-ui/react';
import { DataGrid, GridColDef, GridRenderCellParams, GridRowsProp, useGridApiRef } from '@mui/x-data-grid';
import * as React from 'react';
import { FiTrash2 } from 'react-icons/fi';

// CSV utilities
function parseCSV(csv: string): { columns: GridColDef[]; rows: any[] } {
    const lines = csv.trim().split(/\r?\n/).filter(Boolean);
    if (lines.length === 0) return { columns: [], rows: [] };
    const headers = lines[0].split(';');
    const columns: GridColDef[] = headers.map((h, _) => ({
        field: h,
        headerName: h,
        width: 150,
        editable: true,
        sortable: false,
        disableColumnMenu: true
    }));
    const rows = lines.slice(1).map((line, idx) => {
        const values = line.split(';');
        const row: any = { id: idx + 1 };
        headers.forEach((h, i) => { row[h] = values[i] ?? ''; });
        return row;
    });
    return { columns, rows };
}

function toCSV(columns: GridColDef[], rows: any[]): string {
    if (!columns.length) return '';
    const headers = columns.map(c => c.headerName || c.field);
    const headerRow = headers.join(';');
    const dataRows = rows.map(row => columns.map(c => row[c.field] ?? '').join(';'));
    return [headerRow, ...dataRows].join('\n');
}

interface TableViewerProps {
    inputData?: string;
    onDataChange?: (csv: string) => void;
    readOnly?: boolean;
    allowRowEdit?: boolean;
}

const TableViewer: React.FC<TableViewerProps> = ({
    inputData = '',
    onDataChange,
    readOnly = false,
    allowRowEdit = true
}) => {
    // State
    const [columns, setColumns] = React.useState<GridColDef[]>([]);
    const [rows, setRows] = React.useState<GridRowsProp>([]);
    const apiRef = useGridApiRef();

    // Parse CSV on mount or inputData change
    React.useEffect(() => {
        if (inputData) {
            const { columns: parsedCols, rows: parsedRows } = parseCSV(inputData);
            // Always add id field (hidden)
            setColumns(parsedCols.map((col, _) => ({ ...col, editable: !readOnly && allowRowEdit, hide: col.field === 'id' })));
            setRows(parsedRows);
        }
    }, [inputData, readOnly, allowRowEdit]);

    // Call onDataChange on any data change
    React.useEffect(() => {
        if (onDataChange && columns.length && rows.length) {
            onDataChange(toCSV(columns.filter(c => c.field !== 'actions'), [...rows]));
        }
        // eslint-disable-next-line
    }, [columns, rows]);

    // Add a new row
    const handleAddRow = () => {
        const newId = Math.max(0, ...rows.map(r => Number(r.id))) + 1;
        const newRow: any = { id: newId };
        columns.forEach(col => {
            if (col.field !== 'actions') newRow[col.field] = '';
        });
        setRows(prev => [...prev, newRow]);
    };

    // Delete a row
    const handleDeleteRow = (id: number) => {
        setRows(prev => prev.filter(row => row.id !== id));
    };

    // Compose columns: leftmost delete, then data columns
    const gridColumns: GridColDef[] = [
        !readOnly && allowRowEdit ? {
            field: 'actions',
            headerName: '',
            width: 60,
            sortable: false,
            filterable: false,
            disableColumnMenu: true,
            editable: false,
            renderCell: (params: GridRenderCellParams) => (
                <Button
                    variant="ghost"
                    size="sm"
                    colorPalette="red"
                    onClick={() => handleDeleteRow(params.row.id)}
                >
                    <FiTrash2 fontSize="16px" />
                </Button>
            )
        } : undefined,
        ...columns.map(col => ({
            ...col,
            editable: !readOnly && allowRowEdit,
            sortable: false,
            disableColumnMenu: true,
        }))
    ].filter(Boolean) as GridColDef[];

    // Row editing
    const processRowUpdate = (newRow: any) => {
        setRows(prevRows => prevRows.map(row => row.id === newRow.id ? newRow : row));
        return newRow;
    };

    return (
        <Box>
            {!readOnly && (
                <HStack mb={2} gap={2}>
                    {allowRowEdit && <Button size="sm" colorScheme="blue" onClick={handleAddRow}>Nueva Fila</Button>}
                </HStack>
            )}
            <div style={{ height: 400, width: '100%' }}>
                <DataGrid
                    apiRef={apiRef}
                    rows={rows}
                    columns={gridColumns}
                    processRowUpdate={processRowUpdate}
                    getRowId={(row) => row.id}
                    disableRowSelectionOnClick
                    isCellEditable={(_) => !readOnly && allowRowEdit}
                />
            </div>
        </Box>
    );
};

export default TableViewer;