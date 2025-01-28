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

import { type ApiError, UsersService } from "@/client"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"

interface DeleteProps {
  open: boolean
  onClose: () => void
}

const DeleteConfirmation = ({ open, onClose }: DeleteProps) => {
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    handleSubmit,
    formState: { isSubmitting },
  } = useForm()
  const { logout } = useAuth()

  const mutation = useMutation({
    mutationFn: () => UsersService.deleteUserMe(),
    onSuccess: () => {
      showSuccessToast("Su cuenta se ha eliminado con éxito.")
      logout()
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["currentUser"] })
    },
  })

  const onSubmit = async () => {
    mutation.mutate()
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
            <DialogTitle>Se Requiere Confirmación</DialogTitle>
            {/* <DialogCloseTrigger /> */}
          </DialogHeader>
          <DialogBody>
            Todos los datos de su cuenta <strong>se eliminarán permanentemente.</strong>{" "}
            Si está seguro, por fabor, clicke en <strong>"Confirmar"</strong>.
            Esta acción no se podrá deshacer.
          </DialogBody>

          <DialogFooter gap={3}>
            <Button colorPalette="red" type="submit" loading={isSubmitting}>
              Confirmar
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

export default DeleteConfirmation
