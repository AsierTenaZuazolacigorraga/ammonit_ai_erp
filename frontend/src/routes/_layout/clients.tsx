import {
    Container,
    Heading,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { z } from "zod"

import { ClientsService } from "@/client"
import AddClient from "@/components/Clients/AddClient"
import { ClientActionsMenu } from "@/components/Common/ClientActionsMenu"
import { DataTable, type Column } from "@/components/Common/DataTable"
import PendingClients from "@/components/Pending/PendingClients"

const clientsSearchSchema = z.object({
    page: z.number().catch(1),
})

const PER_PAGE = 10

function getClientsQueryOptions({ page }: { page: number }) {
    return {
        queryFn: () =>
            ClientsService.readClients({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
        queryKey: ["clients", { page }],
    }
}

export const Route = createFileRoute("/_layout/clients")({
    component: Clients,
    validateSearch: (search) => clientsSearchSchema.parse(search),
})

function ClientsTable() {
    const navigate = useNavigate({ from: Route.fullPath })
    const { page } = Route.useSearch()

    const { data, isLoading, isPlaceholderData } = useQuery({
        ...getClientsQueryOptions({ page }),
        placeholderData: (prevData) => prevData,
    })

    const setPage = (page: number) =>
        navigate({
            search: (prev: { [key: string]: string }) => ({ ...prev, page }),
        })

    const clients = data?.data.slice(0, PER_PAGE) ?? []
    const count = data?.count ?? 0

    const columns: Column<typeof clients[0]>[] = [
        {
            header: "Nombre",
            accessor: (client) => client.name,
        },
        {
            header: "Clasificador",
            accessor: (client) => client.clasifier,
        },
        {
            header: "Estructura",
            accessor: (client) => client.structure,
        },
        {
            header: "Acciones",
            accessor: (client) => <ClientActionsMenu client={client} />,
        },
    ]

    return (
        <DataTable
            data={clients}
            columns={columns}
            isLoading={isLoading}
            isPlaceholderData={isPlaceholderData}
            count={count}
            pageSize={PER_PAGE}
            onPageChange={setPage}
            emptyStateTitle="No tienes ningún cliente"
            emptyStateDescription="Agrega un nuevo cliente para empezar"
            LoadingComponent={PendingClients}
        />
    )
}

function Clients() {
    return (
        <Container maxW="full">
            <Heading size="lg" pt={12}>
                Gestión de Clientes
            </Heading>
            <AddClient />
            <ClientsTable />
        </Container>
    )
}
