import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
    Button,
    DialogActionTrigger,
    DialogTitle,
    Input,
    VStack,
} from "@chakra-ui/react"
import { useEffect, useState } from "react"

import { type ClientPublic, ClientsService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import { FiEdit2 } from "react-icons/fi"
import {
    DialogBody,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogRoot,
    DialogTrigger
} from "../ui/dialog"
import { Field } from "../ui/field"

interface EditClientProps {
    client: ClientPublic
}

const EditClient = ({ client }: EditClientProps) => {
    const [isOpen, setIsOpen] = useState(false)
    const queryClient = useQueryClient()
    const { showSuccessToast } = useCustomToast()
    const {
        register,
        handleSubmit,
        reset,
        formState: { errors, isSubmitting },
    } = useForm<ClientPublic>({
        mode: "onBlur",
        criteriaMode: "all",
        defaultValues: client,
    })

    // Update form values when client prop changes
    useEffect(() => {
        reset(client)
    }, [client, reset])

    const mutation = useMutation({
        mutationFn: (data: ClientPublic) =>
            ClientsService.updateClient({ id: client.id, requestBody: data }),
        onSuccess: () => {
            showSuccessToast("Cliente actualizado correctamente.")
            reset()
            setIsOpen(false)
        },
        onError: (err: ApiError) => {
            handleError(err)
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["clients"] })
        },
    })

    const onSubmit: SubmitHandler<ClientPublic> = async (data) => {
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
                    {/* Editar Cliente */}
                </Button>
            </DialogTrigger>
            <DialogContent>
                <form onSubmit={handleSubmit(onSubmit)}>
                    <DialogHeader>
                        <DialogTitle>Editar Cliente</DialogTitle>
                    </DialogHeader>
                    <DialogBody>
                        <VStack gap={4}>
                            <Field
                                required
                                invalid={!!errors.name}
                                errorText={errors.name?.message}
                                label="Nombre"
                            >
                                <Input
                                    {...register("name", {
                                        required: "El nombre es requerido",
                                    })}
                                />
                            </Field>
                            <Field
                                required
                                invalid={!!errors.clasifier}
                                errorText={errors.clasifier?.message}
                                label="Clasificador"
                            >
                                <Input
                                    {...register("clasifier", {
                                        required: "El clasificador es requerido",
                                    })}
                                />
                            </Field>
                            <Field
                                required
                                invalid={!!errors.structure}
                                errorText={errors.structure?.message}
                                label="Estructura"
                            >
                                <Input
                                    {...register("structure", {
                                        required: "La estructura es requerida",
                                    })}
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
                    {/* <DialogCloseTrigger /> */}
                </form>
            </DialogContent>
        </DialogRoot>
    )
}

export default EditClient 