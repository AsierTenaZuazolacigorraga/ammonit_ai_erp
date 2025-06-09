import {
    Container,
    Heading,
    HStack,
} from "@chakra-ui/react"
import {
    type UseQueryOptions,
} from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { z } from "zod"

import { ApiError, ClientPublic, ClientsService } from "@/client"
import AddClient from "@/components/Clients/AddClient"
import DeleteClient from "@/components/Clients/DeleteClient"
import EditClient from "@/components/Clients/EditClient"
import { DataTable, type Column, type PaginatedData } from "@/components/Common/DataTable"

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
            header: "Acciones",
            width: "120px",
            accessor: (client) => (
                <HStack gap={2}>
                    <DeleteClient id={client.id} />
                    <EditClient client={client} />
                </HStack>
            )
        },
        {
            header: "Nombre",
            accessor: (client) => client.name,
        },
        {
            header: "Clasificador",
            accessor: (client) => client.clasifier,
        }
    ]

    return (
        <Container maxW="full">
            <Heading size="lg" py={6}>
                Gestión de Clientes
            </Heading>
            <AddClient />
            <DataTable
                queryKeyBase="clients"
                baseQueryOptionsFn={baseClientsQueryOptionsFn}
                searchSchema={clientsSearchSchema}
                route={Route}
                columns={columns}
                emptyStateTitle="No tienes ningún cliente"
                emptyStateDescription="Agrega un nuevo cliente para empezar"
                pageSize={PER_PAGE}
            />
        </Container>
    )
}
