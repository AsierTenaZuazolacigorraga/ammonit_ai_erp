import {
  DialogBackdrop,
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
} from "@/components/ui/dialog"
import { Field } from "@/components/ui/field"
import { Input } from "@chakra-ui/react"

import { Button } from "@/components/ui/button"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import { type ApiError, type OrderCreate, OrdersService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface AddOrderProps {
  open: boolean
  onClose: () => void
}

const AddOrder = ({ open, onClose }: AddOrderProps) => {
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<OrderCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      in_document: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: OrderCreate) =>
      OrdersService.createOrder({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Order created successfully.")
      reset()
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["orders"] })
    },
  })

  const onSubmit: SubmitHandler<OrderCreate> = (data) => {
    mutation.mutate(data)
  }

  return (
    <>
      <DialogRoot
        open={open}
        onExitComplete={onClose}
        size={{ base: "sm", md: "md" }}
      >
        <DialogBackdrop />
        <DialogContent as="form" onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Añadir Pedido</DialogTitle>
            <DialogCloseTrigger />
          </DialogHeader>
          <DialogBody pb={6}>
            <Field
              label="Documento de Pedido"
              required
              invalid={!!errors.in_document}
              errorText={errors.in_document?.message}
            >
              <Input
                {...register("in_document", {
                  required: "Se requiere el documento de pedido.",
                })}
                placeholder="Title"
                type="text"
              />
            </Field>
          </DialogBody>

          <DialogFooter gap={3}>
            <Button colorPalette="blue" type="submit" loading={isSubmitting}>
              Guardar
            </Button>
            <Button onClick={onClose}>Cancelar</Button>
          </DialogFooter>
        </DialogContent>
      </DialogRoot>
    </>
  )
}

export default AddOrder
