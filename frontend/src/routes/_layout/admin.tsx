import { Badge, Container, Heading } from "@chakra-ui/react"
import { useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { z } from "zod"

import { UsersService, type UserPublic } from "@/client"
import AddUser from "@/components/Admin/AddUser"
import { DataTable, type Column } from "@/components/Common/DataTable"
import { UserActionsMenu } from "@/components/Common/UserActionsMenu"
import PendingUsers from "@/components/Pending/PendingUsers"

const usersSearchSchema = z.object({
  page: z.number().catch(1),
})

const PER_PAGE = 10

function getUsersQueryOptions({ page }: { page: number }) {
  return {
    queryFn: () =>
      UsersService.readUsers({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
    queryKey: ["users", { page }],
  }
}

export const Route = createFileRoute("/_layout/admin")({
  component: Admin,
  validateSearch: (search) => usersSearchSchema.parse(search),
})

function UsersTable() {
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])
  const navigate = useNavigate({ from: Route.fullPath })
  const { page } = Route.useSearch()

  const { data, isLoading, isPlaceholderData } = useQuery({
    ...getUsersQueryOptions({ page }),
    placeholderData: (prevData) => prevData,
  })

  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: string }) => ({ ...prev, page }),
    })

  const users = data?.data.slice(0, PER_PAGE) ?? []
  const count = data?.count ?? 0

  const columns: Column<typeof users[0]>[] = [
    {
      header: "Nombre",
      accessor: (user) => (
        <>
          <span style={{ color: !user.full_name ? "gray" : "inherit" }}>
            {user.full_name || "N/A"}
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
      accessor: (user) => user.is_superuser ? "Superuser" : "Usuario",
    },
    {
      header: "Estado",
      accessor: (user) => user.is_active ? "Activo" : "Inactivo",
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
    <DataTable
      data={users}
      columns={columns}
      isLoading={isLoading}
      isPlaceholderData={isPlaceholderData}
      count={count}
      pageSize={PER_PAGE}
      onPageChange={setPage}
      emptyStateTitle="No hay usuarios"
      emptyStateDescription="No hay usuarios registrados en el sistema"
      LoadingComponent={PendingUsers}
    />
  )
}

function Admin() {
  return (
    <Container maxW="full">
      <Heading size="lg" pt={12}>
        Gestión de Usuarios
      </Heading>

      <AddUser />
      <UsersTable />
    </Container>
  )
}
