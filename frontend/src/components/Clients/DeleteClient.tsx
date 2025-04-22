import { Button, DialogTitle, Text } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { FiTrash2 } from "react-icons/fi"

import { ClientsService } from "@/client"
import {
    DialogActionTrigger,
    DialogBody,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogRoot,
    DialogTrigger
} from "@/components/ui/dialog"
import useCustomToast from "@/hooks/useCustomToast"

const DeleteClient = ({ id }: { id: string }) => {
    const [isOpen, setIsOpen] = useState(false)
    const queryClient = useQueryClient()
    const { showSuccessToast, showErrorToast } = useCustomToast()
    const {
        handleSubmit,
        formState: { isSubmitting },
    } = useForm()

    const deleteClient = async (id: string) => {
        await ClientsService.deleteClient({ id: id })
    }

    const mutation = useMutation({
        mutationFn: deleteClient,
        onSuccess: () => {
            showSuccessToast("El cliente fue eliminado correctamente")
            setIsOpen(false)
        },
        onError: () => {
            showErrorToast("Ocurrió un error al eliminar el cliente")
        },
        onSettled: () => {
            queryClient.invalidateQueries()
        },
    })

    const onSubmit = async () => {
        mutation.mutate(id)
    }

    return (
        <DialogRoot
            size={{ base: "xs", md: "md" }}
            placement="center"
            role="alertdialog"
            open={isOpen}
            onOpenChange={({ open }) => setIsOpen(open)}
        >
            <DialogTrigger asChild>
                <Button variant="ghost" size="sm" colorPalette="red">
                    <FiTrash2 fontSize="16px" />
                    Eliminar Cliente
                </Button>
            </DialogTrigger>
            <DialogContent>
                <form onSubmit={handleSubmit(onSubmit)}>
                    <DialogHeader>
                        <DialogTitle>Eliminar Cliente</DialogTitle>
                    </DialogHeader>
                    <DialogBody>
                        <Text>¿Estás seguro de que quieres eliminar este cliente?</Text>
                    </DialogBody>
                    <DialogFooter gap={2}>
                        <DialogActionTrigger asChild>
                            <Button
                                variant="subtle"
                                colorPalette="gray"
                                disabled={isSubmitting}
                            >
                                Cancelar
                            </Button>
                        </DialogActionTrigger>
                        <Button
                            variant="solid"
                            colorPalette="red"
                            type="submit"
                            loading={isSubmitting}
                        >
                            Eliminar
                        </Button>
                    </DialogFooter>
                    {/* <DialogCloseTrigger /> */}
                </form>
            </DialogContent>
        </DialogRoot>
    )
}

export default DeleteClient 