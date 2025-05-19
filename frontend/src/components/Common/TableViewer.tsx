import { Box, Button, HStack, Input } from '@chakra-ui/react';
import { DataGrid, GridColDef, GridRenderCellParams, GridRowsProp } from '@mui/x-data-grid';
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
    const headers = columns.map(c => c.field);
    const headerRow = headers.join(';');
    const dataRows = rows.map(row => headers.map(h => row[h] ?? '').join(';'));
    return [headerRow, ...dataRows].join('\n');
}

interface TableViewerProps {
    inputData?: string;
    onDataChange?: (csv: string) => void;
    readOnly?: boolean;
    allowColumnEdit?: boolean;
    allowRowEdit?: boolean;
}

const TableViewer: React.FC<TableViewerProps> = ({
    inputData = '',
    onDataChange,
    readOnly = false,
    allowColumnEdit = false,
    allowRowEdit = true
}) => {
    // State
    const [columns, setColumns] = React.useState<GridColDef[]>([]);
    const [rows, setRows] = React.useState<GridRowsProp>([]);
    const [renamingCol, setRenamingCol] = React.useState<string | null>(null);
    const [renameValue, setRenameValue] = React.useState('');
    const inputRef = React.useRef<HTMLInputElement>(null);

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

    React.useEffect(() => {
        if (renamingCol && inputRef.current) {
            inputRef.current.focus();
            inputRef.current.select();
        }
    }, [renamingCol]);

    // Add a new row
    const handleAddRow = () => {
        const newId = Math.max(0, ...rows.map(r => Number(r.id))) + 1;
        const newRow: any = { id: newId };
        columns.forEach(col => {
            if (col.field !== 'actions') newRow[col.field] = '';
        });
        setRows(prev => [...prev, newRow]);
    };

    // Add a new column
    const handleAddColumn = () => {
        let colNum = 1;
        let newField = `Col${colNum}`;
        while (columns.some(col => col.field === newField)) {
            colNum++;
            newField = `Col${colNum}`;
        }
        const newCol: GridColDef = {
            field: newField,
            headerName: newField,
            width: 120,
            editable: !readOnly && allowRowEdit,
            sortable: false,
            disableColumnMenu: true,
            renderHeader: (params) => renderHeaderWithDeleteAndRename(params, newField)
        };
        setColumns(prev => [...prev, newCol]);
        setRows(prevRows => prevRows.map(row => ({ ...row, [newField]: '' })));
    };

    // Delete a row
    const handleDeleteRow = (id: number) => {
        setRows(prev => prev.filter(row => row.id !== id));
    };

    // Delete a column
    const handleDeleteColumn = (field: string) => {
        setColumns(prev => prev.filter(col => col.field !== field));
        setRows(prevRows => prevRows.map(row => {
            const { [field]: _, ...rest } = row;
            return rest;
        }));
        if (renamingCol === field) {
            setRenamingCol(null);
            setRenameValue('');
        }
    };

    // Start renaming
    const startRenaming = (field: string, currentName: string) => {
        setRenamingCol(field);
        setRenameValue(currentName);
    };

    // Commit rename
    const commitRename = (field: string) => {
        if (!renameValue.trim()) return;
        setColumns(prevCols => prevCols.map(col =>
            col.field === field ? { ...col, headerName: renameValue } : col
        ));
        setRenamingCol(null);
        setRenameValue('');
    };

    // Render header with delete and rename
    const renderHeaderWithDeleteAndRename = (params: any, field: string) => (
        <Box display="flex" alignItems="center" gap={1}>
            {allowColumnEdit && renamingCol === field ? (
                <Input
                    ref={inputRef}
                    size="xs"
                    variant="flushed"
                    style={{ border: 'none', boxShadow: 'none', fontWeight: 500, fontSize: '1rem', padding: 0, minWidth: 0, maxWidth: 80, height: 'auto', background: 'transparent' }}
                    value={renameValue}
                    onChange={e => setRenameValue(e.target.value)}
                    onBlur={() => commitRename(field)}
                    onKeyDown={e => {
                        if (e.key === 'Enter') commitRename(field);
                        if (e.key === 'Escape') { setRenamingCol(null); setRenameValue(''); }
                    }}
                />
            ) : (
                <span
                    style={{ cursor: allowColumnEdit ? 'pointer' : 'default', fontWeight: 500 }}
                    onClick={() => allowColumnEdit && startRenaming(field, params.colDef.headerName)}
                >
                    {params.colDef.headerName}
                </span>
            )}
            {allowColumnEdit && (
                <Button
                    variant="ghost"
                    size="xs"
                    colorPalette="red"
                    ml={1}
                    onClick={() => handleDeleteColumn(field)}
                >
                    <FiTrash2 fontSize="14px" />
                </Button>
            )}
        </Box>
    );

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
            renderHeader: (params: any) => renderHeaderWithDeleteAndRename(params, col.field)
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
                    {allowColumnEdit && <Button size="sm" colorScheme="blue" onClick={handleAddColumn}>Nueva Columna</Button>}
                </HStack>
            )}
            <div style={{ height: 400, width: '100%' }}>
                <DataGrid
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