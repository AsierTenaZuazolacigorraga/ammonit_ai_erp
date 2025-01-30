import { Button } from "@/components/ui/button"
import {
  DialogBackdrop,
  DialogBody,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle
} from "@/components/ui/dialog"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useForm } from "react-hook-form"

import { OrdersService, UsersService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"

interface DeleteProps {
  type: string
  id: string
  open: boolean
  onClose: () => void
}

const Delete = ({ type, id, open, onClose }: DeleteProps) => {
  const queryClient = useQueryClient()
  const { showSuccessToast, showErrorToast } = useCustomToast()
  const {
    handleSubmit,
    formState: { isSubmitting },
  } = useForm()

  const deleteEntity = async (id: string) => {
    if (type === "Pedido") {
      await OrdersService.deleteOrder({ id })
    } else if (type === "Usuario") {
      await UsersService.deleteUser({ userId: id })
    } else {
      throw new Error(`Unexpected type: ${type}`)
    }
  }

  const mutation = useMutation({
    mutationFn: deleteEntity,
    onSuccess: () => {
      showSuccessToast(`Se ha eliminado correctamente: ${type.toLowerCase()}.`)
      onClose()
    },
    onError: () => {
      showErrorToast(
        `Ha ocurrido algún error al eliminar: ${type.toLowerCase()}.`,
      )
    },
    onSettled: () => {
      queryClient.invalidateQueries({
        queryKey: [type === "Pedido" ? "orders" : "users"],
      })
    },
  })

  const onSubmit = async () => {
    mutation.mutate(id)
  }

  return (
    <>
      <DialogRoot
        open={open}
        onExitComplete={onClose}
        size={{ base: "sm", md: "md" }}
        role="alertdialog"
      >
        <DialogBackdrop />
        <DialogContent as="form" onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Eliminar {type}</DialogTitle>
            {/* <DialogCloseTrigger /> */}
          </DialogHeader>

          <DialogBody>
            {type === "Usuario" && (
              <span>
                Todo lo relacionado con el usuario también será{" "}
                <strong>eliminado permanentemente. </strong>
              </span>
            )}
            Estás seguro? No se va a poder deshacer esta acción.
          </DialogBody>

          <DialogFooter gap={3}>
            <Button colorPalette="red" type="submit" loading={isSubmitting}>
              Eliminar
            </Button>
            <Button onClick={onClose} disabled={isSubmitting}>
              Cancelar
            </Button>
          </DialogFooter>
        </DialogContent>
      </DialogRoot>
    </>
  )
}

export default Delete
