import { Field } from "@/components/ui/field"
import { Box, Container, Heading, Input, Text } from "@chakra-ui/react"
import { useForm } from "react-hook-form"

import {
  type UserPublic
} from "@/client"
import useAuth from "@/hooks/useAuth"
import { emailPattern } from "@/utils"
import { useState } from "react"

const UserInformation = () => {
  // const queryClient = useQueryClient()
  // const { showSuccessToast } = useCustomToast()
  // const [editMode, setEditMode] = useState(false)
  const [editMode] = useState(false)
  const { user: currentUser } = useAuth()
  const {
    register,
    // handleSubmit,
    // reset,
    // formState: { isSubmitting, errors },
    formState: { errors },
  } = useForm<UserPublic>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      full_name: currentUser?.full_name,
      email: currentUser?.email,
    },
  })

  // const toggleEditMode = () => {
  //   setEditMode(!editMode)
  // }

  // const mutation = useMutation({
  //   // mutationFn: (data: UserUpdateMe) =>
  //   //   UsersService.updateUserMe({ requestBody: data }),
  //   onSuccess: () => {
  //     showSuccessToast("Usuario actualizado correctamente.")
  //   },
  //   onError: (err: ApiError) => {
  //     handleError(err)
  //   },
  //   onSettled: () => {
  //     queryClient.invalidateQueries()
  //   },
  // })

  // const onSubmit: SubmitHandler<UserUpdateMe> = async (data) => {
  //   mutation.mutate(data)
  // }

  // const onCancel = () => {
  //   reset()
  //   toggleEditMode()
  // }

  return (
    <>
      <Container maxW="full">
        <Heading size="sm" py={4}>
          Información de Usuario
        </Heading>
        <Box
          w={{ sm: "full", md: "50%" }}
          as="form"
        // onSubmit={handleSubmit(onSubmit)}
        >
          <Field label="Nombre completo">
            {editMode ? (
              <Input
                {...register("full_name", { maxLength: 30 })}
                type="text"
                size="md"
                w="auto"
              />
            ) : (
              <Text
                fontSize="md"
                py={2}
                color={!currentUser?.full_name ? "gray" : "inherit"}
                truncate
                maxWidth="250px"
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
                  required: "Se requiere email",
                  pattern: emailPattern,
                })}
                type="email"
                size="md"
                w="auto"
              />
            ) : (
              <Text fontSize="md" py={2} truncate maxWidth="250px">
                {currentUser?.email}
              </Text>
            )}
          </Field>
          {/* <Flex mt={4} gap={3}>
            <Button
              colorPalette="green"
              onClick={toggleEditMode}
              type={editMode ? "button" : "submit"}
              loading={editMode ? isSubmitting : false}
            // disabled={editMode ? !isDirty || !getValues("email") : false}
            >
              {editMode ? "Guardar" : "Editar"}
            </Button>
            {editMode && (
              <Button onClick={onCancel} disabled={isSubmitting}>
                Cancel
              </Button>
            )}
          </Flex> */}
        </Box>
      </Container>
    </>
  )
}

export default UserInformation
