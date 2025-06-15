import { Container, Heading, HStack, Icon } from "@chakra-ui/react"
import { UseQueryOptions } from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { z } from "zod"

import { ApiError, EmailPublic, EmailsService } from "@/client"
import { DataTable, type Column, type PaginatedData } from "@/components/Common/DataTable"
import AddEmail from "@/components/Emails/AddEmail"
import ConnectEmail from "@/components/Emails/ConnectEmail"
import DeleteEmail from "@/components/Emails/DeleteEmail"
import EditEmail from "@/components/Emails/EditEmail"
import { MdCheckCircle, MdError } from "react-icons/md"

const emailsSearchSchema = z.object({
    page: z.number().int().positive().catch(1),
})
type EmailsSearch = z.infer<typeof emailsSearchSchema>

const PER_PAGE = 10

const baseEmailsQueryOptionsFn = (
    search: EmailsSearch
): Omit<
    UseQueryOptions<PaginatedData<EmailPublic>, ApiError, PaginatedData<EmailPublic>>,
    "queryKey"
> => {
    return {
        queryFn: () =>
            EmailsService.readEmails({
                skip: (search.page - 1) * PER_PAGE,
                limit: PER_PAGE,
            }),
    }
}

export const Route = createFileRoute("/_layout/emails")({
    component: EmailsConfig,
    validateSearch: (search: Record<string, unknown>): EmailsSearch =>
        emailsSearchSchema.parse(search),
})

function EmailsConfig() {
    const columns: Column<EmailPublic>[] = [
        {
            header: "Acciones",
            width: "120px",
            accessor: (email) => (
                <HStack gap={2}>
                    <ConnectEmail email={email.email} is_connected={email.is_connected} />
                    <DeleteEmail id={email.id} />
                    <EditEmail email={email} />
                </HStack>
            )
        },
        {
            header: "Email",
            accessor: (email) => email.email
        },
        {
            header: "Estado",
            accessor: (email) => (
                <HStack gap={2}>
                    <Icon
                        as={
                            email.is_connected
                                ? MdCheckCircle
                                : MdError
                        }
                        color={
                            email.is_connected
                                ? "green"
                                : "red"
                        }
                        boxSize="16px"
                    />
                    {email.is_connected
                        ? "Conectado"
                        : "No conectado"}
                </HStack>
            )
        },
        {
            header: "Habilitado para Pedidos",
            accessor: (email) => (email.is_orders ? "Sí" : "No"),
        },
        {
            header: "Filtro para Pedidos",
            accessor: (email) => email.orders_filter || "No hay filtros definidos, se procesan todos los email que se reciben"
        },
        {
            header: "Habilitado para Ofertas",
            accessor: (email) => (email.is_offers ? "Sí" : "No"),
        },
        {
            header: "Filtro para Ofertas",
            accessor: (email) => email.offers_filter || "No hay filtros definidos, se procesan todos los email que se reciben"
        },
    ]

    return (
        <Container maxW="full">
            <Heading size="lg" py={6}>
                Configuración Outlook
            </Heading>
            <AddEmail />
            <DataTable
                queryKeyBase="emails"
                baseQueryOptionsFn={baseEmailsQueryOptionsFn}
                searchSchema={emailsSearchSchema}
                route={Route}
                columns={columns}
                emptyStateTitle="No hay emails configurados"
                emptyStateDescription="Agrega un nuevo email para empezar a conectar con Outlook."
                pageSize={PER_PAGE}
            />
        </Container>
    )
} 