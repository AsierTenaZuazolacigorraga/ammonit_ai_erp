import { Button, DialogTitle, Text } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { FiTrash2 } from "react-icons/fi"

import { UsersService } from "@/client"
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

const DeleteUser = ({ id, disabled = false }: { id: string; disabled?: boolean }) => {
    const [isOpen, setIsOpen] = useState(false)
    const queryClient = useQueryClient()
    const { showSuccessToast, showErrorToast } = useCustomToast()
    const {
        handleSubmit,
        formState: { isSubmitting },
    } = useForm()

    const deleteUser = async (id: string) => {
        await UsersService.deleteUser({ id })
    }

    const mutation = useMutation({
        mutationFn: deleteUser,
        onSuccess: () => {
            showSuccessToast("El usuario ha sido eliminado correctamente")
            setIsOpen(false)
        },
        onError: () => {
            showErrorToast("Ha ocurrido un error al eliminar el usuario")
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
                <Button
                    variant="ghost"
                    size="sm"
                    colorPalette="red"
                    disabled={disabled}
                    opacity={disabled ? 0.5 : 1}
                >
                    <FiTrash2 fontSize="16px" />
                    {/* Eliminar Usuario */}
                </Button>
            </DialogTrigger>
            <DialogContent>
                <form onSubmit={handleSubmit(onSubmit)}>
                    <DialogHeader>
                        <DialogTitle>Eliminar Usuario</DialogTitle>
                    </DialogHeader>
                    <DialogBody>
                        <Text mb={4}>
                            Todos los elementos asociados con este usuario también serán{" "}
                            <strong>eliminados permanentemente.</strong> ¿Estás seguro? No podrás
                            deshacer esta acción.
                        </Text>
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

export default DeleteUser