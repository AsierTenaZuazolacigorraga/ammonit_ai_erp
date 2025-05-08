import {
  Box,
  Button,
  Checkbox,
  Flex,
  Heading,
  Input
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useEffect } from "react"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
  type ApiError,
  type UserPublic,
  type UserUpdateMe,
  UsersService,
} from "@/client"
import useAuth from "@/hooks/useAuth"
import useCustomToast from "@/hooks/useCustomToast"
import { emailPattern, handleError } from "@/utils"
import { Field } from "../ui/field"

const UserInformation = () => {
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const { user: currentUser } = useAuth()
  const {
    register,
    handleSubmit,
    reset,
    getValues,
    formState: { isSubmitting, errors, isDirty, isValid },
  } = useForm<UserPublic>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      full_name: currentUser?.full_name || "",
      email: currentUser?.email || "",
      is_auto_approved: currentUser?.is_auto_approved || false,
    },
  })

  // Keep form in sync with user data
  useEffect(() => {
    reset({
      full_name: currentUser?.full_name || "",
      email: currentUser?.email || "",
      is_auto_approved: currentUser?.is_auto_approved || false,
    })
  }, [currentUser, reset])

  const mutation = useMutation({
    mutationFn: (data: UserUpdateMe) =>
      UsersService.updateUserMe({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Usuario actualizado correctamente.")
      queryClient.invalidateQueries({ queryKey: ["user"] })
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries()
    },
  })

  const onSubmit: SubmitHandler<UserUpdateMe> = async (data) => {
    mutation.mutate(data)
  }

  return (
    <Box
      w={{ sm: "full", md: "sm" }}
      as="form"
      onSubmit={handleSubmit(onSubmit)}
    >
      <Heading size="lg" py={4}>
        Información del Usuario
      </Heading>
      <Field label="Nombre Completo">
        <Input
          {...register("full_name", { maxLength: 30 })}
          type="text"
          size="md"
        />
      </Field>
      <Field
        mt={4}
        label="Email"
        invalid={!!errors.email}
        errorText={errors.email?.message}
      >
        <Input
          {...register("email", {
            required: "Email is required",
            pattern: emailPattern,
          })}
          type="email"
          size="md"
        />
      </Field>
      <Field
        mt={4}
        label="Aprobación Automática"
        invalid={!!errors.is_auto_approved}
        errorText={errors.is_auto_approved?.message}
      >
        <Checkbox.Root
          {...register("is_auto_approved")}
          mt={2}
          checked={getValues("is_auto_approved")}
        >
          <Checkbox.HiddenInput />
          <Checkbox.Control />
          <Checkbox.Label>
            Permitir que la IA apruebe los documentos automáticamente, sin supervisión humana.
          </Checkbox.Label>
        </Checkbox.Root>
      </Field>
      <Flex mt={4} gap={3}>
        <Button
          variant="solid"
          w="100%"
          mt={0}
          type="submit"
          loading={isSubmitting}
          disabled={!isDirty || !isValid}
        >
          Guardar
        </Button>
      </Flex>
    </Box>
  )
}

export default UserInformation