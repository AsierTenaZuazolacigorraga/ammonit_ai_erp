import { useMutation, useQueryClient } from "@tanstack/react-query"

import {
    Button,
    DialogTitle,
} from "@chakra-ui/react"
import { useState } from "react"

import { type ClientPublic, ClientsService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import ClientViewer from "@/components/Clients/ClientViewer"
import {
    DialogBody,
    DialogContent,
    DialogHeader,
    DialogRoot,
    DialogTrigger
} from "@/components/ui/dialog"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import { FiEdit2 } from "react-icons/fi"

interface EditClientProps {
    client: ClientPublic
}

const EditClient = ({ client }: EditClientProps) => {
    const [isOpen, setIsOpen] = useState(false)
    const [editingClient, setEditingClient] = useState<ClientPublic>(client)
    const queryClient = useQueryClient()
    const { showSuccessToast } = useCustomToast()

    const mutation = useMutation({
        mutationFn: (data: ClientPublic) => {
            // Exclude document fields for updates
            const { base_document, base_document_name, ...updateData } = data

            return ClientsService.updateClient({
                id: client.id,
                requestBody: updateData as any
            })
        },
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
            setEditingClient(client)
        }
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
                        client={editingClient}
                        onClientChange={handleClientChange}
                        onSubmit={handleSubmit}
                        onCancel={() => setIsOpen(false)}
                        isSubmitting={mutation.isPending}
                        submitButtonText="Guardar"
                        cancelButtonText="Cancelar"
                        mode="edit" // Indicate this is edit mode
                    />
                </DialogBody>
            </DialogContent>
        </DialogRoot>
    )
}

export default EditClient 