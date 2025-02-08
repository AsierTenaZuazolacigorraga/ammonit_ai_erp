import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import {
  DialogBackdrop,
  DialogBody,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle
} from "@/components/ui/dialog"
import { Field } from "@/components/ui/field"
import { Flex, Input } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { Controller, type SubmitHandler, useForm } from "react-hook-form"

import {
  type ApiError,
  type UserPublic,
  type UserUpdate,
  UsersService,
} from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { emailPattern, handleError } from "@/utils"

interface EditUserProps {
  user: UserPublic
  open: boolean
  onClose: () => void
}

interface UserUpdateForm extends UserUpdate {
  confirm_password: string
}

const EditUser = ({ user, open, onClose }: EditUserProps) => {
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()

  const {
    register,
    control,
    handleSubmit,
    reset,
    getValues,
    formState: { errors, isSubmitting },
  } = useForm<UserUpdateForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: user,
  })

  const mutation = useMutation({
    mutationFn: (data: UserUpdateForm) =>
      UsersService.updateUser({ id: user.id, requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Usuario actualizado correctamente.")
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] })
    },
  })

  const onSubmit: SubmitHandler<UserUpdateForm> = async (data) => {
    if (data.password === "") {
      data.password = undefined
    }
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
        role="alertdialog"
      >
        <DialogBackdrop />
        <DialogContent as="form" onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Editar Usuario</DialogTitle>
            {/* <DialogCloseTrigger /> */}
          </DialogHeader>
          <DialogBody pb={6}>
            <Field
              label="Email"
              invalid={!!errors.email}
              errorText={errors.email?.message}
            >
              <Input
                {...register("email", {
                  required: "Se requiere email",
                  pattern: emailPattern,
                })}
                placeholder="Email"
                type="email"
              />
            </Field>
            <Field mt={4} label="Nombre completo">
              <Input {...register("full_name")} type="text" />
            </Field>
            <Field
              mt={4}
              label="Nuevo Password"
              invalid={!!errors.password}
              errorText={errors.password?.message}
            >
              <Input
                {...register("password", {
                  minLength: {
                    value: 8,
                    message: "El password debe de tener al menos 8 caracteres",
                  },
                })}
                placeholder="Password"
                type="password"
              />
            </Field>
            <Field
              mt={4}
              label="Nuevo Password Confirmado"
              invalid={!!errors.confirm_password}
              errorText={errors.confirm_password?.message}
            >
              <Input
                {...register("confirm_password", {
                  validate: (value) =>
                    value === getValues().password ||
                    "Las contraseñas no coinciden",
                })}
                placeholder="Password"
                type="password"
              />
            </Field>
            <Flex mt={4}>
              <Controller
                control={control}
                name="is_superuser"
                render={({ field }) => (
                  <Field
                    disabled={field.disabled}
                    invalid={!!errors.is_superuser}
                    errorText={errors.is_superuser?.message}
                  >
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={({ checked }) => field.onChange(checked)}
                    >
                      Es superuser?
                    </Checkbox>
                  </Field>
                )}
              />
              <Controller
                control={control}
                name="is_active"
                render={({ field }) => (
                  <Field
                    disabled={field.disabled}
                    invalid={!!errors.is_active}
                    errorText={errors.is_active?.message}
                  >
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={({ checked }) => field.onChange(checked)}
                    >
                      Es active?
                    </Checkbox>
                  </Field>
                )}
              />
            </Flex>
          </DialogBody>

          <DialogFooter gap={3}>
            <Button
              colorPalette="green"
              type="submit"
              loading={isSubmitting}
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

export default EditUser
