import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import type { ApiError, PromptCreate } from "@/client"
import { PromptsService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
    Button,
    DialogActionTrigger,
    DialogTitle,
    Input,
    Textarea,
    VStack
} from "@chakra-ui/react"
import { useState } from "react"
import { FaPlus } from "react-icons/fa"
import {
    DialogBody,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogRoot,
    DialogTrigger
} from "../ui/dialog"
import { Field } from "../ui/field"

const AddPrompt = () => {
    const [isOpen, setIsOpen] = useState(false)
    const queryClient = useQueryClient()
    const { showSuccessToast } = useCustomToast()
    const {
        register,
        handleSubmit,
        reset,
        formState: { errors, isValid, isSubmitting },
    } = useForm<PromptCreate>({
        mode: "onBlur",
        criteriaMode: "all",
        defaultValues: {
            query: undefined,
            service: undefined,
            model: undefined,
            prompt: undefined,
            structure: undefined,
        },
    })

    const mutation = useMutation({
        mutationFn: (data: PromptCreate) => {
            // Convert empty strings to undefined
            const processedData = { ...data }
            Object.keys(processedData).forEach(key => {
                if (processedData[key as keyof PromptCreate] === '') {
                    processedData[key as keyof PromptCreate] = undefined
                }
            })

            // Try to parse structure as JSON if it's a string
            const structure = processedData.structure as string | undefined
            if (structure && typeof structure === 'string' && structure.trim()) {
                try {
                    processedData.structure = JSON.parse(structure)
                } catch (e) {
                    throw new Error("El campo structure debe ser un JSON válido")
                }
            }
            return PromptsService.createPrompt({
                requestBody: processedData
            })
        },
        onSuccess: () => {
            showSuccessToast("Prompt creado correctamente.")
            reset()
            setIsOpen(false)
        },
        onError: (err: ApiError) => {
            handleError(err)
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["prompts"] })
        },
    })

    const onSubmit: SubmitHandler<PromptCreate> = (data) => {
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
                <Button value="add-prompt" my={4}>
                    <FaPlus fontSize="16px" />
                    Agregar Prompt
                </Button>
            </DialogTrigger>
            <DialogContent>
                <form onSubmit={handleSubmit(onSubmit)}>
                    <DialogHeader>
                        <DialogTitle>Agregar Prompt</DialogTitle>
                    </DialogHeader>
                    <DialogBody>
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
                                invalid={!!errors.structure}
                                errorText={String(errors.structure?.message)}
                                label="Structure (JSON opcional)"
                            >
                                <Textarea
                                    id="structure"
                                    {...register("structure", {
                                        validate: (value) => {
                                            if (!value) return true
                                            if (typeof value !== 'string') return true
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
                        <Button
                            variant="solid"
                            type="submit"
                            disabled={!isValid}
                            loading={isSubmitting}
                        >
                            Guardar
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </DialogRoot>
    )
}

export default AddPrompt 