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
    base_document_markdown: string;
    content_processed: string;
    base_document?: any;
    base_document_name?: string | null;
}

const AddClient = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [step, setStep] = useState<'form' | 'proposal'>("form");
    const [pdfFile, setPdfFile] = useState<File | null>(null);
    const [_, setPdfBase64] = useState<string>("");
    const [apiBase64, setApiBase64] = useState<string>("");
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
            base_document: null,
            base_document_name: null,
        },
    });
    const currentFileName = watch("base_document_name");

    // Step 2 form (proposal edit)
    const [editState, setEditState] = useState<ProposalEditData | null>(null);

    // Dropzone logic
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
    const handleContinue = async (_: AddClientFormData) => {
        if (!pdfFile) return;
        setIsLoadingProposal(true);
        try {
            const proposal = await ClientsService.getClientProposal({
                formData: { base_document: pdfFile },
            });
            setProposal({
                name: proposal.name ?? "",
                clasifier: proposal.clasifier ?? "",
                base_document_markdown: proposal.base_document_markdown ?? "",
                content_processed: proposal.content_processed ?? "",
                base_document: (proposal as any).base_document,
                base_document_name: (proposal as any).base_document_name,
            });
            setEditState({
                name: proposal.name ?? "",
                clasifier: proposal.clasifier ?? "",
                base_document_markdown: proposal.base_document_markdown ?? "",
                content_processed: proposal.content_processed ?? "",
                base_document: (proposal as any).base_document,
                base_document_name: (proposal as any).base_document_name,
            });
            setTableData(proposal.content_processed ?? "");
            setApiBase64((proposal as any).base_document || "");
            setStep("proposal");
        } catch (err) {
            handleError(err as ApiError);
        } finally {
            setIsLoadingProposal(false);
        }
    };

    // Save client mutation
    const mutation = useMutation({
        mutationFn: (data: ProposalEditData & { structure: any }) =>
            ClientsService.createClient({
                requestBody: {
                    name: data.name,
                    clasifier: data.clasifier,
                    base_document_markdown: data.base_document_markdown,
                    content_processed: data.content_processed,
                    structure: data.structure,
                    base_document: data.base_document,
                    base_document_name: data.base_document_name,
                    // additional_info and other fields can be added if needed
                },
            }),
        onSuccess: () => {
            showSuccessToast("Cliente guardado correctamente.");
            reset();
            setStep("form");
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
            setStep("form");
            setPdfFile(null);
            setPdfBase64("");
            setProposal(null);
            setEditState(null);
            setTableData("");
            reset();
        }
    };

    let content = null;
    if (step === "form") {
        content = (
            <form onSubmit={handleSubmit(handleContinue)}>
                <DialogHeader>
                    <DialogTitle>Añadir Cliente</DialogTitle>
                </DialogHeader>
                <DialogBody>
                    <VStack gap={4}>
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
                                    border: "2.5px dashed #319795",
                                    borderRadius: "12px",
                                    boxShadow: "0 2px 8px rgba(49, 151, 149, 0.08)",
                                    padding: "18px 10px",
                                    textAlign: "center",
                                    backgroundColor: isSubmitting || isLoadingProposal ? "#f5f5f5" : "#f9fafb",
                                    opacity: isSubmitting || isLoadingProposal ? 0.5 : 1,
                                    cursor: isSubmitting || isLoadingProposal ? "not-allowed" : "pointer",
                                    transition: "border-color 0.2s, box-shadow 0.2s, background 0.2s",
                                }}
                                onMouseEnter={e => {
                                    if (!(isSubmitting || isLoadingProposal)) e.currentTarget.style.borderColor = '#2b6cb0';
                                }}
                                onMouseLeave={e => {
                                    if (!(isSubmitting || isLoadingProposal)) e.currentTarget.style.borderColor = '#319795';
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
        );
    } else if (step === "proposal" && proposal && editState) {
        content = (
            <form
                onSubmit={e => {
                    e.preventDefault();
                    mutation.mutate({ ...editState, content_processed: tableData, structure: (proposal as any).structure ?? {} });
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
                            <DocumentViewer base64Document={apiBase64} />
                        </Box>
                        <Box maxH="80vh" overflow="auto" minW={0} width="100%">
                            <VStack gap={4} align="stretch">
                                <Field
                                    required
                                    label="Nombre del Cliente"
                                    invalid={false}
                                    errorText={undefined}
                                >
                                    <Input
                                        value={editState.name}
                                        onChange={e => setEditState({ ...editState, name: e.target.value })}
                                        placeholder="Nombre del cliente"
                                    />
                                </Field>
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
                        onClick={() => setStep("form")}
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
        );
    }

    return (
        <DialogRoot
            size={{ base: "xs", md: step === "proposal" ? "xl" : "md" }}
            placement="center"
            open={isOpen}
            onOpenChange={handleDialogChange}
        >
            <DialogTrigger asChild>
                <Button value="add-client" my={4}>
                    <FaPlus fontSize="16px" /> Añadir Cliente
                </Button>
            </DialogTrigger>
            <DialogContent maxW={step === "proposal" ? "95vw" : undefined}>
                {content}
            </DialogContent>
        </DialogRoot>
    );
};

export default AddClient;
