import { ApiError, OrderPublic, OrdersService } from "@/client"
import { DataTable, type Column, type PaginatedData } from "@/components/Common/DataTable"
import AddOrder from "@/components/Orders/AddOrder"
import ApproveOrder from "@/components/Orders/ApproveOrder"
import DeleteOrder from "@/components/Orders/DeleteOrder"
import {
    Container,
    Heading,
    HStack,
    Icon,
    Link
} from "@chakra-ui/react"
import {
    type UseQueryOptions,
} from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { MdAccessTime, MdCheckCircle, MdError } from "react-icons/md"
import { z } from "zod"

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
        refetchInterval: 15000,
    }
}

export const Route = createFileRoute("/_layout/orders")({
    component: Orders,
    validateSearch: (search: Record<string, unknown>): OrdersSearch =>
        ordersSearchSchema.parse(search),
})

// Helper function to convert UTC dates to local timezone
const formatLocalDate = (dateString: string | null | undefined): string => {
    if (!dateString) {
        return "-";
    }
    try {
        // If dateString doesn't end with Z, it's likely a database timestamp format without timezone info
        // Ensure we treat it as UTC
        let parsedDate;

        if (dateString.endsWith('Z')) {
            // Already has UTC indicator
            parsedDate = new Date(dateString);
        } else if (dateString.includes('T')) {
            // ISO format without Z, add Z to explicitly mark as UTC
            parsedDate = new Date(dateString + 'Z');
        } else {
            // Database timestamp format (YYYY-MM-DD HH:MM:SS)
            // Convert to ISO format and mark as UTC
            parsedDate = new Date(dateString.replace(' ', 'T') + 'Z');
        }

        if (isNaN(parsedDate.getTime())) {
            console.error("Invalid date format:", dateString);
            return "Invalid Date";
        }

        // Get local date parts (parsedDate is already converted to local time by JavaScript)
        const day = String(parsedDate.getDate()).padStart(2, '0');
        const month = String(parsedDate.getMonth() + 1).padStart(2, '0');
        const year = parsedDate.getFullYear();
        const hours = String(parsedDate.getHours()).padStart(2, '0');
        const minutes = String(parsedDate.getMinutes()).padStart(2, '0');
        const seconds = String(parsedDate.getSeconds()).padStart(2, '0');

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
            width: "120px",
            accessor: (order) => (
                <HStack gap={2}>
                    <DeleteOrder id={order.id} />
                    <ApproveOrder order={order} />
                </HStack>
            )
        },
        {
            header: "Fecha de Creación",
            accessor: (order) => formatLocalDate(order.created_at)
        },
        {
            header: "Estado",
            accessor: (order) => (
                <HStack gap={2}>
                    <Icon
                        as={
                            order.state === "PENDING"
                                ? MdAccessTime
                                : order.state === "APPROVED"
                                    ? MdAccessTime
                                    : order.state === "INTEGRATED_OK"
                                        ? MdCheckCircle
                                        : MdError
                        }
                        color={
                            order.state === "PENDING"
                                ? "orange"
                                : order.state === "APPROVED"
                                    ? "gray"
                                    : order.state === "INTEGRATED_OK"
                                        ? "green"
                                        : "red"
                        }
                        boxSize="16px"
                    />
                    {order.state === "PENDING"
                        ? "Pendiente de Aprobación"
                        : order.state === "APPROVED"
                            ? "Aprobado"
                            : order.state === "INTEGRATED_OK"
                                ? "Integrado en ERP"
                                : "Error al integrar en ERP"}
                </HStack>
            )
        },
        {
            header: "Cliente",
            accessor: (order) => order.client_name
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
            header: "Información Extraída",
            accessor: (order) => {
                if (!order.content_processed) return "-";
                return (
                    <Link
                        href={`data:text/csv;charset=utf-8,${encodeURIComponent(order.content_processed)}`}
                        download={order.base_document_name?.replace('.pdf', '_ammonit.csv')}
                        color="blue.500"
                        textDecoration="underline"
                    >
                        {order.base_document_name?.replace('.pdf', '_ammonit.csv')}
                    </Link>
                );
            }
        },
    ]

    return (
        <Container maxW="full">
            <Heading size="lg" py={6}>
                Gestión de Documentos
            </Heading>
            <AddOrder />
            <DataTable
                queryKeyBase="orders"
                baseQueryOptionsFn={baseOrdersQueryOptionsFn}
                searchSchema={ordersSearchSchema}
                route={Route}
                columns={columns}
                emptyStateTitle="No tienes ningún documento"
                emptyStateDescription="Agrega un nuevo documento para empezar, bien por email o bien por el botón para añadir un documento desde un archivo .pdf"
                pageSize={PER_PAGE}
            />
        </Container>
    )
}
