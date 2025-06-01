import { ClientsService } from "@/client";
import type { ApiError } from "@/client/core/ApiError";
import ClientViewer from "@/components/Clients/ClientViewer";
import DropZone from "@/components/Common/DropZone";
import {
    DialogBody,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogRoot,
    DialogTrigger,
} from "@/components/ui/dialog";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import {
    Button,
    DialogActionTrigger,
    DialogTitle,
    VStack
} from "@chakra-ui/react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { useForm } from "react-hook-form";
import { FaPlus } from "react-icons/fa";

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
    structure_descriptions: Record<string, string>;
    structure: any;
}

const AddClient = () => {
    const [isOpen, setIsOpen] = useState(false);
    const [step, setStep] = useState<'form' | 'proposal'>("form");
    const [pdfFile, setPdfFile] = useState<File | null>(null);
    const [proposal, setProposal] = useState<ProposalEditData | null>(null);
    const [isLoadingProposal, setIsLoadingProposal] = useState(false);
    const queryClient = useQueryClient();
    const { showSuccessToast } = useCustomToast();

    // Step 1 form
    const {
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

    // Dropzone logic
    const handleFileDrop = (file: File) => {
        setValue("base_document_name", file.name, { shouldValidate: true });
        setValue("base_document", file, { shouldValidate: true });
        setPdfFile(file);
    };

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
                structure_descriptions: (proposal as any).structure_descriptions ?? {},
                structure: (proposal as any).structure,
            });
            setStep("proposal");
        } catch (err) {
            handleError(err as ApiError);
        } finally {
            setIsLoadingProposal(false);
        }
    };

    // Save client mutation
    const mutation = useMutation({
        mutationFn: async (data: ProposalEditData & { structure: any }) => {
            // Convert PDF file to base64 for JSON transport (create endpoint expects JSON, not multipart)
            let fileBase64: string | null = null;
            if (pdfFile) {
                // Use FileReader API for robust base64 conversion - handles large files efficiently
                fileBase64 = await new Promise<string>((resolve, reject) => {
                    const reader = new FileReader();
                    reader.onload = () => {
                        const result = reader.result as string;
                        // Remove the data URL prefix (data:application/pdf;base64,)
                        const base64 = result.split(',')[1];
                        resolve(base64);
                    };
                    reader.onerror = () => reject(new Error('Failed to read file'));
                    reader.readAsDataURL(pdfFile);
                });
            }

            // Create JSON payload with base64 encoded file
            const createData = {
                name: data.name,
                clasifier: data.clasifier,
                base_document_markdown: data.base_document_markdown,
                content_processed: data.content_processed,
                structure: data.structure,
                base_document: fileBase64, // Send as base64 string for JSON transport
                base_document_name: data.base_document_name,
                structure_descriptions: data.structure_descriptions,
            };

            return ClientsService.createClient({
                requestBody: createData as any, // Type assertion to bypass incorrect auto-generated types
            });
        },
        onSuccess: () => {
            showSuccessToast("Cliente guardado correctamente.");
            reset();
            setStep("form");
            setIsOpen(false);
            setPdfFile(null);
            setProposal(null);
        },
        onError: (err: ApiError) => {
            handleError(err);
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["clients"] });
        },
    });

    // Reset dialog state on close
    const handleDialogChange = ({ open }: { open: boolean }) => {
        setIsOpen(open);
        if (!open) {
            setStep("form");
            setPdfFile(null);
            setProposal(null);
            reset();
        }
    };

    const handleProposalChange = (updatedClient: any) => {
        // Convert back from ClientViewer format to ProposalEditData format
        const updatedProposal: ProposalEditData = {
            ...updatedClient,
            base_document_name: updatedClient.base_document_name || null,
        };
        setProposal(updatedProposal);
    };

    const handleProposalSubmit = () => {
        if (proposal) {
            mutation.mutate({
                ...proposal,
                structure: proposal.structure,
                structure_descriptions: proposal.structure_descriptions,
            });
        }
    };

    // Transform proposal to match ClientViewer's expected format
    const getProposalForViewer = (proposal: ProposalEditData) => ({
        name: proposal.name,
        clasifier: proposal.clasifier,
        base_document_markdown: proposal.base_document_markdown,
        content_processed: proposal.content_processed,
        base_document: proposal.base_document,
        base_document_name: proposal.base_document_name || undefined,
        structure_descriptions: proposal.structure_descriptions,
        structure: proposal.structure,
    });

    let content = null;
    if (step === "form") {
        content = (
            <form onSubmit={handleSubmit(handleContinue)}>
                <DialogHeader>
                    <DialogTitle>Añadir Cliente</DialogTitle>
                </DialogHeader>
                <DialogBody>
                    <VStack gap={4}>
                        <DropZone
                            onFileDrop={handleFileDrop}
                            fileName={currentFileName}
                            isDisabled={isSubmitting || isLoadingProposal}
                            error={errors.base_document_name?.message || errors.base_document?.message}
                        />
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
    } else if (step === "proposal" && proposal) {
        content = (
            <>
                <DialogHeader>
                    <DialogTitle>Revisar y Guardar Cliente</DialogTitle>
                </DialogHeader>
                <DialogBody>
                    <ClientViewer
                        client={getProposalForViewer(proposal)}
                        onClientChange={handleProposalChange}
                        onSubmit={handleProposalSubmit}
                        onCancel={() => setStep("form")}
                        isSubmitting={mutation.isPending}
                        submitButtonText="Guardar"
                        cancelButtonText="Volver"
                        mode="create"
                    />
                </DialogBody>
            </>
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
