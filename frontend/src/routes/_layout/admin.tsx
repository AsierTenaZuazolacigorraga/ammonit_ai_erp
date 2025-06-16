import { Badge, Container, Heading, HStack } from "@chakra-ui/react"
import { UseQueryOptions } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { z } from "zod"

import { ApiError, PromptsService, UsersService, type PromptPublic, type UserPublic } from "@/client"
import AddPrompt from "@/components/Admin/AddPrompt"
import AddUser from "@/components/Admin/AddUser"
import DeletePrompt from "@/components/Admin/DeletePrompt"
import DeleteUser from "@/components/Admin/DeleteUser"
import EditPrompt from "@/components/Admin/EditPrompt"
import EditUser from "@/components/Admin/EditUser"
import { DataTable, type Column, type PaginatedData } from "@/components/Common/DataTable"
import useAuth from "@/hooks/useAuth"

// Schema
const usersSearchSchema = z.object({
  page: z.number().int().positive().catch(1),
})
type UsersSearch = z.infer<typeof usersSearchSchema>

const promptsSearchSchema = z.object({
  page: z.number().int().positive().catch(1),
})
type PromptsSearch = z.infer<typeof promptsSearchSchema>

const PER_PAGE = 10

// Base query options function
const baseUsersQueryOptionsFn = (
  search: UsersSearch
): Omit<
  UseQueryOptions<PaginatedData<UserPublic>, ApiError, PaginatedData<UserPublic>>,
  "queryKey"
> => {
  return {
    queryFn: () =>
      UsersService.readUsers({
        skip: (search.page - 1) * PER_PAGE,
        limit: PER_PAGE,
      }),
  }
}

const basePromptsQueryOptionsFn = (
  search: PromptsSearch
): Omit<
  UseQueryOptions<PaginatedData<PromptPublic>, ApiError, PaginatedData<PromptPublic>>,
  "queryKey"
> => {
  return {
    queryFn: () =>
      PromptsService.readPrompts({
        skip: (search.page - 1) * PER_PAGE,
        limit: PER_PAGE,
      }),
  }
}

// Route definition
export const Route = createFileRoute("/_layout/admin")({
  component: Admin,
  validateSearch: (search: Record<string, unknown>): UsersSearch =>
    usersSearchSchema.parse(search),
})

// Main component
function Admin() {
  const { user: currentUser } = useAuth()

  // Define columns here
  const userColumns: Column<UserPublic>[] = [
    {
      header: "Acciones",
      width: "120px",
      accessor: (user) => (
        <HStack gap={2}>
          <DeleteUser id={user.id} disabled={currentUser?.id === user.id} />
          <EditUser user={user} />
        </HStack>
      )
    },
    {
      header: "Nombre",
      accessor: (user) => (
        <>
          <span style={{ color: !user.full_name ? "gray" : "inherit" }}>
            {user.full_name || "-"}
          </span>
          {currentUser?.id === user.id && (
            <Badge ml="1" colorScheme="teal">
              Tú
            </Badge>
          )}
        </>
      ),
    },
    {
      header: "Email",
      accessor: (user) => user.email,
    },
    {
      header: "Rol",
      accessor: (user) => (user.is_superuser ? "Superuser" : "Usuario"),
    },
    {
      header: "Habilitado",
      accessor: (user) => (user.is_active ? "Sí" : "No"),
    },
    {
      header: "Prompts Orders Additional Rules",
      accessor: (user) => user.prompts_orders_additional_rules || "-",
    },
    {
      header: "Prompts Orders Particular Rules",
      accessor: (user) => user.prompts_orders_particular_rules || "-",
    },
  ]

  const promptColumns: Column<PromptPublic>[] = [
    {
      header: "Acciones",
      width: "120px",
      accessor: (prompt) => (
        <HStack gap={2}>
          <DeletePrompt id={prompt.id} />
          <EditPrompt prompt={prompt} />
        </HStack>
      )
    },
    {
      header: "Version",
      accessor: (prompt) => prompt.version || "1",
    },
    {
      header: "Query",
      accessor: (prompt) => prompt.query || "-",
    },
    {
      header: "Service",
      accessor: (prompt) => prompt.service || "-",
    },
    {
      header: "Model",
      accessor: (prompt) => prompt.model || "-",
    },
    {
      header: "Prompt",
      accessor: (prompt) => prompt.prompt || "-",
    },
    {
      header: "Structure",
      accessor: (prompt) => JSON.stringify(prompt.structure) || "-",
    },
  ]

  return (
    <Container maxW="full">
      <Heading size="lg" py={6}>
        Gestión de Usuarios
      </Heading>
      <AddUser />
      <DataTable
        queryKeyBase="users"
        baseQueryOptionsFn={baseUsersQueryOptionsFn}
        searchSchema={usersSearchSchema}
        route={Route}
        columns={userColumns}
        emptyStateTitle="No hay usuarios"
        emptyStateDescription="No hay usuarios registrados en el sistema"
        pageSize={PER_PAGE}
      />
      <Heading size="lg" py={6}>
        Gestión de Prompts
      </Heading>
      <AddPrompt />
      <DataTable
        queryKeyBase="prompts"
        baseQueryOptionsFn={basePromptsQueryOptionsFn}
        searchSchema={promptsSearchSchema}
        route={Route}
        columns={promptColumns}
        emptyStateTitle="No hay prompts"
        emptyStateDescription="No hay prompts registrados en el sistema"
        pageSize={PER_PAGE}
      />
    </Container>
  )
}
