import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
    Button,
    DialogActionTrigger,
    DialogRoot,
    DialogTrigger,
    Input,
    Text,
    Textarea,
    VStack,
} from "@chakra-ui/react"
import { useState } from "react"

import { type PromptPublic, PromptsService, type PromptUpdate } from "@/client"
import {
    DialogBody,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogTitle
} from "@/components/ui/dialog"
import { Field } from "@/components/ui/field"
import useCustomToast from "@/hooks/useCustomToast"
import { FiEdit2 } from "react-icons/fi"

interface EditPromptProps {
    prompt: PromptPublic
    disabled?: boolean
}

const EditPrompt = ({ prompt, disabled = false }: EditPromptProps) => {
    const [isOpen, setIsOpen] = useState(false)
    const queryClient = useQueryClient()
    const { showSuccessToast, showErrorToast } = useCustomToast()
    const {
        register,
        handleSubmit,
        reset,
        formState: { errors, isSubmitting },
    } = useForm<PromptUpdate & { structureString?: string }>({
        mode: "onBlur",
        criteriaMode: "all",
        defaultValues: {
            ...prompt,
            structureString: prompt.structure ? JSON.stringify(prompt.structure, null, 2) : undefined
        },
    })

    const mutation = useMutation({
        mutationFn: (data: PromptUpdate & { structureString?: string }) => {
            // Convert empty strings to undefined
            const processedData = { ...data }
            Object.keys(processedData).forEach(key => {
                if (processedData[key as keyof typeof processedData] === '') {
                    processedData[key as keyof typeof processedData] = undefined
                }
            })

            // Handle structure field
            if (processedData.structureString) {
                try {
                    processedData.structure = JSON.parse(processedData.structureString)
                } catch (e) {
                    throw new Error("El campo structure debe ser un JSON válido")
                }
            }
            delete processedData.structureString

            return PromptsService.updatePrompt({ id: prompt.id, requestBody: processedData })
        },
        onSuccess: (updatedPrompt) => {
            showSuccessToast("Prompt actualizado correctamente.")
            reset(updatedPrompt)
            setIsOpen(false)
        },
        onError: () => {
            showErrorToast("Ha ocurrido un error al editar el prompt")
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["prompts"] })
        },
    })

    const onSubmit: SubmitHandler<PromptUpdate & { structureString?: string }> = async (data) => {
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
                <Button
                    variant="ghost"
                    size="sm"
                    disabled={disabled}
                    opacity={disabled ? 0.5 : 1}
                >
                    <FiEdit2 fontSize="16px" />
                </Button>
            </DialogTrigger>
            <DialogContent>
                <form onSubmit={handleSubmit(onSubmit)}>
                    <DialogHeader>
                        <DialogTitle>Editar Prompt</DialogTitle>
                    </DialogHeader>
                    <DialogBody>
                        <Text mb={4}>Actualiza los detalles del prompt abajo.</Text>
                        <VStack gap={4}>
                            <Field
                                invalid={!!errors.query}
                                errorText={errors.query?.message}
                                label="Query"
                            >
                                <Input
                                    id="query"
                                    {...register("query", { required: "Este campo es requerido" })}
                                    placeholder="Query"
                                    type="text"
                                />
                            </Field>

                            <Field
                                invalid={!!errors.service}
                                errorText={errors.service?.message}
                                label="Service"
                            >
                                <Input
                                    id="service"
                                    {...register("service", { required: "Este campo es requerido" })}
                                    placeholder="Service"
                                    type="text"
                                />
                            </Field>

                            <Field
                                invalid={!!errors.model}
                                errorText={errors.model?.message}
                                label="Model"
                            >
                                <Input
                                    id="model"
                                    {...register("model", { required: "Este campo es requerido" })}
                                    placeholder="Model"
                                    type="text"
                                />
                            </Field>

                            <Field
                                invalid={!!errors.prompt}
                                errorText={errors.prompt?.message}
                                label="Prompt"
                            >
                                <Textarea
                                    id="prompt"
                                    {...register("prompt", { required: "Este campo es requerido" })}
                                    placeholder="Prompt"
                                    rows={6}
                                    minH="150px"
                                />
                            </Field>

                            <Field
                                invalid={!!errors.structureString}
                                errorText={String(errors.structureString?.message)}
                                label="Structure (JSON opcional)"
                            >
                                <Textarea
                                    id="structureString"
                                    {...register("structureString", {
                                        validate: (value) => {
                                            if (!value) return true
                                            try {
                                                JSON.parse(value)
                                                return true
                                            } catch (e) {
                                                return "Debe ser un JSON válido"
                                            }
                                        }
                                    })}
                                    placeholder='{"key": "value"}'
                                    rows={4}
                                    minH="100px"
                                />
                            </Field>
                        </VStack>
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
                        <Button variant="solid" type="submit" loading={isSubmitting}>
                            Guardar
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </DialogRoot>
    )
}

export default EditPrompt 