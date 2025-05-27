import { EmailsService, type ApiError, type EmailPublic } from "@/client"
import {
    DialogBody,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogRoot,
    DialogTrigger
} from "@/components/ui/dialog"
import { Field } from "@/components/ui/field"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
    Button,
    Checkbox,
    DialogActionTrigger,
    DialogTitle,
    VStack,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { Controller, useForm } from "react-hook-form"
import { FiEdit2 } from "react-icons/fi"

interface EditEmailProps {
    email: EmailPublic
}

const EditEmail = ({ email }: EditEmailProps) => {
    const [isOpen, setIsOpen] = useState(false)
    const queryClient = useQueryClient()
    const { showSuccessToast } = useCustomToast()
    const {
        handleSubmit,
        formState: { errors, isSubmitting },
        control,
    } = useForm<{ is_active: boolean }>({
        mode: "onBlur",
        criteriaMode: "all",
        defaultValues: { is_active: email.is_active },
    })

    const mutation = useMutation({
        mutationFn: (data: { is_active: boolean }) =>
            EmailsService.updateEmail({ id: email.id, requestBody: { is_active: data.is_active, email: email.email } }),
        onSuccess: () => {
            showSuccessToast("Email habilitado correctamente.")
            setIsOpen(false)
        },
        onError: (err: ApiError) => {
            handleError(err)
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["emails"] })
        },
    })

    const onSubmit = (data: { is_active: boolean }) => {
        mutation.mutate(data)
    }

    return (
        <DialogRoot
            size={{ base: "xs", md: "md" }}
            placement="center"
            open={isOpen}
            onOpenChange={({ open }) => setIsOpen(open)}
        >
            <DialogTrigger asChild>
                <Button variant="ghost" size="sm">
                    <FiEdit2 fontSize="16px" />
                </Button>
            </DialogTrigger>
            <DialogContent>
                <form onSubmit={handleSubmit(onSubmit)}>
                    <DialogHeader>
                        <DialogTitle>Editar Email</DialogTitle>
                    </DialogHeader>
                    <DialogBody>
                        <VStack gap={4}>
                            <Field
                                label="Email habilitado"
                                invalid={!!errors.is_active}
                                errorText={errors.is_active?.message}
                            >
                                <Controller
                                    name="is_active"
                                    control={control}
                                    render={({ field }) => {
                                        return (
                                            <Checkbox.Root
                                                mt={2}
                                                checked={!!field.value}
                                                onCheckedChange={val => {
                                                    field.onChange(val.checked)
                                                }}
                                            >
                                                <Checkbox.HiddenInput />
                                                <Checkbox.Control />
                                                <Checkbox.Label>
                                                    Habilitar Email
                                                </Checkbox.Label>
                                            </Checkbox.Root>
                                        )
                                    }}
                                />
                            </Field>
                        </VStack>
                    </DialogBody>
                    <DialogFooter gap={2}>
                        {!(isSubmitting || mutation.isPending) && (
                            <DialogActionTrigger asChild>
                                <Button
                                    variant="subtle"
                                    colorPalette="gray"
                                    disabled={isSubmitting}
                                >
                                    Cancelar
                                </Button>
                            </DialogActionTrigger>
                        )}
                        <Button
                            variant="solid"
                            type="submit"
                            loading={isSubmitting || mutation.isPending}
                            loadingText="Procesando..."
                        >
                            Guardar
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </DialogRoot>
    )
}

export default EditEmail 