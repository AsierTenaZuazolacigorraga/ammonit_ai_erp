import {
    Container,
    Heading,
    HStack, Link
} from "@chakra-ui/react"
import {
    type UseQueryOptions,
} from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { z } from "zod"

import { ApiError, OrderPublic, OrdersService } from "@/client"
import { DataTable, type Column, type PaginatedData } from "@/components/Common/DataTable"
import AddOrder from "@/components/Orders/AddOrder"
import ApproveOrder from "@/components/Orders/ApproveOrder"
import DeleteOrder from "@/components/Orders/DeleteOrder"

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

// Updated helper function for specific date/time format
const formatLocalDate = (dateString: string | null | undefined): string => {
    if (!dateString) {
        return "-";
    }
    try {
        const date = new Date(dateString);
        if (isNaN(date.getTime())) {
            return "Invalid Date";
        }

        // Extract parts and pad with leading zeros
        const day = String(date.getDate()).padStart(2, '0');
        const month = String(date.getMonth() + 1).padStart(2, '0'); // Month is 0-indexed
        const year = date.getFullYear();
        const hours = String(date.getHours()).padStart(2, '0');
        const minutes = String(date.getMinutes()).padStart(2, '0');
        const seconds = String(date.getSeconds()).padStart(2, '0');

        // Construct the desired format
        return `${day}-${month}-${year} ${hours}:${minutes}:${seconds}`;
    } catch (error) {
        console.error("Error formatting date:", error);
        return "Invalid Date";
    }
};

function Orders() {
    const columns: Column<OrderPublic>[] = [
        {
            header: "Acciones",
            accessor: (order) => (
                <HStack gap={2}>
                    <DeleteOrder id={order.id} />
                    <ApproveOrder order={order} />
                </HStack>
            )
        },
        {
            header: "Fecha de Procesado",
            accessor: (order) => formatLocalDate(order.date_processed)
        },
        {
            header: "Fecha de Aprobación",
            accessor: (order) => formatLocalDate(order.date_approved)
        },
        {
            header: "Documento Base",
            accessor: (order) => (
                <Link
                    href={`data:application/pdf;base64,${order.base_document}`}
                    download={order.base_document_name}
                    color="blue.500"
                    textDecoration="underline"
                >
                    {order.base_document_name}
                </Link>
            )
        },
        {
            header: "Documento Procesado",
            accessor: (order) => {
                if (!order.content_processed) return "-";
                return (
                    <Link
                        href={`data:text/csv;charset=utf-8,${encodeURIComponent(order.content_processed)}`}
                        download={order.base_document_name?.replace('.pdf', '_processed.csv')}
                        color="blue.500"
                        textDecoration="underline"
                    >
                        {order.base_document_name?.replace('.pdf', '_processed.csv')}
                    </Link>
                );
            }
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
                emptyStateTitle="No tienes ningún pedido"
                emptyStateDescription="Agrega un nuevo pedido para empezar, bien por email o bien por el botón para añadir un pedido desde un archivo .pdf"
                pageSize={PER_PAGE}
            />
        </Container>
    )
}
