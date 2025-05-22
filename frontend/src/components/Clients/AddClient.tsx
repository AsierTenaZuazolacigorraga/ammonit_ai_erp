import { ClientsService } from "@/client";
import type { ApiError } from "@/client/core/ApiError";
import DocumentViewer from "@/components/Common/DocumentViewer";
import TableViewer from "@/components/Common/TableViewer";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import {
    Box,
    Button,
    DialogActionTrigger,
    DialogTitle,
    Grid,
    Input,
    Text,
    VStack
} from "@chakra-ui/react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useDropzone } from "react-dropzone";
import { useForm } from "react-hook-form";
import { FaPlus } from "react-icons/fa";
import {
    DialogBody,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogRoot,
    DialogTrigger,
} from "../ui/dialog";
import { Field } from "../ui/field";

// Step 1: Enter name & upload PDF
interface AddClientFormData {
    name: string;
    base_document: File | null;
    base_document_name: string | null;
}

// Step 2: Proposal editing
interface ProposalEditData {
    name: string;
    clasifier: string;
    base_markdown: string;
    content_processed: string;
}

const AddClient = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [step, setStep] = useState<1 | 2>(1);
    const [pdfFile, setPdfFile] = useState<File | null>(null);
    const [pdfBase64, setPdfBase64] = useState<string>("");
    const [proposal, setProposal] = useState<ProposalEditData | null>(null);
    const [tableData, setTableData] = useState<string>("");
    const [isLoadingProposal, setIsLoadingProposal] = useState(false);
    const queryClient = useQueryClient();
    const { showSuccessToast } = useCustomToast();

    // Step 1 form
    const {
        register,
        handleSubmit,
        setValue,
        watch,
        reset,
        formState: { errors, isSubmitting },
    } = useForm<AddClientFormData>({
        mode: "onBlur",
        criteriaMode: "all",
        defaultValues: {
            name: "",
            base_document: null,
            base_document_name: null,
        },
    });
    const currentFileName = watch("base_document_name");

    // Step 2 form (proposal edit)
    const [editState, setEditState] = useState<ProposalEditData | null>(null);

    // Dropzone logic (from AddOrder)
    const onDrop = (acceptedFiles: File[]) => {
        const file = acceptedFiles[0];
        if (file) {
            setValue("base_document_name", file.name, { shouldValidate: true });
            setValue("base_document", file, { shouldValidate: true });
            setPdfFile(file);
            // Convert to base64 for DocumentViewer
            const reader = new FileReader();
            reader.onload = (e) => {
                setPdfBase64((e.target?.result as string) || "");
            };
            reader.readAsDataURL(file);
        }
    };
    const { getRootProps, getInputProps } = useDropzone({
        onDrop,
        accept: { "application/pdf": [".pdf"] },
        maxFiles: 1,
        maxSize: 5 * 1024 * 1024,
        disabled: isSubmitting || isLoadingProposal,
    });

    // Step 1: Continue → get proposal
    const handleContinue = async (data: AddClientFormData) => {
        if (!pdfFile) return;
        setIsLoadingProposal(true);
        try {
            const proposal = await ClientsService.getClientProposal({
                formData: { base_document: pdfFile },
            });
            setProposal({
                name: data.name,
                clasifier: proposal.clasifier,
                base_markdown: proposal.base_markdown,
                content_processed: proposal.content_processed,
            });
            setEditState({
                name: data.name,
                clasifier: proposal.clasifier,
                base_markdown: proposal.base_markdown,
                content_processed: proposal.content_processed,
            });
            setTableData(proposal.content_processed);
            setStep(2);
        } catch (err) {
            handleError(err as ApiError);
        } finally {
            setIsLoadingProposal(false);
        }
    };

    // Save client mutation
    const mutation = useMutation({
        mutationFn: (data: ProposalEditData) =>
            ClientsService.createClient({
                requestBody: {
                    name: data.name,
                    clasifier: data.clasifier,
                    base_markdown: data.base_markdown,
                    content_processed: data.content_processed,
                },
            }),
        onSuccess: () => {
            showSuccessToast("Cliente guardado correctamente.");
            reset();
            setStep(1);
            setIsOpen(false);
            setPdfFile(null);
            setPdfBase64("");
            setProposal(null);
            setEditState(null);
            setTableData("");
        },
        onError: (err: ApiError) => {
            handleError(err);
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["clients"] });
        },
    });

    // TableViewer data change
    const handleTableDataChange = (csv: string) => {
        setTableData(csv);
        if (editState) setEditState({ ...editState, content_processed: csv });
    };

    // Reset dialog state on close
    const handleDialogChange = ({ open }: { open: boolean }) => {
        setIsOpen(open);
        if (!open) {
            setStep(1);
            setPdfFile(null);
            setPdfBase64("");
            setProposal(null);
            setEditState(null);
            setTableData("");
            reset();
        }
    };

    return (
        <DialogRoot
            size={{ base: "xs", md: step === 2 ? "xl" : "md" }}
            placement="center"
            open={isOpen}
            onOpenChange={handleDialogChange}
        >
            <DialogTrigger asChild>
                <Button value="add-client" my={4}>
                    <FaPlus fontSize="16px" /> Añadir Cliente
                </Button>
            </DialogTrigger>
            <DialogContent maxW={step === 2 ? "95vw" : undefined}>
                {step === 1 && (
                    <form onSubmit={handleSubmit(handleContinue)}>
                        <DialogHeader>
                            <DialogTitle>Añadir Cliente</DialogTitle>
                        </DialogHeader>
                        <DialogBody>
                            <VStack gap={4}>
                                <Field
                                    required
                                    label="Nombre del Cliente"
                                    invalid={!!errors.name}
                                    errorText={errors.name?.message}
                                >
                                    <Input
                                        {...register("name", { required: "El nombre es requerido" })}
                                        placeholder="Nombre del cliente"
                                    />
                                </Field>
                                <Field
                                    required
                                    label="Documento de ejemplo (.pdf)"
                                    invalid={!!errors.base_document_name || !!errors.base_document}
                                    errorText={
                                        errors.base_document_name?.message || errors.base_document?.message
                                    }
                                >
                                    <div
                                        {...getRootProps()}
                                        style={{
                                            border: "2px dashed #ccc",
                                            padding: "10px",
                                            textAlign: "center",
                                            backgroundColor: isSubmitting || isLoadingProposal ? "#f5f5f5" : "transparent",
                                            opacity: isSubmitting || isLoadingProposal ? 0.5 : 1,
                                            cursor: isSubmitting || isLoadingProposal ? "not-allowed" : "pointer",
                                        }}
                                    >
                                        <input {...getInputProps()} />
                                        <p>Arrastra y suelta el archivo aquí o haz clic para seleccionar uno (.pdf hasta 5MB)</p>
                                    </div>
                                    <Input
                                        {...register("base_document_name", {
                                            required: "Se requiere el documento.",
                                        })}
                                        placeholder="Nombre del documento"
                                        value={currentFileName || ""}
                                        type="text"
                                        readOnly
                                        variant="subtle"
                                        mt={2}
                                    />
                                </Field>
                            </VStack>
                        </DialogBody>
                        <DialogFooter gap={2}>
                            <DialogActionTrigger asChild>
                                <Button variant="subtle" colorPalette="gray" disabled={isSubmitting || isLoadingProposal}>
                                    Cancelar
                                </Button>
                            </DialogActionTrigger>
                            <Button
                                variant="solid"
                                type="submit"
                                loading={isSubmitting || isLoadingProposal}
                                loadingText="Procesando..."
                                disabled={isLoadingProposal}
                            >
                                Continuar
                            </Button>
                        </DialogFooter>
                    </form>
                )}
                {step === 2 && proposal && editState && (
                    <form
                        onSubmit={e => {
                            e.preventDefault();
                            mutation.mutate({ ...editState, content_processed: tableData });
                        }}
                    >
                        <DialogHeader>
                            <DialogTitle>Revisar y Guardar Cliente</DialogTitle>
                        </DialogHeader>
                        <DialogBody>
                            <Grid templateColumns="auto 1fr" gap={8} alignItems="flex-start">
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
                                    <DocumentViewer base64Document={pdfBase64} />
                                </Box>
                                <Box maxH="80vh" overflow="auto" minW={0} width="100%">
                                    <VStack gap={4} align="stretch">
                                        <Field
                                            required
                                            label="Clasificador"
                                            invalid={false}
                                            errorText={undefined}
                                        >
                                            <Input
                                                value={editState.clasifier}
                                                onChange={e =>
                                                    setEditState({ ...editState, clasifier: e.target.value })
                                                }
                                                placeholder="Clasificador propuesto"
                                            />
                                        </Field>
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
                                                allowColumnEdit={false}
                                            />
                                        </Field>
                                    </VStack>
                                </Box>
                            </Grid>
                        </DialogBody>
                        <DialogFooter gap={2}>
                            <Button
                                variant="subtle"
                                colorPalette="gray"
                                onClick={() => setStep(1)}
                                disabled={mutation.isPending}
                            >
                                Volver
                            </Button>
                            <Button
                                variant="solid"
                                type="submit"
                                loading={mutation.isPending}
                                loadingText="Guardando..."
                                colorScheme="green"
                            >
                                Guardar
                            </Button>
                        </DialogFooter>
                    </form>
                )}
            </DialogContent>
        </DialogRoot>
    );
};

export default AddClient;
