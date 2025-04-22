import {
    Container,
    Heading,
    Link,
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { z } from "zod"

import { OrdersService } from "@/client"
import { DataTable, type Column } from "@/components/Common/DataTable"
import { OrderActionsMenu } from "@/components/Common/OrderActionsMenu"
import AddOrder from "@/components/Orders/AddOrder"
import PendingOrders from "@/components/Pending/PendingOrders"

const ordersSearchSchema = z.object({
    page: z.number().catch(1),
})

const PER_PAGE = 10

function getOrdersQueryOptions({ page }: { page: number }) {
    return {
        queryFn: () =>
            OrdersService.readOrders({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
        queryKey: ["orders", { page }],
    }
}

export const Route = createFileRoute("/_layout/orders")({
    component: Orders,
    validateSearch: (search) => ordersSearchSchema.parse(search),
})

function OrdersTable() {
    const navigate = useNavigate({ from: Route.fullPath })
    const { page } = Route.useSearch()

    const { data, isLoading, isPlaceholderData } = useQuery({
        ...getOrdersQueryOptions({ page }),
        placeholderData: (prevData) => prevData,
    })

    const setPage = (page: number) =>
        navigate({
            search: (prev: { [key: string]: string }) => ({ ...prev, page }),
        })

    const orders = data?.data.slice(0, PER_PAGE) ?? []
    const count = data?.count ?? 0

    const columns: Column<typeof orders[0]>[] = [
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
        <DataTable
            data={orders}
            columns={columns}
            isLoading={isLoading}
            isPlaceholderData={isPlaceholderData}
            count={count}
            pageSize={PER_PAGE}
            onPageChange={setPage}
            emptyStateTitle="No tienes ningún pedido"
            emptyStateDescription="Agrega un nuevo pedido para empezar, bien por email o bien por el botón para añadir un pedido desde un archivo .pdf"
            LoadingComponent={PendingOrders}
        />
    )
}

function Orders() {
    return (
        <Container maxW="full">
            <Heading size="lg" pt={12}>
                Gestión de Pedidos
            </Heading>
            <AddOrder />
            <OrdersTable />
        </Container>
    )
}
