import { EmailCreate, EmailsService } from "@/client"
import {
    DialogActionTrigger,
    DialogBody,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogRoot,
    DialogTitle,
    DialogTrigger
} from "@/components/ui/dialog"
import { Field } from "@/components/ui/field"
import useCustomToast from "@/hooks/useCustomToast"
import { emailPattern } from "@/utils/utils"
import { Button, Input, VStack } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { useForm } from "react-hook-form"
import { FaPlus } from "react-icons/fa"
import ConnectEmail from "./ConnectEmail"

const AddEmail = () => {
    const [isOpen, setIsOpen] = useState(false)
    const [selectedEmail, setSelectedEmail] = useState<EmailCreate | null>(null)
    const queryClient = useQueryClient()
    const { showSuccessToast, showErrorToast } = useCustomToast()
    const { register, handleSubmit, reset, formState: { errors, isSubmitting }, watch } = useForm<{ email: string }>({
        mode: "onBlur",
        criteriaMode: "all",
        defaultValues: { email: "" },
    })
    const emailValue = watch("email")
    const [showConnect, setShowConnect] = useState(false)

    // Create new email
    const mutation = useMutation({
        mutationFn: (data: { email: string }) =>
            EmailsService.createEmail({ requestBody: data }),
        onSuccess: (data) => {
            showSuccessToast(`Email ${data.email} añadido. Ahora conéctalo a Outlook.`)
            setSelectedEmail({ email: data.email })
            setShowConnect(true)
            queryClient.invalidateQueries({ queryKey: ["emails"] })
            reset()
        },
        onError: () => showErrorToast("No se pudo añadir el email."),
    })

    const onSubmit = (data: { email: string }) => {
        mutation.mutate(data)
    }

    let content = (
        <form onSubmit={handleSubmit(onSubmit)}>
            <DialogHeader>
                <DialogTitle>Agregar Email</DialogTitle>
            </DialogHeader>
            <DialogBody>
                <VStack gap={4} align="stretch">
                    <Field
                        required
                        invalid={!!errors.email}
                        errorText={errors.email?.message}
                        label="Email"
                    >
                        <Input
                            id="email"
                            {...register("email", {
                                required: "El email es requerido",
                                pattern: emailPattern,
                            })}
                            placeholder="nombre@outlook.com"
                            type="email"
                            autoFocus
                        />
                    </Field>
                </VStack>
            </DialogBody>
            <DialogFooter gap={2}>
                <DialogActionTrigger asChild>
                    <Button variant="subtle" colorPalette="gray" disabled={isSubmitting}>
                        Cancelar
                    </Button>
                </DialogActionTrigger>
                <Button
                    variant="solid"
                    colorScheme="blue"
                    type="submit"
                    loading={isSubmitting || mutation.isPending}
                    disabled={!emailValue}
                    loadingText="Guardando..."
                >
                    Guardar
                </Button>
            </DialogFooter>
        </form>
    )

    return (
        <>
            <DialogRoot
                size={{ base: "xs", md: "md" }}
                placement="center"
                open={isOpen}
                onOpenChange={({ open }) => {
                    setIsOpen(open)
                    if (!open) {
                        setSelectedEmail(null)
                        setShowConnect(false)
                    }
                }}
            >
                <DialogTrigger asChild>
                    <Button colorScheme="blue" my={4}>
                        <FaPlus fontSize="16px" style={{ marginRight: 8 }} />
                        Agregar Email
                    </Button>
                </DialogTrigger>
                <DialogContent>{content}</DialogContent>
            </DialogRoot>
            {showConnect && selectedEmail && (
                <ConnectEmail
                    email={selectedEmail.email}
                    isOpen={showConnect}
                    onClose={() => {
                        setShowConnect(false)
                        setSelectedEmail(null)
                        setIsOpen(false)
                    }}
                />
            )}
        </>
    )
}

export default AddEmail 