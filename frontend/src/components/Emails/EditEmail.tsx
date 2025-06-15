import { EmailsService, type ApiError, type EmailPublic } from "@/client"
import {
    DialogBody,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogRoot,
    DialogTrigger
} from "@/components/ui/dialog"
import { Field } from "@/components/ui/field"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import {
    Button,
    Checkbox,
    DialogActionTrigger,
    DialogTitle,
    Textarea,
    VStack,
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { Controller, useForm } from "react-hook-form"
import { FiEdit2 } from "react-icons/fi"

interface EditEmailProps {
    email: EmailPublic
}

interface EmailUpdateForm {
    is_orders: boolean
    is_orders_active: boolean
    is_offers: boolean
    is_offers_active: boolean
    orders_filter?: string
    offers_filter?: string
}

const EditEmail = ({ email }: EditEmailProps) => {
    const [isOpen, setIsOpen] = useState(false)
    const queryClient = useQueryClient()
    const { showSuccessToast } = useCustomToast()
    const {
        handleSubmit,
        formState: { errors, isSubmitting },
        control,
        register,
    } = useForm<EmailUpdateForm>({
        mode: "onBlur",
        criteriaMode: "all",
        defaultValues: {
            is_orders: email.is_orders ?? false,
            is_offers: email.is_offers ?? false,
            orders_filter: email.orders_filter ?? "",
            offers_filter: email.offers_filter ?? "",
        },
    })

    const mutation = useMutation({
        mutationFn: (data: EmailUpdateForm) =>
            EmailsService.updateEmail({
                id: email.id,
                requestBody: {
                    email: email.email,
                    is_orders: data.is_orders,
                    is_offers: data.is_offers,
                    orders_filter: data.orders_filter,
                    offers_filter: data.offers_filter,
                }
            }),
        onSuccess: () => {
            showSuccessToast("Email actualizado correctamente.")
            setIsOpen(false)
        },
        onError: (err: ApiError) => {
            handleError(err)
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["emails"] })
        },
    })

    const onSubmit = (data: EmailUpdateForm) => {
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
                </Button>
            </DialogTrigger>
            <DialogContent>
                <form onSubmit={handleSubmit(onSubmit)}>
                    <DialogHeader>
                        <DialogTitle>Editar Email</DialogTitle>
                    </DialogHeader>
                    <DialogBody>
                        <VStack gap={4}>
                            <Field
                                label=""
                                invalid={!!errors.is_orders}
                                errorText={errors.is_orders?.message}
                            >
                                <Controller
                                    name="is_orders"
                                    control={control}
                                    render={({ field }) => {
                                        return (
                                            <Checkbox.Root
                                                mt={2}
                                                checked={!!field.value}
                                                onCheckedChange={val => {
                                                    field.onChange(val.checked)
                                                }}
                                            >
                                                <Checkbox.HiddenInput />
                                                <Checkbox.Control />
                                                <Checkbox.Label>
                                                    Se desea recibir/manejar pedidos mediante este email, y gestionarlos mediante AI
                                                </Checkbox.Label>
                                            </Checkbox.Root>
                                        )
                                    }}
                                />
                            </Field>
                            <Field
                                label="Filtros para Pedidos"
                                invalid={!!errors.orders_filter}
                                errorText={errors.orders_filter?.message}
                            >
                                <Textarea
                                    id="orders_filter"
                                    {...register("orders_filter")}
                                    placeholder="Filtros para pedidos (opcional si quires procesar solamete algunos emails)"
                                    rows={4}
                                    minH="100px"
                                />
                            </Field>
                            <Field
                                label=""
                                invalid={!!errors.is_offers}
                                errorText={errors.is_offers?.message}
                            >
                                <Controller
                                    name="is_offers"
                                    control={control}
                                    render={({ field }) => {
                                        return (
                                            <Checkbox.Root
                                                mt={2}
                                                checked={!!field.value}
                                                onCheckedChange={val => {
                                                    field.onChange(val.checked)
                                                }}
                                            >
                                                <Checkbox.HiddenInput />
                                                <Checkbox.Control />
                                                <Checkbox.Label>
                                                    Se desea recibir/manejar ofertas mediante este email, y gestionarlas mediante AI
                                                </Checkbox.Label>
                                            </Checkbox.Root>
                                        )
                                    }}
                                />
                            </Field>
                            <Field
                                label="Filtros para Ofertas"
                                invalid={!!errors.offers_filter}
                                errorText={errors.offers_filter?.message}
                            >
                                <Textarea
                                    id="offers_filter"
                                    {...register("offers_filter")}
                                    placeholder="Filtros para ofertas (opcional si quires procesar solamete algunos emails)"
                                    rows={4}
                                    minH="100px"
                                />
                            </Field>
                        </VStack>
                    </DialogBody>
                    <DialogFooter gap={2}>
                        {!(isSubmitting || mutation.isPending) && (
                            <DialogActionTrigger asChild>
                                <Button
                                    variant="subtle"
                                    colorPalette="gray"
                                    disabled={isSubmitting}
                                >
                                    Cancelar
                                </Button>
                            </DialogActionTrigger>
                        )}
                        <Button
                            variant="solid"
                            type="submit"
                            loading={isSubmitting || mutation.isPending}
                            loadingText="Procesando..."
                        >
                            Guardar
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </DialogRoot>
    )
}

export default EditEmail 