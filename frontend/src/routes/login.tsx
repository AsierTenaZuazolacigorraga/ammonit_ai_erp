import { Button } from "@/components/ui/button"
import { Field } from "@/components/ui/field"
import { ReactIcon } from "@/components/ui/icon"
import { InputGroup } from "@/components/ui/input-group"
import { Container, Image, Input } from "@chakra-ui/react"
import { createFileRoute, redirect } from "@tanstack/react-router"
import { type SubmitHandler, useForm } from "react-hook-form"

import { FaEye, FaEyeSlash } from "react-icons/fa"
import { useBoolean } from "usehooks-ts"
import type { Body_login_login_access_token as AccessToken } from "../client"
import useAuth, { isLoggedIn } from "../hooks/useAuth"
import { emailPattern } from "../utils"
import Logo from "/assets/images/ammonit_generic_logo.svg"

export const Route = createFileRoute("/login")({
  component: Login,
  beforeLoad: async () => {
    if (isLoggedIn()) {
      throw redirect({
        to: "/",
      })
    }
  },
})

function Login() {
  const { value: show, toggle } = useBoolean()
  const { loginMutation, error, resetError } = useAuth()
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<AccessToken>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      username: "",
      password: "",
    },
  })

  const onSubmit: SubmitHandler<AccessToken> = async (data) => {
    if (isSubmitting) return

    resetError()

    try {
      await loginMutation.mutateAsync(data)
    } catch {
      // error is handled by useAuth hook
    }
  }

  return (
    <>
      <Container
        as="form"
        onSubmit={handleSubmit(onSubmit)}
        h="100vh"
        maxW="sm"
        alignItems="stretch"
        justifyContent="center"
        gap={4}
        centerContent
      >
        <Image
          src={Logo}
          alt="FastAPI logo"
          height="auto"
          maxW="2xs"
          alignSelf="center"
          mb={4}
        />
        <Field
          invalid={!!errors.username || !!error}
          errorText={errors.username?.message}
        >
          <Input
            {...register("username", {
              required: "Se requiere email",
              pattern: emailPattern,
            })}
            placeholder="Email"
            type="email"
            required
          />
        </Field>
        <Field invalid={!!error} errorText={error}>
          <InputGroup
            width="100%"
            endElement={
              <ReactIcon
                icon={show ? FaEyeSlash : FaEye}
                cursor="pointer"
                onClick={toggle}
                aria-label={show ? "Hide password" : "Show password"}
              />
            }
          >
            <Input
              {...register("password", {
                required: "Se requiere password",
              })}
              type={show ? "text" : "password"}
              placeholder="Password"
              required
            />
          </InputGroup>
        </Field>
        {/* <RouterLink to="/recover-password" color="blue.500">
          Forgot password?
        </RouterLink> */}
        <Button colorPalette="green" type="submit" loading={isSubmitting}>
          Log In
        </Button>
        {/* <Text>
          Don't have an account?{" "}
          <RouterLink to="/signup" color="blue.500">
            Sign up
          </RouterLink>
        </Text> */}
      </Container>
    </>
  )
}
