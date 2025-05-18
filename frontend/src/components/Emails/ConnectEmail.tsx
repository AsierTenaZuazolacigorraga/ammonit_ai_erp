import { EmailCreate, EmailsService } from "@/client"
import {
    DialogContent,
    DialogRoot,
    DialogTrigger
} from "@/components/ui/dialog"
import useCustomToast from "@/hooks/useCustomToast"
import { Button, Icon, Input, Text, VStack } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useRef, useState } from "react"
import { FiLink } from "react-icons/fi"

interface ConnectEmailProps {
    email: string
    is_connected?: boolean
}

const ConnectEmail = ({ email, is_connected }: ConnectEmailProps) => {
    const [isOpen, setIsOpen] = useState(false)
    const [step, setStep] = useState<'prepare' | 'connect' | 'code'>('prepare')
    const [_, setAuthUrl] = useState("")
    const codeInputRef = useRef<HTMLInputElement>(null)
    const queryClient = useQueryClient()
    const { showSuccessToast, showErrorToast } = useCustomToast()
    const emailObj: EmailCreate = { email }

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
                    email_in: emailObj
                }
            })
        },
        onSuccess: () => {
            showSuccessToast("¡Conexión con Outlook realizada con éxito!")
            setStep("prepare")
            setIsOpen(false)
            setAuthUrl("")
            queryClient.invalidateQueries({ queryKey: ["emails"] })
        },
        onError: () => showErrorToast("No se pudo completar la autenticación con Outlook."),
    })

    if (is_connected) {
        return (
            <Button
                variant="ghost"
                size="sm"
                colorScheme="gray"
                disabled
                opacity={0.5}
            >
                <Icon as={FiLink} fontSize="16px" />
            </Button>
        )
    }

    let content = null
    if (step === "prepare") {
        content = (
            <VStack align="stretch" mt={2} gap={4}>
                <Text fontWeight="medium" fontSize="sm" mb={2}>
                    Empezar con la Conexión Para:
                </Text>
                <Text fontWeight="medium" fontSize="sm" mb={2}>
                    <em>{email}</em>
                </Text>
                <Text fontSize="sm" mb={2}>
                    <em>¿Qué es esto?</em>
                </Text>
                <Text fontSize="sm" mb={2}>
                    Un proceso sencillo para conectar Ammonit a tu cuenta de Outlook.
                </Text>
                <Text fontSize="sm" mb={2}>
                    <em>Prepárate</em>
                </Text>
                <Text fontSize="sm" mb={2}>
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
                    onClick={() => setIsOpen(false)}
                >
                    Cancelar
                </Button>
            </VStack>
        )
    } else if (step === "connect") {
        content = (
            <VStack align="stretch" mt={2} gap={4}>
                <Text fontWeight="medium" fontSize="sm" mb={2}>
                    Empezar con la Conexión Para:
                </Text>
                <Text fontWeight="medium" fontSize="sm" mb={2}>
                    <em>{email}</em>
                </Text>
                <Text fontSize="sm" mb={2}>
                    <em>Autentícate</em>
                </Text>
                <Text fontSize="sm" mb={2}>
                    1. Cuando clickes en "Conectar Outlook" se te abrirá una ventana nueva.<br />
                    2. Autentícate en la ventana que se ha abierto, usando la cuenta de Outlook que tienes para Ammonit.<br />
                    3. Copia el url de la página y vuelve aquí para pegarlo.
                </Text>
                <Button
                    variant="solid"
                    w="100%"
                    mt={2}
                    type="button"
                    onClick={() => step1Mutation.mutate(emailObj)}
                    loading={step1Mutation.status === "pending"}
                    colorScheme="blue"
                >
                    Conectar Outlook
                </Button>
                <Button
                    variant="ghost"
                    w="100%"
                    onClick={() => setIsOpen(false)}
                    disabled={step1Mutation.status === "pending"}
                >
                    Cancelar
                </Button>
            </VStack>
        )
    } else if (step === "code") {
        content = (
            <VStack align="stretch" mt={2} gap={4}>
                <Text fontWeight="medium" fontSize="sm" mb={2}>
                    Empezar con la Conexión Para:
                </Text>
                <Text fontWeight="medium" fontSize="sm" mb={2}>
                    <em>{email}</em>
                </Text>
                <Text fontSize="sm" mb={2}>
                    <em>Autentícate</em>
                </Text>
                <Text fontSize="sm" mb={2}>
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
                    onClick={() => setIsOpen(false)}
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
                setStep('prepare')
                setAuthUrl("")
            }}
        >
            <DialogTrigger asChild>
                <Button
                    variant="ghost"
                    size="sm"
                    colorScheme="blue"
                >
                    <Icon as={FiLink} fontSize="16px" />
                </Button>
            </DialogTrigger>
            <DialogContent p={6}>{content}</DialogContent>
        </DialogRoot>
    )
}

export default ConnectEmail 