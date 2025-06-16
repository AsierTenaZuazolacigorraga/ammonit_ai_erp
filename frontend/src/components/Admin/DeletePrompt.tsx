import { Button, DialogTitle, Text } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { FiTrash2 } from "react-icons/fi"

import { PromptsService } from "@/client"
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

const DeletePrompt = ({ id, disabled = false }: { id: string; disabled?: boolean }) => {
    const [isOpen, setIsOpen] = useState(false)
    const queryClient = useQueryClient()
    const { showSuccessToast, showErrorToast } = useCustomToast()
    const {
        handleSubmit,
        formState: { isSubmitting },
    } = useForm()

    const deletePrompt = async (id: string) => {
        await PromptsService.deletePrompt({ id })
    }

    const mutation = useMutation({
        mutationFn: deletePrompt,
        onSuccess: () => {
            showSuccessToast("El prompt ha sido eliminado correctamente")
            setIsOpen(false)
        },
        onError: () => {
            showErrorToast("Ha ocurrido un error al eliminar el prompt")
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
                </Button>
            </DialogTrigger>
            <DialogContent>
                <form onSubmit={handleSubmit(onSubmit)}>
                    <DialogHeader>
                        <DialogTitle>Eliminar Prompt</DialogTitle>
                    </DialogHeader>
                    <DialogBody>
                        <Text mb={4}>
                            ¿Estás seguro de que deseas eliminar este prompt? Esta acción no se puede deshacer.
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
                </form>
            </DialogContent>
        </DialogRoot>
    )
}

export default DeletePrompt 