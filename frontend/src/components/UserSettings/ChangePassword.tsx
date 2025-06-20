import { Box, Button, Heading, VStack } from "@chakra-ui/react"
import { useMutation } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FiLock } from "react-icons/fi"

import { type ApiError, type UpdatePassword, UsersService } from "@/client"
import useCustomToast from "@/hooks/useCustomToast"
import { confirmPasswordRules, handleError, passwordRules } from "@/utils/utils"
import { PasswordInput } from "../ui/password-input"

interface UpdatePasswordForm extends UpdatePassword {
  confirm_password: string
}

const ChangePassword = () => {
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    getValues,
    formState: { errors, isValid, isSubmitting },
  } = useForm<UpdatePasswordForm>({
    mode: "onBlur",
    criteriaMode: "all",
  })

  const mutation = useMutation({
    mutationFn: (data: UpdatePassword) =>
      UsersService.updatePasswordMe({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Contraseña actualizada correctamente.")
      reset()
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
  })

  const onSubmit: SubmitHandler<UpdatePasswordForm> = async (data) => {
    mutation.mutate(data)
  }

  return (
    <Box
      w={{ sm: "full", md: "sm" }}
      as="form"
      onSubmit={handleSubmit(onSubmit)}
    >
      <Heading size="lg" py={4}>
        Cambio de Contraseña
      </Heading>
      <VStack gap={4} w={{ base: "100%", md: "sm" }}>
        <PasswordInput
          type="current_password"
          startElement={<FiLock />}
          {...register("current_password", passwordRules())}
          placeholder="Contraseña actual"
          errors={errors}
        />
        <PasswordInput
          type="new_password"
          startElement={<FiLock />}
          {...register("new_password", passwordRules())}
          placeholder="Nueva contraseña"
          errors={errors}
        />
        <PasswordInput
          type="confirm_password"
          startElement={<FiLock />}
          {...register("confirm_password", confirmPasswordRules(getValues))}
          placeholder="Confirmar contraseña"
          errors={errors}
        />
      </VStack>
      <Button
        variant="solid"
        w="100%"
        mt={4}
        type="submit"
        loading={isSubmitting}
        disabled={!isValid}
      >
        Guardar
      </Button>
    </Box>
  )
}

export default ChangePassword

