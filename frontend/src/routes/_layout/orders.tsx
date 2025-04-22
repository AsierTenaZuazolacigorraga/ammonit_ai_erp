import {
    Container,
    Heading,
    Link,
} from "@chakra-ui/react"
import {
    type UseQueryOptions,
} from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { z } from "zod"

import { ApiError, OrderPublic, OrdersService } from "@/client"
import { DataTable, type Column, type PaginatedData } from "@/components/Common/DataTable"
import { OrderActionsMenu } from "@/components/Common/OrderActionsMenu"
import AddOrder from "@/components/Orders/AddOrder"
import PendingOrders from "@/components/Pending/PendingOrders"

const ordersSearchSchema = z.object({
    page: z.number().int().positive().catch(1),
})
type OrdersSearch = z.infer<typeof ordersSearchSchema>

const PER_PAGE = 10

const baseOrdersQueryOptionsFn = (
    search: OrdersSearch
): Omit<
    UseQueryOptions<PaginatedData<OrderPublic>, ApiError, PaginatedData<OrderPublic>>,
    "queryKey"
> => {
    return {
        queryFn: () =>
            OrdersService.readOrders({
                skip: (search.page - 1) * PER_PAGE,
                limit: PER_PAGE,
            }),
    }
}

export const Route = createFileRoute("/_layout/orders")({
    component: Orders,
    validateSearch: (search: Record<string, unknown>): OrdersSearch =>
        ordersSearchSchema.parse(search),
})

function Orders() {
    const columns: Column<OrderPublic>[] = [
        {
            header: "Fecha",
            accessor: (order) => order.date_local,
        },
        {
            header: "Documento de Pedido",
            accessor: (order) => (
                <Link
                    href={`data:application/pdf;base64,${order.in_document}`}
                    download={order.in_document_name}
                    color="blue.500"
                    textDecoration="underline"
                >
                    {order.in_document_name}
                </Link>
            ),
        },
        {
            header: "Documento Procesado",
            accessor: (order) => (
                <Link
                    href={`data:application/pdf;base64,${order.out_document}`}
                    download={order.out_document_name}
                    color="blue.500"
                    textDecoration="underline"
                >
                    {order.out_document_name}
                </Link>
            ),
        },
        {
            header: "Acciones",
            accessor: (order) => <OrderActionsMenu order={order} />,
        },
    ]

    return (
        <Container maxW="full">
            <Heading size="lg" pt={12}>
                Gestión de Pedidos
            </Heading>
            <AddOrder />
            <DataTable
                queryKeyBase="orders"
                baseQueryOptionsFn={baseOrdersQueryOptionsFn}
                searchSchema={ordersSearchSchema}
                route={Route}
                columns={columns}
                LoadingComponent={PendingOrders}
                emptyStateTitle="No tienes ningún pedido"
                emptyStateDescription="Agrega un nuevo pedido para empezar, bien por email o bien por el botón para añadir un pedido desde un archivo .pdf"
                pageSize={PER_PAGE}
            />
        </Container>
    )
}
