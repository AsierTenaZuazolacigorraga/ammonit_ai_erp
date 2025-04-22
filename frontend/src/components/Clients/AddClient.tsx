import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
    Button,
    DialogActionTrigger,
    DialogTitle,
    Input,
    VStack
} from "@chakra-ui/react"
import { useState } from "react"
import { FaPlus } from "react-icons/fa"

import { type ClientCreate, ClientsService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
    DialogBody,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogRoot,
    DialogTrigger
} from "../ui/dialog"
import { Field } from "../ui/field"

const AddClient = () => {
    const [isOpen, setIsOpen] = useState(false)
    const queryClient = useQueryClient()
    const { showSuccessToast } = useCustomToast()
    const {
        register,
        handleSubmit,
        reset,
        formState: { errors, isSubmitting },
    } = useForm<ClientCreate>({
        mode: "onBlur",
        criteriaMode: "all"
    })

    const mutation = useMutation({
        mutationFn: (data: ClientCreate) =>
            ClientsService.createClient({ requestBody: data }),
        onSuccess: () => {
            showSuccessToast("Cliente creado correctamente.")
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

    const onSubmit: SubmitHandler<ClientCreate> = async (data) => {
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
                <Button value="add-client" my={4}>
                    <FaPlus fontSize="16px" />
                    Añadir Cliente
                </Button>
            </DialogTrigger>
            <DialogContent>
                <DialogHeader>
                    <DialogTitle>Añadir Cliente</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSubmit(onSubmit)}>
                    <DialogBody>
                        <VStack gap={4}>
                            <Field
                                required
                                invalid={!!errors.name}
                                errorText={errors.name?.message}
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

export default AddClient 