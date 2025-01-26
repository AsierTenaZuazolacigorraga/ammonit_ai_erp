import { Input } from "@chakra-ui/react"

import { Field } from "@/components/ui/field"

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

import { Button } from "@/components/ui/button"

import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
  type ApiError,
  type OrderPublic,
  type OrderUpdate,
  OrdersService,
} from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface EditOrderProps {
  order: OrderPublic
  open: boolean
  onClose: () => void
}

const EditOrder = ({ order, open, onClose }: EditOrderProps) => {
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    formState: { isSubmitting, errors, isDirty },
  } = useForm<OrderUpdate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: order,
  })

  const mutation = useMutation({
    mutationFn: (data: OrderUpdate) =>
      OrdersService.updateOrder({ id: order.id, requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Order updated successfully.")
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["orders"] })
    },
  })

  const onSubmit: SubmitHandler<OrderUpdate> = async (data) => {
    mutation.mutate(data)
  }

  const onCancel = () => {
    reset()
    onClose()
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
            <DialogTitle>Editar Pedido</DialogTitle>
            <DialogCloseTrigger />
          </DialogHeader>
          <DialogBody pb={6}>
            <Field
              label="Title"
              invalid={!!errors.in_document}
              errorText={errors.in_document?.message}
            >
              <Input
                {...register("in_document", {
                  required: "Se requiere el documento de pedido",
                })}
                type="text"
              />
            </Field>
          </DialogBody>
          <DialogFooter gap={3}>
            <Button
              colorPalette="blue"
              type="submit"
              loading={isSubmitting}
              disabled={!isDirty}
            >
              Guardar
            </Button>
            <Button onClick={onCancel}>Cancelar</Button>
          </DialogFooter>
        </DialogContent>
      </DialogRoot>
    </>
  )
}

export default EditOrder
