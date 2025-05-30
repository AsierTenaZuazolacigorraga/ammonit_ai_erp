import { useMutation, useQueryClient } from "@tanstack/react-query"

import {
    Button,
    DialogTitle,
} from "@chakra-ui/react"
import { useState } from "react"

import { type ClientPublic, ClientsService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import { FiEdit2 } from "react-icons/fi"
import {
    DialogBody,
    DialogContent,
    DialogHeader,
    DialogRoot,
    DialogTrigger
} from "../ui/dialog"
import ClientViewer from "./ClientViewer"

interface EditClientProps {
    client: ClientPublic
}

const EditClient = ({ client }: EditClientProps) => {
    const [isOpen, setIsOpen] = useState(false)
    const [editingClient, setEditingClient] = useState<ClientPublic>(client)
    const queryClient = useQueryClient()
    const { showSuccessToast } = useCustomToast()

    const mutation = useMutation({
        mutationFn: (data: ClientPublic) =>
            ClientsService.updateClient({ id: client.id, requestBody: data }),
        onSuccess: () => {
            showSuccessToast("Cliente actualizado correctamente.")
            setIsOpen(false)
        },
        onError: (err: ApiError) => {
            handleError(err)
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["clients"] })
        },
    })

    const handleClientChange = (updatedClient: any) => {
        setEditingClient(updatedClient)
    }

    const handleSubmit = () => {
        mutation.mutate(editingClient)
    }

    const handleDialogChange = ({ open }: { open: boolean }) => {
        setIsOpen(open)
        if (open) {
            // Reset editing state when opening
            setEditingClient(client)
        }
    }

    // Transform ClientPublic to match ClientViewer's expected format
    const clientForViewer = {
        name: editingClient.name || "",
        clasifier: editingClient.clasifier || "",
        base_document_markdown: editingClient.base_document_markdown || "",
        content_processed: editingClient.content_processed || "",
        base_document: editingClient.base_document,
        base_document_name: editingClient.base_document_name,
        structure_descriptions: editingClient.structure_descriptions || {},
        structure: editingClient.structure || {},
    }

    return (
        <DialogRoot
            size={{ base: "xs", md: "xl" }}
            placement="center"
            open={isOpen}
            onOpenChange={handleDialogChange}
        >
            <DialogTrigger asChild>
                <Button variant="ghost" size="sm">
                    <FiEdit2 fontSize="16px" />
                </Button>
            </DialogTrigger>
            <DialogContent maxW="95vw">
                <DialogHeader>
                    <DialogTitle>Editar Cliente</DialogTitle>
                </DialogHeader>
                <DialogBody>
                    <ClientViewer
                        client={clientForViewer}
                        onClientChange={handleClientChange}
                        onSubmit={handleSubmit}
                        onCancel={() => setIsOpen(false)}
                        isSubmitting={mutation.isPending}
                        submitButtonText="Actualizar"
                        cancelButtonText="Cancelar"
                        showDocument={!!client.base_document}
                    />
                </DialogBody>
            </DialogContent>
        </DialogRoot>
    )
}

export default EditClient 