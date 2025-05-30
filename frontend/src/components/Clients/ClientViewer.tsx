import { type ClientPublic } from "@/client";
import DocumentViewer from "@/components/Common/DocumentViewer";
import TableViewer from "@/components/Common/TableViewer";
import { Field } from "@/components/ui/field";
import {
    Box,
    Button,
    Grid,
    Input,
    Text,
    VStack
} from "@chakra-ui/react";
import { useState } from "react";

interface ClientViewerProps {
    client: ClientPublic | any; // Allow both ClientPublic and the create proposal format
    onClientChange: (client: any) => void;
    onSubmit: () => void;
    onCancel?: () => void;
    isSubmitting?: boolean;
    submitButtonText?: string;
    cancelButtonText?: string;
    mode?: 'create' | 'edit'; // New mode prop
}

const ClientViewer = ({
    client,
    onClientChange,
    onSubmit,
    onCancel,
    isSubmitting = false,
    submitButtonText = "Guardar",
    cancelButtonText = "Cancelar",
    mode = 'create',
}: ClientViewerProps) => {
    const [tableData, setTableData] = useState(client.content_processed || "");

    const handleFieldChange = (field: string, value: any) => {
        const updatedClient = { ...client, [field]: value };
        onClientChange(updatedClient);
    };

    const handleStructureDescriptionChange = (key: string, value: string) => {
        const updatedDescriptions = {
            ...client.structure_descriptions,
            [key]: value,
        };
        handleFieldChange('structure_descriptions', updatedDescriptions);
    };

    const handleTableDataChange = (csv: string) => {
        setTableData(csv);
        handleFieldChange('content_processed', csv);
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        onSubmit();
    };

    // Show document in create mode or if we have one in edit mode
    const showDocument = mode === 'create' || (mode === 'edit' && client.base_document);

    const documentSection = showDocument && client.base_document ? (
        <Box
            width="595px"
            display="flex"
            flexDirection="column"
            alignItems="center"
            minW="0"
            pr={2}
        >
            <Text fontWeight="bold" mb={2} alignSelf="flex-start">
                Documento Base
            </Text>
            <DocumentViewer base64Document={client.base_document} />
        </Box>
    ) : null;

    const formSection = (
        <Box maxH="80vh" overflow="auto" minW={0} width="100%">
            <Text fontWeight="bold" mb={2}>Información del Cliente</Text>
            <VStack gap={4} align="stretch">
                <Field
                    required
                    label="Nombre del Cliente"
                    invalid={false}
                    errorText={undefined}
                >
                    <Input
                        value={client.name || ""}
                        onChange={e => handleFieldChange('name', e.target.value)}
                        placeholder="Nombre del cliente"
                        readOnly={mode === 'edit'}
                        variant={mode === 'edit' ? 'subtle' : 'outline'}
                    />
                </Field>
                <Field
                    required
                    label="Clasificador"
                    invalid={false}
                    errorText={undefined}
                >
                    <Input
                        value={client.clasifier || ""}
                        onChange={e => handleFieldChange('clasifier', e.target.value)}
                        placeholder="Clasificador"
                    />
                </Field>
                {client.structure_descriptions && Object.keys(client.structure_descriptions).length > 0 && (
                    <Field
                        required
                        label="Descripciones de las Columnas"
                        invalid={false}
                        errorText={undefined}
                    >
                        <Box width="100%">
                            <table style={{ width: "100%" }}>
                                <tbody>
                                    {Object.entries(client.structure_descriptions).map(([key, value]) => (
                                        <tr key={key}>
                                            <td style={{
                                                width: "260px",
                                                fontWeight: 500,
                                                verticalAlign: "middle",
                                                paddingRight: 10,
                                                whiteSpace: "nowrap"
                                            }}>
                                                {key}
                                            </td>
                                            <td style={{ width: "100%" }}>
                                                <Input
                                                    value={value as string || ""}
                                                    onChange={e => handleStructureDescriptionChange(key, e.target.value)}
                                                    placeholder={`Descripción para ${key}`}
                                                    size="sm"
                                                    variant="outline"
                                                    width="100%"
                                                />
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </Box>
                    </Field>
                )}
                {client.content_processed && (
                    <Field
                        required
                        label="Tabla de Extracción"
                        invalid={false}
                        errorText={undefined}
                    >
                        <TableViewer
                            inputData={tableData}
                            onDataChange={handleTableDataChange}
                            readOnly={false}
                            allowRowEdit={true}
                        />
                    </Field>
                )}
            </VStack>
        </Box>
    );

    return (
        <form onSubmit={handleSubmit}>
            {documentSection && formSection ? (
                <Grid templateColumns="auto 1fr" gap={8} alignItems="flex-start">
                    {documentSection}
                    {formSection}
                </Grid>
            ) : (
                formSection
            )}
            <Box mt={6} display="flex" gap={2} justifyContent="flex-end">
                {onCancel && (
                    <Button
                        variant="subtle"
                        colorPalette="gray"
                        onClick={onCancel}
                        disabled={isSubmitting}
                    >
                        {cancelButtonText}
                    </Button>
                )}
                <Button
                    variant="solid"
                    type="submit"
                    loading={isSubmitting}
                    loadingText="Procesando..."
                    colorScheme="green"
                >
                    {submitButtonText}
                </Button>
            </Box>
        </form>
    );
};

export default ClientViewer;
