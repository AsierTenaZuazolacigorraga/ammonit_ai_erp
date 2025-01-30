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

import { type UserCreate, UsersService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
import { emailPattern, handleError } from "@/utils"

interface AddUserProps {
  open: boolean
  onClose: () => void
}

interface UserCreateForm extends UserCreate {
  confirm_password: string
}

const AddUser = ({ open, onClose }: AddUserProps) => {

  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()

  const {
    register,
    control,
    handleSubmit,
    reset,
    getValues,
    formState: { isSubmitting, errors },
  } = useForm<UserCreateForm>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      email: "",
      full_name: "",
      password: "",
      confirm_password: "",
      is_superuser: false,
      is_active: false,
    },
  })

  const mutation = useMutation({
    mutationFn: (data: UserCreate) =>
      UsersService.createUser({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Usuario creado correctamente.")
      reset()
      onClose()
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["users"] })
    },
  })

  const onSubmit: SubmitHandler<UserCreateForm> = (data) => {
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
            <DialogTitle>Añadir Usuario</DialogTitle>
            {/* <DialogCloseTrigger /> */}
          </DialogHeader>
          <DialogBody pb={6}>
            <Field
              required
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
            <Field
              mt={4}
              label="Nombre completo"
              invalid={!!errors.full_name}
              errorText={errors.full_name?.message}
            >
              <Input
                {...register("full_name")}
                placeholder="Nombre completo"
                type="text"
              />
            </Field>
            <Field
              mt={4}
              label="Nuevo Password"
              required
              invalid={!!errors.password}
              errorText={errors.password?.message}
            >
              <Input
                {...register("password", {
                  required: "Se requiere password",
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
              required
              label="Nuevo Password Confirmado"
              invalid={!!errors.confirm_password}
              errorText={errors.confirm_password?.message}
            >
              <Input
                {...register("confirm_password", {
                  required: "Por favor, confirme su password",
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
            <Button colorPalette="green" type="submit" loading={isSubmitting} >
              Guardar
            </Button>
            <Button onClick={onClose}>Cancelar</Button>
          </DialogFooter>
        </DialogContent>
      </DialogRoot>
    </>
  )
}

export default AddUser
