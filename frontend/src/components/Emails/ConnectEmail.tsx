import { EmailCreate, EmailsService } from "@/client"
import {
    DialogActionTrigger,
    DialogBody,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogRoot,
    DialogTitle
} from "@/components/ui/dialog"
import useCustomToast from "@/hooks/useCustomToast"
import { Button, IconButton, Input, Text, VStack } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useRef, useState } from "react"
import { FiLink } from "react-icons/fi"

interface ConnectEmailProps {
    email: string
    is_connected?: boolean
    isOpen?: boolean
    onClose?: () => void
}

const ConnectEmail = ({ email, is_connected, isOpen: controlledIsOpen, onClose: controlledOnClose }: ConnectEmailProps) => {
    // Internal state for uncontrolled usage
    const [internalOpen, setInternalOpen] = useState(false)
    const isOpen = controlledIsOpen !== undefined ? controlledIsOpen : internalOpen
    const onClose = controlledOnClose !== undefined ? controlledOnClose : () => setInternalOpen(false)

    const [step, setStep] = useState<'prepare' | 'connect' | 'code'>('prepare')
    const [_, setAuthUrl] = useState("")
    const codeInputRef = useRef<HTMLInputElement>(null)
    const queryClient = useQueryClient()
    const { showSuccessToast, showErrorToast } = useCustomToast()
    const selectedEmail: EmailCreate = { email }

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
            return EmailsService.createOutlookTokenStep2({
                requestBody: {
                    data: { code },
                    email_in: selectedEmail
                }
            })
        },
        onSuccess: () => {
            showSuccessToast("¡Conexión con Outlook realizada con éxito!")
            setStep("prepare")
            setAuthUrl("")
            queryClient.invalidateQueries({ queryKey: ["emails"] })
            if (onClose) onClose()
        },
        onError: () => showErrorToast("No se pudo completar la autenticación con Outlook."),
    })

    // Always render the icon button
    const iconButton = (
        <IconButton
            aria-label="Conectar"
            variant="ghost"
            colorScheme={is_connected ? "gray" : "blue"}
            size="sm"
            onClick={is_connected ? undefined : () => setInternalOpen(true)}
            title="Conectar"
            disabled={!!is_connected}
            opacity={is_connected ? 0.5 : 1}
        >
            <FiLink />
        </IconButton>
    )

    // Dialog content (same as before)
    let content = null
    if (step === "prepare") {
        content = (
            <form>
                <DialogHeader>
                    <DialogTitle>Conectar Outlook</DialogTitle>
                </DialogHeader>
                <DialogBody>
                    <VStack gap={3} align="stretch">
                        <Text fontWeight="medium" fontSize="sm">
                            Empezar con la Conexión Para:
                        </Text>
                        <Text fontWeight="semibold" fontSize="md">
                            <em>{selectedEmail.email}</em>
                        </Text>
                        <Text fontSize="sm" fontStyle="italic" mt={2}>
                            ¿Qué es esto?
                        </Text>
                        <Text fontSize="sm">
                            Un proceso sencillo para conectar Ammonit a tu cuenta de Outlook.
                        </Text>
                        <Text fontSize="sm" fontStyle="italic" mt={2}>
                            Prepárate
                        </Text>
                        <Text fontSize="sm">
                            Asegúrate de tener cerradas todas las sesiones de Outlook en el navegador. Tienes que hacer un log out, para luego hacer un log in fresco. Cuando hayas salido de todas las sesiones, haz click en "Estoy Listo".
                        </Text>
                    </VStack>
                </DialogBody>
                <DialogFooter>
                    <VStack w="100%" gap={2}>
                        <Button
                            variant="solid"
                            w="100%"
                            type="button"
                            onClick={() => setStep("connect")}
                        >
                            Estoy Listo
                        </Button>
                        <DialogActionTrigger asChild>
                            <Button
                                variant="ghost"
                                w="100%"
                                onClick={onClose}
                            >
                                Cancelar
                            </Button>
                        </DialogActionTrigger>
                    </VStack>
                </DialogFooter>
            </form>
        )
    } else if (step === "connect") {
        content = (
            <form>
                <DialogHeader>
                    <DialogTitle>Conectar Outlook</DialogTitle>
                </DialogHeader>
                <DialogBody>
                    <VStack gap={3} align="stretch">
                        <Text fontWeight="medium" fontSize="sm">
                            Empezar con la Conexión Para:
                        </Text>
                        <Text fontWeight="semibold" fontSize="md">
                            <em>{selectedEmail.email}</em>
                        </Text>
                        <Text fontSize="sm" fontStyle="italic" mt={2}>
                            Autentícate
                        </Text>
                        <Text fontSize="sm">
                            1. Cuando clickes en "Conectar Outlook" se te abrirá una ventana nueva.<br />
                            2. Autentícate en la ventana que se ha abierto, usando la cuenta de Outlook que tienes para Ammonit.<br />
                            3. Copia el url de la página y vuelve aquí para pegarlo.
                        </Text>
                    </VStack>
                </DialogBody>
                <DialogFooter>
                    <VStack w="100%" gap={2}>
                        <Button
                            variant="solid"
                            w="100%"
                            type="button"
                            onClick={() => step1Mutation.mutate(selectedEmail)}
                            loading={step1Mutation.status === "pending"}
                            colorScheme="blue"
                        >
                            Conectar Outlook
                        </Button>
                        <DialogActionTrigger asChild>
                            <Button
                                variant="ghost"
                                w="100%"
                                onClick={onClose}
                                disabled={step1Mutation.status === "pending"}
                            >
                                Cancelar
                            </Button>
                        </DialogActionTrigger>
                    </VStack>
                </DialogFooter>
            </form>
        )
    } else if (step === "code") {
        content = (
            <form onSubmit={e => { e.preventDefault(); step2Mutation.mutate(codeInputRef.current?.value || "") }}>
                <DialogHeader>
                    <DialogTitle>Conectar Outlook</DialogTitle>
                </DialogHeader>
                <DialogBody>
                    <VStack gap={3} align="stretch">
                        <Text fontWeight="medium" fontSize="sm">
                            Empezar con la Conexión Para:
                        </Text>
                        <Text fontWeight="semibold" fontSize="md">
                            <em>{selectedEmail.email}</em>
                        </Text>
                        <Text fontSize="sm" fontStyle="italic" mt={2}>
                            Autentícate
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
                    </VStack>
                </DialogBody>
                <DialogFooter>
                    <VStack w="100%" gap={2}>
                        <Button
                            colorScheme="green"
                            w="100%"
                            type="submit"
                            loading={step2Mutation.status === "pending"}
                        >
                            Confirmar
                        </Button>
                        <DialogActionTrigger asChild>
                            <Button
                                variant="ghost"
                                w="100%"
                                onClick={onClose}
                                disabled={step2Mutation.status === "pending"}
                            >
                                Cancelar
                            </Button>
                        </DialogActionTrigger>
                    </VStack>
                </DialogFooter>
            </form>
        )
    }

    return (
        <>
            {iconButton}
            <DialogRoot
                size={{ base: "xs", md: "md" }}
                placement="center"
                open={!!isOpen}
                onOpenChange={({ open }) => {
                    if (!open && onClose) onClose()
                }}
            >
                <DialogContent>{content}</DialogContent>
            </DialogRoot>
        </>
    )
}

export default ConnectEmail 