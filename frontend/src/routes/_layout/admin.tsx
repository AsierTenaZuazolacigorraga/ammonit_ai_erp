import { Badge, Container, Heading } from "@chakra-ui/react"
import {
  useQueryClient,
  type UseQueryOptions,
} from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { z } from "zod"

import { ApiError, UsersService, type UserPublic } from "@/client"
import AddUser from "@/components/Admin/AddUser"
import { DataTable, type Column, type PaginatedData } from "@/components/Common/DataTable"
import { UserActionsMenu } from "@/components/Common/UserActionsMenu"

// Schema
const usersSearchSchema = z.object({
  page: z.number().int().positive().catch(1),
})
type UsersSearch = z.infer<typeof usersSearchSchema>

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

// Route definition
export const Route = createFileRoute("/_layout/admin")({
  component: Admin,
  validateSearch: (search: Record<string, unknown>): UsersSearch =>
    usersSearchSchema.parse(search),
})

// Main component
function Admin() {
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])

  // Define columns here
  const columns: Column<UserPublic>[] = [
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
      header: "Estado",
      accessor: (user) => (user.is_active ? "Activo" : "Inactivo"),
    },
    {
      header: "Acciones",
      accessor: (user) => (
        <UserActionsMenu
          user={user}
          disabled={currentUser?.id === user.id}
        />
      ),
    },
  ]

  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>
        Gestión de Usuarios
      </Heading>
      <AddUser />
      <DataTable
        queryKeyBase="users"
        baseQueryOptionsFn={baseUsersQueryOptionsFn}
        searchSchema={usersSearchSchema}
        route={Route}
        columns={columns}
        emptyStateTitle="No hay usuarios"
        emptyStateDescription="No hay usuarios registrados en el sistema"
        pageSize={PER_PAGE}
      />
    </Container>
  )
}
