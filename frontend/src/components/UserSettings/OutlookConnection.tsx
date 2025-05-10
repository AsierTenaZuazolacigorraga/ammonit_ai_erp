import { EmailCreate, EmailPublic, EmailsService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import {
    Box,
    Button,
    Em,
    Flex,
    Heading,
    Input,
    Spinner,
    Text,
    VStack
} from "@chakra-ui/react"
import { useMutation, useQuery } from "@tanstack/react-query"
import { useRef, useState } from "react"

const OutlookConnection = () => {
    const { showSuccessToast, showErrorToast } = useCustomToast()
    const [step, setStep] = useState<'list' | 'prepare' | 'connect' | 'code'>("list")
    const [_, setAuthUrl] = useState("")
    const [newEmail, setNewEmail] = useState("")
    const [selectedEmail, setSelectedEmail] = useState<EmailCreate | null>(null)
    const codeInputRef = useRef<HTMLInputElement>(null)

    // Query for all emails
    const { data, isLoading, isError, refetch } = useQuery({
        queryKey: ["emails-list"],
        queryFn: () => EmailsService.readEmails(),
    })

    // Create new email
    const createEmailMutation = useMutation({
        mutationFn: (email: string) =>
            EmailsService.createEmail({ requestBody: { email } }),
        onSuccess: (data) => {
            showSuccessToast(`Email ${data.email} añadido. Ahora conéctalo a Outlook.`)
            setSelectedEmail({ email: data.email })
            setStep("prepare")
            refetch()
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
            if (!selectedEmail) {
                throw new Error("No email selected")
            }
            return EmailsService.createOutlookTokenStep2({
                requestBody: {
                    data: { code },
                    email_in: selectedEmail
                }
            })
        },
        onSuccess: () => {
            showSuccessToast("¡Conexión con Outlook realizada con éxito!")
            setStep("list")
            setSelectedEmail(null)
            setAuthUrl("")
            refetch()
        },
        onError: () => showErrorToast("No se pudo completar la autenticación con Outlook."),
    })

    // Handle starting the connection process for an email
    const startConnection = (email: EmailPublic) => {
        setSelectedEmail({ email: email.email })
        setStep("prepare")
    }

    // Handle adding a new email
    const handleAddEmail = () => {
        if (newEmail) {
            createEmailMutation.mutate(newEmail)
            setNewEmail("")
        }
    }

    let content = null

    if (isLoading) {
        content = <Spinner size="md" />
    } else if (isError) {
        content = (
            <VStack align="stretch" mt={4} gap={3}>
                <Text color="red.500">
                    No se pudo obtener el listado de emails.
                </Text>
            </VStack>
        )
    } else {
        // List view - show all emails and add new one form
        if (step === "list") {
            const emailsList = data?.data || []

            content = (
                <VStack align="stretch" mt={4} gap={3}>

                    <Text fontWeight="medium" fontSize="sm">
                        Emails conectados a Outlook
                    </Text>

                    {emailsList.length === 0 ? (
                        <Text color="gray.500">No hay emails configurados.</Text>
                    ) : (
                        emailsList.map((email) => (
                            <Flex
                                key={email.id}
                                justify="space-between"
                                align="center"
                                p={3}
                                bg="gray.50"
                                borderRadius="md"
                            >
                                <Box maxW="60%" overflow="hidden" textOverflow="ellipsis" whiteSpace="nowrap">
                                    <Text truncate>{email.email}</Text>
                                    {email.is_connected ? (
                                        <Text color="green.500" fontSize="sm">Conectado</Text>
                                    ) : (
                                        <Text color="orange.500" fontSize="sm">No conectado</Text>
                                    )}
                                </Box>
                                {!email.is_connected && (
                                    <Button
                                        size="sm"
                                        colorScheme="blue"
                                        onClick={() => startConnection(email)}
                                    >
                                        Conectar
                                    </Button>
                                )}
                            </Flex>
                        ))
                    )}

                    <Box borderBottom="1px solid" borderColor="gray.200" my={2} />

                    <Text fontWeight="medium" fontSize="sm">
                        Añadir nuevo email
                    </Text>

                    <Box>
                        <Text mb={2}>Email</Text>
                        <Input
                            type="email"
                            placeholder="nombre@outlook.com"
                            value={newEmail}
                            onChange={(e) => setNewEmail(e.target.value)}
                        />
                    </Box>

                    <Button
                        colorScheme="blue"
                        onClick={handleAddEmail}
                        disabled={!newEmail}
                        loading={createEmailMutation.status === "pending"}
                    >
                        Añadir email
                    </Button>
                </VStack>
            )
        }
        // Views for the connection steps (when an email is selected)
        else if (selectedEmail) {
            // Base content for all steps
            const baseContent = (
                <>
                    <Text fontWeight="medium" fontSize="sm">
                        Empezar con la Conexión Para:
                    </Text>
                    <Text fontWeight="medium" fontSize="sm">
                        <Em>{selectedEmail.email}</Em>
                    </Text>
                    <Text fontSize="sm">
                        <Em>¿Qué es esto?</Em>
                    </Text>
                    <Text fontSize="sm">
                        Un proceso sencillo para conectar Ammonit a tu cuenta de Outlook.
                    </Text>
                    <Text fontSize="sm">
                        <Em>Prepárate</Em>
                    </Text>
                    <Text fontSize="sm">
                        Asegúrate de tener cerradas todas las sesiones de Outlook en el navegador.
                        Tienes que hacer un log out, para luego hacer un log in fresco.
                        Cuando hayas salido de todas las sesiones, haz click en "Estoy Listo".
                    </Text>
                </>
            )

            // Prepare step
            if (step === "prepare") {
                content = (
                    <VStack align="stretch" mt={4} gap={3}>
                        {baseContent}
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
                                setStep("list")
                                setSelectedEmail(null)
                            }}
                        >
                            Cancelar
                        </Button>
                    </VStack>
                )
            }
            // Connect step
            else if (step === "connect") {
                content = (
                    <VStack align="stretch" mt={4} gap={3}>
                        {baseContent}
                        <Button
                            variant="solid"
                            w="100%"
                            mt={4}
                            type="button"
                            colorScheme="gray"
                            disabled
                        >
                            Estoy Listo
                        </Button>
                        <Text fontSize="sm">
                            <Em>Autentícate</Em>
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
                                setStep("list")
                                setSelectedEmail(null)
                            }}
                            disabled={step1Mutation.status === "pending"}
                        >
                            Cancelar
                        </Button>
                    </VStack>
                )
            }
            // Code entry step
            else if (step === "code") {
                content = (
                    <VStack align="stretch" mt={4} gap={3}>
                        {baseContent}
                        <Button
                            variant="solid"
                            w="100%"
                            mt={4}
                            type="button"
                            colorScheme="gray"
                            disabled
                        >
                            Estoy Listo
                        </Button>
                        <Text fontSize="sm">
                            <Em>Autentícate</Em>
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
                                setStep("list")
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
        }
    }

    return (
        <Box
            w={{ sm: "full", md: "sm" }}
            as="form"
            onSubmit={(e) => e.preventDefault()} // Prevent form submission
        >
            <Heading size="lg" py={4}>
                Conexión con Outlook
            </Heading>
            {content}
        </Box>
    )
}

export default OutlookConnection
