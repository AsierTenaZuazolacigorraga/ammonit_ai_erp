import { Button, DialogTitle, Text } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { FiTrash2 } from "react-icons/fi"

import { EmailsService } from "@/client"
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

const DeleteEmail = ({ id }: { id: string }) => {
    const [isOpen, setIsOpen] = useState(false)
    const queryClient = useQueryClient()
    const { showSuccessToast, showErrorToast } = useCustomToast()
    const {
        handleSubmit,
        formState: { isSubmitting },
    } = useForm()

    const deleteEmail = async (id: string) => {
        await EmailsService.deleteEmail({ id: id })
    }

    const mutation = useMutation({
        mutationFn: deleteEmail,
        onSuccess: () => {
            showSuccessToast("El email fue eliminado correctamente")
            setIsOpen(false)
        },
        onError: () => {
            showErrorToast("Ocurrió un error al eliminar el email")
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
                </Button>
            </DialogTrigger>
            <DialogContent>
                <form onSubmit={handleSubmit(onSubmit)}>
                    <DialogHeader>
                        <DialogTitle>Eliminar Email</DialogTitle>
                    </DialogHeader>
                    <DialogBody>
                        <Text>¿Estás seguro de que quieres eliminar este email?</Text>
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
                </form>
            </DialogContent>
        </DialogRoot>
    )
}

export default DeleteEmail 