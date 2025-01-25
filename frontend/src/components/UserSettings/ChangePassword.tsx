import { ViewIcon, ViewOffIcon } from "@chakra-ui/icons"
import {
  Box,
  Button,
  Container,
  FormControl,
  FormErrorMessage,
  FormLabel,
  Heading,
  Icon,
  Input,
  InputGroup,
  InputRightElement,
  useBoolean,
  useColorModeValue
} from "@chakra-ui/react"
import { useMutation } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import { type ApiError, type UpdatePassword, UsersService } from "../../client"
import useCustomToast from "../../hooks/useCustomToast"
import { confirmPasswordRules, handleError, passwordRules } from "../../utils"

interface UpdatePasswordForm extends UpdatePassword {
  confirm_password: string
}

const ChangePassword = () => {
  const [showCurrentPass, setShowCurrentPass] = useBoolean()
  const [showNewPass, setShowNewPass] = useBoolean()
  const [showConfirmPass, setShowConfirmPass] = useBoolean()
  const color = useColorModeValue("inherit", "ui.light")
  const showToast = useCustomToast()
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
      showToast("Éxito!", "Password actualizado correctamente.", "success")
      reset()
    },
    onError: (err: ApiError) => {
      handleError(err, showToast)
    },
  })

  const onSubmit: SubmitHandler<UpdatePasswordForm> = async (data) => {
    mutation.mutate(data)
  }

  return (
    <>
      <Container maxW="full">
        <Heading size="sm" py={4}>
          Cabiar Password
        </Heading>
        <Box
          w={{ sm: "full", md: "50%" }}
          as="form"
          onSubmit={handleSubmit(onSubmit)}
        >
          <FormControl isRequired isInvalid={!!errors.current_password}>
            <FormLabel color={color} htmlFor="current_password">
              Password Actual
            </FormLabel>
            <InputGroup width='50%'>
              <Input
                id="current_password"
                {...register("current_password")}
                placeholder="Password"
                type={showCurrentPass ? "text" : "password"}
              // w="auto"
              />
              <InputRightElement
                color="ui.dim"
                _hover={{
                  cursor: "pointer",
                }}
              >
                <Icon
                  as={showCurrentPass ? ViewOffIcon : ViewIcon}
                  onClick={setShowCurrentPass.toggle}
                  aria-label={showCurrentPass ? "Hide password" : "Show password"}
                >
                  {showCurrentPass ? <ViewOffIcon /> : <ViewIcon />}
                </Icon>
              </InputRightElement>
            </InputGroup>
            {errors.current_password && (
              <FormErrorMessage>
                {errors.current_password.message}
              </FormErrorMessage>
            )}
          </FormControl>
          <FormControl mt={4} isRequired isInvalid={!!errors.new_password}>
            <FormLabel htmlFor="password">Nuevo Password</FormLabel>
            <InputGroup width='50%'>
              <Input
                id="password"
                {...register("new_password", passwordRules())}
                placeholder="Password"
                type={showNewPass ? "text" : "password"}
              // w="auto"
              />
              <InputRightElement
                color="ui.dim"
                _hover={{
                  cursor: "pointer",
                }}
              >
                <Icon
                  as={showNewPass ? ViewOffIcon : ViewIcon}
                  onClick={setShowNewPass.toggle}
                  aria-label={showNewPass ? "Hide password" : "Show password"}
                >
                  {showNewPass ? <ViewOffIcon /> : <ViewIcon />}
                </Icon>
              </InputRightElement>
            </InputGroup>
            {errors.new_password && (
              <FormErrorMessage>{errors.new_password.message}</FormErrorMessage>
            )}
          </FormControl>
          <FormControl mt={4} isRequired isInvalid={!!errors.confirm_password}>
            <FormLabel htmlFor="confirm_password">Nuevo Password Confirmado</FormLabel>
            <InputGroup width='50%'>
              <Input
                id="confirm_password"
                {...register("confirm_password", confirmPasswordRules(getValues))}
                placeholder="Password"
                type={showConfirmPass ? "text" : "password"}
              // w="auto"
              />
              <InputRightElement
                color="ui.dim"
                _hover={{
                  cursor: "pointer",
                }}
              >
                <Icon
                  as={showConfirmPass ? ViewOffIcon : ViewIcon}
                  onClick={setShowConfirmPass.toggle}
                  aria-label={showConfirmPass ? "Hide password" : "Show password"}
                >
                  {showConfirmPass ? <ViewOffIcon /> : <ViewIcon />}
                </Icon>
              </InputRightElement>
            </InputGroup>
            {errors.confirm_password && (
              <FormErrorMessage>
                {errors.confirm_password.message}
              </FormErrorMessage>
            )}
          </FormControl>
          <Button
            variant="primary"
            mt={4}
            type="submit"
            isLoading={isSubmitting}
          >
            Guardar
          </Button>
        </Box>
      </Container>
    </>
  )
}
export default ChangePassword
