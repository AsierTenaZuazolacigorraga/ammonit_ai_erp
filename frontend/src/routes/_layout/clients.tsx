import {
    Container,
    Heading,
} from "@chakra-ui/react"
import {
    type UseQueryOptions,
} from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { z } from "zod"

import { ApiError, ClientPublic, ClientsService, PaginatedData } from "@/client"
import AddClient from "@/components/Clients/AddClient"
import { ClientActionsMenu } from "@/components/Common/ClientActionsMenu"
import { DataTable, type Column } from "@/components/Common/DataTable"
import PendingClients from "@/components/Pending/PendingClients"

const clientsSearchSchema = z.object({
    page: z.number().int().positive().catch(1),
})
type ClientsSearch = z.infer<typeof clientsSearchSchema>

const PER_PAGE = 10

const baseClientsQueryOptionsFn = (
    search: ClientsSearch
): Omit<
    UseQueryOptions<
        PaginatedData<ClientPublic>,
        ApiError,
        PaginatedData<ClientPublic>
    >,
    "queryKey"
> => {
    return {
        queryFn: () =>
            ClientsService.readClients({
                skip: (search.page - 1) * PER_PAGE,
                limit: PER_PAGE,
            }),
    }
}

export const Route = createFileRoute("/_layout/clients")({
    component: Clients,
    validateSearch: (search: Record<string, unknown>): ClientsSearch =>
        clientsSearchSchema.parse(search),
})

function Clients() {
    const columns: Column<ClientPublic>[] = [
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
        <Container maxW="full">
            <Heading size="lg" pt={12}>
                Gestión de Clientes
            </Heading>
            <AddClient />
            <DataTable
                queryKeyBase="clients"
                baseQueryOptionsFn={baseClientsQueryOptionsFn}
                searchSchema={clientsSearchSchema}
                route={Route}
                columns={columns}
                LoadingComponent={PendingClients}
                emptyStateTitle="No tienes ningún cliente"
                emptyStateDescription="Agrega un nuevo cliente para empezar"
                pageSize={PER_PAGE}
            />
        </Container>
    )
}
