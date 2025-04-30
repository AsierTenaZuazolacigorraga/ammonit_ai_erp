import {
  Box,
  Button,
  Checkbox,
  Flex,
  Heading,
  Input,
  Text
} from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
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
  const [editMode, setEditMode] = useState(false)
  const { user: currentUser } = useAuth()
  const {
    register,
    handleSubmit,
    reset,
    getValues,
    formState: { isSubmitting, errors, isDirty },
  } = useForm<UserPublic>({
    mode: "onBlur",
    criteriaMode: "all"
  })

  const toggleEditMode = () => {
    if (!editMode) {
      reset({
        full_name: currentUser?.full_name,
        email: currentUser?.email,
        is_auto_approved: currentUser?.is_auto_approved,
      })
    }
    setEditMode(!editMode)
  }

  const mutation = useMutation({
    mutationFn: (data: UserUpdateMe) =>
      UsersService.updateUserMe({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Usuario actualizado correctamente.")
      setEditMode(false)
      reset()
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

  const onCancel = () => {
    reset()
    toggleEditMode()
  }

  return (
    <Box
      w={{ sm: "full", md: "sm" }}
      as="form"
      onSubmit={handleSubmit(onSubmit)}
    >
      <Heading size="lg" py={4}>
        Información del usuario
      </Heading>
      <Box maxW="sm" borderWidth="1px" borderRadius="lg" p={6}>
        <Field label="Full name">
          {editMode ? (
            <Input
              {...register("full_name", { maxLength: 30 })}
              type="text"
              size="md"
            />
          ) : (
            <Text
              fontSize="md"
              py={2}
              color={!currentUser?.full_name ? "gray" : "inherit"}
              truncate
              maxW="sm"
            >
              {currentUser?.full_name || "N/A"}
            </Text>
          )}
        </Field>
        <Field
          mt={4}
          label="Email"
          invalid={!!errors.email}
          errorText={errors.email?.message}
        >
          {editMode ? (
            <Input
              {...register("email", {
                required: "Email is required",
                pattern: emailPattern,
              })}
              type="email"
              size="md"
            />
          ) : (
            <Text fontSize="md" py={2} truncate maxW="sm">
              {currentUser?.email}
            </Text>
          )}
        </Field>
        <Field
          mt={4}
          label="Aprobación automática"
          invalid={!!errors.is_auto_approved}
          errorText={errors.is_auto_approved?.message}
        >
          {editMode ? (
            <Checkbox.Root
              {...register("is_auto_approved")}
              mt={2}
            >
              <Checkbox.HiddenInput />
              <Checkbox.Control />
              <Checkbox.Label>
                Permitir que la IA apruebe los documentos automáticamente, sin supervisión humana.
              </Checkbox.Label>
            </Checkbox.Root>
          ) : (
            <Checkbox.Root
              checked={currentUser?.is_auto_approved}
              disabled
              mt={2}
            >
              <Checkbox.HiddenInput />
              <Checkbox.Control />
              <Checkbox.Label>
                Permitir que la IA apruebe los documentos automáticamente, sin supervisión humana.
              </Checkbox.Label>
            </Checkbox.Root>
          )}
        </Field>
      </Box>
      <Flex mt={4} gap={3}>
        <Button
          variant="solid"
          onClick={toggleEditMode}
          type={editMode ? "button" : "submit"}
          loading={editMode ? isSubmitting : false}
          disabled={editMode ? !isDirty || !getValues("email") : false}
        >
          {editMode ? "Guardar" : "Editar"}
        </Button>
        {editMode && (
          <Button
            variant="subtle"
            colorPalette="gray"
            onClick={onCancel}
            disabled={isSubmitting}
          >
            Cancelar
          </Button>
        )}
      </Flex>
    </Box>
  )
}

export default UserInformation