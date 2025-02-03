import { type ApiError, type UpdatePassword, UsersService } from "@/client"
import { Button } from "@/components/ui/button"
import { Field } from "@/components/ui/field"
import { ReactIcon } from "@/components/ui/icon"
import { InputGroup } from "@/components/ui/input-group"
import useCustomToast from "@/hooks/useCustomToast"
import { confirmPasswordRules, handleError, passwordRules } from "@/utils"
import { Box, Container, Heading, Input } from "@chakra-ui/react"
import { useMutation } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"
import { FaEye, FaEyeSlash } from "react-icons/fa"
import { useBoolean } from "usehooks-ts"

interface UpdatePasswordForm extends UpdatePassword {
  confirm_password: string
}

const ChangePassword = () => {

  const { showSuccessToast } = useCustomToast()
  const { value: showPasswordActual, toggle: togglePasswordActual } = useBoolean()
  const { value: showPasswordNew, toggle: togglePasswordNew } = useBoolean()
  const { value: showPasswordConf, toggle: togglePasswordConf } = useBoolean()

  const {
    register,
    handleSubmit,
    reset,
    getValues,
    formState: { errors, isSubmitting },
  } = useForm<UpdatePasswordForm>({
    mode: "onBlur",
    criteriaMode: "all",
  })

  const mutation = useMutation({
    mutationFn: (data: UpdatePassword) =>
      UsersService.updatePasswordMe({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Password actualizado correctamente.")
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
    <>
      <Container maxW="full">
        <Heading size="sm" py={4}>
          Cambiar Password
        </Heading>
        <Box
          w={{ sm: "full", md: "50%" }}
          as="form"
          onSubmit={handleSubmit(onSubmit)}
        >
          <Field
            label="Password Actual"
            required
            invalid={!!errors.current_password}
            errorText={errors.current_password?.message}
          >
            <InputGroup
              endElement={
                <ReactIcon
                  icon={showPasswordActual ? FaEyeSlash : FaEye}
                  cursor="pointer"
                  onClick={togglePasswordActual}
                  aria-label={showPasswordActual ? "Hide password" : "Show password"}
                />
              }
            >
              <Input
                {...register("current_password")}
                placeholder="Password"
                type={showPasswordActual ? "text" : "password"}
                w="auto"
              />
            </InputGroup>
          </Field>

          <Field
            mt={4}
            label="Nuevo Password"
            required
            invalid={!!errors.new_password}
            errorText={errors.new_password?.message}
          >
            <InputGroup
              endElement={
                <ReactIcon
                  icon={showPasswordNew ? FaEyeSlash : FaEye}
                  cursor="pointer"
                  onClick={togglePasswordNew}
                  aria-label={showPasswordNew ? "Hide password" : "Show password"}
                />
              }
            >
              <Input
                {...register("new_password", passwordRules())}
                placeholder="Password"
                type="password"
                type={showPasswordNew ? "text" : "password"}
                w="auto"
              />
            </InputGroup>
          </Field>
          <Field
            mt={4}
            label="Nuevo Password Confirmado"
            required
            invalid={!!errors.confirm_password}
            errorText={errors.confirm_password?.message}
          >
            <InputGroup
              endElement={
                <ReactIcon
                  icon={showPasswordConf ? FaEyeSlash : FaEye}
                  cursor="pointer"
                  onClick={togglePasswordConf}
                  aria-label={showPasswordConf ? "Hide password" : "Show password"}
                />
              }
            >
              <Input
                {...register("confirm_password", confirmPasswordRules(getValues))}
                placeholder="Password"
                type={showPasswordConf ? "text" : "password"}
                w="auto"
              />
            </InputGroup>
          </Field>
          <Button
            colorPalette="green"
            mt={4}
            type="submit"
            loading={isSubmitting}
          >
            Guardar
          </Button>
        </Box>
      </Container >
    </>
  )
}
export default ChangePassword
