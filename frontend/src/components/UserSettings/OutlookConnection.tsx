import { EmailsService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { Box, Button, Em, Heading, Input, Spinner, Text, VStack } from "@chakra-ui/react"
import { useMutation, useQuery } from "@tanstack/react-query"
import { useRef, useState } from "react"

const OutlookConnection = () => {
    const { showSuccessToast, showErrorToast } = useCustomToast()
    const [step, setStep] = useState<'prepare' | 'connect' | 'code'>("prepare")
    const [_, setAuthUrl] = useState("")
    const codeInputRef = useRef<HTMLInputElement>(null)

    // Query for connection status
    const { data, isLoading, isError, refetch } = useQuery({
        queryKey: ["outlook-connection-status"],
        queryFn: EmailsService.isOutlookConnected,
    })

    // Step 1: Get auth URL
    const step1Mutation = useMutation({
        mutationFn: EmailsService.createOutlookTokenStep1,
        onSuccess: (url: string) => {
            setAuthUrl(url)
            setStep("code")
            window.open(url, "_blank")
        },
        onError: () => showErrorToast("No se pudo obtener la URL de autenticación de Outlook."),
    })

    // Step 2: Send code
    const step2Mutation = useMutation({
        mutationFn: (code: string) =>
            EmailsService.createOutlookTokenStep2({ requestBody: { code } }),
        onSuccess: () => {
            showSuccessToast("¡Conexión con Outlook realizada con éxito!")
            setStep("prepare")
            setAuthUrl("")
            refetch()
        },
        onError: () => showErrorToast("No se pudo completar la autenticación con Outlook."),
    })

    let content = null

    if (isLoading) {
        content = <Spinner size="md" />
    } else if (isError) {
        content = (
            <VStack align="stretch" mt={4} gap={3}>
                <Text color="red.500">
                    No se pudo obtener el estado de la conexión.
                </Text>
            </VStack>
        )
    } else if (data && typeof data === "object" && "connected" in data) {
        if (data.connected) {
            content =
                (
                    <VStack align="stretch" mt={4} gap={3}>
                        <Text color="green.500">
                            Outlook está conectado.
                        </Text>
                    </VStack>
                )
        } else {
            content = (
                <VStack align="stretch" mt={4} gap={3}>
                    <Text color="red.500">Outlook no está conectado.</Text>
                    <Text fontWeight="medium" fontSize="sm">
                        Empezar con la Conexión
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

                    {step === "prepare" && (
                        <Button
                            variant="solid"
                            w="100%"
                            mt={4}
                            type="button"
                            onClick={() => setStep("connect")}
                        >
                            Estoy Listo
                        </Button>
                    )}

                    {step === "connect" && (
                        <>
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
                                onClick={() => step1Mutation.mutate()}
                                loading={step1Mutation.status === "pending"}
                                colorScheme="blue"
                            >
                                Conectar Outlook
                            </Button>
                        </>
                    )}

                    {step === "code" && (
                        <>
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
                                    setStep("prepare")
                                    setAuthUrl("")
                                }}
                                disabled={step2Mutation.status === "pending"}
                            >
                                Cancelar
                            </Button>
                        </>
                    )}
                </VStack>
            )
        }
    } else {
        content = <Text color="red.500">Respuesta inesperada del servidor.</Text>
    }

    return (
        <Box
            w={{ sm: "full", md: "sm" }}
            as="form">
            <Heading size="lg" py={4}>
                Conexión con Outlook
            </Heading>
            <Text fontWeight="medium" fontSize="sm">
                Estado de la Conexión
            </Text>
            {content}
        </Box>
    )
}

export default OutlookConnection
