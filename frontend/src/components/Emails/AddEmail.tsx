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
import { emailPattern } from "@/utils"
import { Button, Input, Text, VStack } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useRef, useState } from "react"
import { useForm } from "react-hook-form"
import { FaPlus } from "react-icons/fa"

const AddEmail = () => {
    const [isOpen, setIsOpen] = useState(false)
    const [step, setStep] = useState<'form' | 'prepare' | 'connect' | 'code'>('form')
    const [selectedEmail, setSelectedEmail] = useState<EmailCreate | null>(null)
    const [_, setAuthUrl] = useState("")
    const codeInputRef = useRef<HTMLInputElement>(null)
    const queryClient = useQueryClient()
    const { showSuccessToast, showErrorToast } = useCustomToast()
    const { register, handleSubmit, reset, formState: { errors, isSubmitting }, watch } = useForm<{ email: string }>({
        mode: "onBlur",
        criteriaMode: "all",
        defaultValues: { email: "" },
    })
    const emailValue = watch("email")

    // Create new email
    const createEmailMutation = useMutation({
        mutationFn: (data: { email: string }) =>
            EmailsService.createEmail({ requestBody: data }),
        onSuccess: (data) => {
            showSuccessToast(`Email ${data.email} añadido. Ahora conéctalo a Outlook.`)
            setSelectedEmail({ email: data.email })
            setStep("prepare")
            queryClient.invalidateQueries({ queryKey: ["emails"] })
            reset()
        },
        onError: () => showErrorToast("No se pudo añadir el email."),
    })

    // Step 1: Get auth URL
    const step1Mutation = useMutation({
        mutationFn: (emailData: EmailCreate) =>
            EmailsService.createOutlookTokenStep1({ requestBody: emailData }),
        onSuccess: (url: string) => {
            setAuthUrl(url)
            setStep("code")
            window.open(url, "_blank")
        },
        onError: () => showErrorToast("No se pudo obtener la URL de autenticación de Outlook."),
    })

    // Step 2: Send code
    const step2Mutation = useMutation({
        mutationFn: (code: string) => {
            if (!selectedEmail) throw new Error("No email selected")
            return EmailsService.createOutlookTokenStep2({
                requestBody: {
                    data: { code },
                    email_in: selectedEmail
                }
            })
        },
        onSuccess: () => {
            showSuccessToast("¡Conexión con Outlook realizada con éxito!")
            setStep("form")
            setSelectedEmail(null)
            setAuthUrl("")
            setIsOpen(false)
            queryClient.invalidateQueries({ queryKey: ["emails"] })
        },
        onError: () => showErrorToast("No se pudo completar la autenticación con Outlook."),
    })

    const onSubmit = (data: { email: string }) => {
        createEmailMutation.mutate(data)
    }

    // Dialog content for each step
    let content = null
    if (step === "form") {
        content = (
            <form onSubmit={handleSubmit(onSubmit)}>
                <DialogHeader>
                    <DialogTitle>Agregar Email</DialogTitle>
                </DialogHeader>
                <DialogBody>
                    <VStack gap={4}>
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
                        loading={isSubmitting}
                        disabled={!emailValue}
                    >
                        Guardar
                    </Button>
                </DialogFooter>
            </form>
        )
    } else if (step === "prepare" && selectedEmail) {
        content = (
            <VStack align="stretch" mt={4} gap={3}>
                <Text fontWeight="medium" fontSize="sm">
                    Empezar con la Conexión Para:
                </Text>
                <Text fontWeight="medium" fontSize="sm">
                    <em>{selectedEmail.email}</em>
                </Text>
                <Text fontSize="sm">
                    <em>¿Qué es esto?</em>
                </Text>
                <Text fontSize="sm">
                    Un proceso sencillo para conectar Ammonit a tu cuenta de Outlook.
                </Text>
                <Text fontSize="sm">
                    <em>Prepárate</em>
                </Text>
                <Text fontSize="sm">
                    Asegúrate de tener cerradas todas las sesiones de Outlook en el navegador.
                    Tienes que hacer un log out, para luego hacer un log in fresco.
                    Cuando hayas salido de todas las sesiones, haz click en "Estoy Listo".
                </Text>
                <Button
                    variant="solid"
                    w="100%"
                    mt={4}
                    type="button"
                    onClick={() => setStep("connect")}
                >
                    Estoy Listo
                </Button>
                <Button
                    variant="ghost"
                    w="100%"
                    onClick={() => {
                        setStep("form")
                        setSelectedEmail(null)
                    }}
                >
                    Cancelar
                </Button>
            </VStack>
        )
    } else if (step === "connect" && selectedEmail) {
        content = (
            <VStack align="stretch" mt={4} gap={3}>
                <Text fontWeight="medium" fontSize="sm">
                    Empezar con la Conexión Para:
                </Text>
                <Text fontWeight="medium" fontSize="sm">
                    <em>{selectedEmail.email}</em>
                </Text>
                <Text fontSize="sm">
                    <em>Autentícate</em>
                </Text>
                <Text fontSize="sm">
                    1. Cuando clickes en "Conectar Outlook" se te abrirá una ventana nueva.<br />
                    2. Autentícate en la ventana que se ha abierto, usando la cuenta de Outlook que tienes para Ammonit.<br />
                    3. Copia el url de la página y vuelve aquí para pegarlo.
                </Text>
                <Button
                    variant="solid"
                    w="100%"
                    mt={2}
                    type="button"
                    onClick={() => step1Mutation.mutate(selectedEmail)}
                    loading={step1Mutation.status === "pending"}
                    colorScheme="blue"
                >
                    Conectar Outlook
                </Button>
                <Button
                    variant="ghost"
                    w="100%"
                    onClick={() => {
                        setStep("form")
                        setSelectedEmail(null)
                    }}
                    disabled={step1Mutation.status === "pending"}
                >
                    Cancelar
                </Button>
            </VStack>
        )
    } else if (step === "code" && selectedEmail) {
        content = (
            <VStack align="stretch" mt={4} gap={3}>
                <Text fontWeight="medium" fontSize="sm">
                    Empezar con la Conexión Para:
                </Text>
                <Text fontWeight="medium" fontSize="sm">
                    <em>{selectedEmail.email}</em>
                </Text>
                <Text fontSize="sm">
                    <em>Autentícate</em>
                </Text>
                <Text fontSize="sm">
                    1. Cuando clickes en "Conectar Outlook" se te abrirá una ventana nueva.<br />
                    2. Autentícate en la ventana que se ha abierto.<br />
                    3. Copia el url de la página y vuelve aquí para pegarlo.
                </Text>
                <Input
                    ref={codeInputRef}
                    placeholder="Pega el código de autorización"
                    disabled={step2Mutation.status === "pending"}
                    onKeyDown={e => {
                        if (e.key === "Enter") {
                            step2Mutation.mutate(codeInputRef.current?.value || "")
                        }
                    }}
                />
                <Button
                    colorScheme="green"
                    w="100%"
                    mt={2}
                    loading={step2Mutation.status === "pending"}
                    onClick={() => step2Mutation.mutate(codeInputRef.current?.value || "")}
                >
                    Confirmar
                </Button>
                <Button
                    variant="ghost"
                    w="100%"
                    mt={2}
                    onClick={() => {
                        setStep("form")
                        setSelectedEmail(null)
                        setAuthUrl("")
                    }}
                    disabled={step2Mutation.status === "pending"}
                >
                    Cancelar
                </Button>
            </VStack>
        )
    }

    return (
        <DialogRoot
            size={{ base: "xs", md: "md" }}
            placement="center"
            open={isOpen}
            onOpenChange={({ open }) => {
                setIsOpen(open)
                if (!open) {
                    setStep("form")
                    setSelectedEmail(null)
                    setAuthUrl("")
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
    )
}

export default AddEmail 