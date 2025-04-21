import {
    Container,
    EmptyState,
    Flex,
    Heading,
    Link,
    Table,
    VStack
} from "@chakra-ui/react"
import { useQuery } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { FiSearch } from "react-icons/fi"
import { z } from "zod"

import { OrdersService } from "@/client"
import { OrderActionsMenu } from "@/components/Common/OrderActionsMenu"
import AddOrder from "@/components/Orders/AddOrder"
import PendingOrders from "@/components/Pending/PendingOrders"
import {
    PaginationItems,
    PaginationNextTrigger,
    PaginationPrevTrigger,
    PaginationRoot,
} from "@/components/ui/pagination.tsx"

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

    if (isLoading) {
        return <PendingOrders />
    }

    if (orders.length === 0) {
        return (
            <EmptyState.Root>
                <EmptyState.Content>
                    <EmptyState.Indicator>
                        <FiSearch />
                    </EmptyState.Indicator>
                    <VStack textAlign="center">
                        <EmptyState.Title>No tienes ningún pedido</EmptyState.Title>
                        <EmptyState.Description>
                            Agrega un nuevo pedido para empezar, bien por email o bien por el botón
                            para añadir un pedido desde un archivo .pdf
                        </EmptyState.Description>
                    </VStack>
                </EmptyState.Content>
            </EmptyState.Root>
        )
    }

    return (
        <>
            <Table.Root size={{ base: "sm", md: "md" }}>
                <Table.Header>
                    <Table.Row>
                        <Table.ColumnHeader w="sm">Fecha</Table.ColumnHeader>
                        <Table.ColumnHeader w="sm">Documento de Pedido</Table.ColumnHeader>
                        <Table.ColumnHeader w="sm">Documento Procesado</Table.ColumnHeader>
                        <Table.ColumnHeader w="sm">Acciones</Table.ColumnHeader>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {orders?.map((order) => (
                        <Table.Row key={order.id} opacity={isPlaceholderData ? 0.5 : 1}>
                            <Table.Cell>
                                {order.date_local}
                            </Table.Cell>
                            <Table.Cell truncate maxWidth="sm">
                                <Link
                                    href={`data:application/pdf;base64,${order.in_document}`}
                                    download={order.in_document_name}
                                    color="blue.500"
                                    textDecoration="underline"
                                >
                                    {order.in_document_name}
                                </Link>
                            </Table.Cell>
                            <Table.Cell truncate maxWidth="sm">
                                <Link
                                    href={`data:application/pdf;base64,${order.out_document}`}
                                    download={order.out_document_name}
                                    color="blue.500"
                                    textDecoration="underline"
                                >
                                    {order.out_document_name}
                                </Link>
                            </Table.Cell>
                            <Table.Cell>
                                <OrderActionsMenu order={order} />
                            </Table.Cell>
                        </Table.Row>
                    ))}
                </Table.Body>
            </Table.Root>
            <Flex justifyContent="flex-end" mt={4}>
                <PaginationRoot
                    count={count}
                    pageSize={PER_PAGE}
                    onPageChange={({ page }) => setPage(page)}
                >
                    <Flex>
                        <PaginationPrevTrigger />
                        <PaginationItems />
                        <PaginationNextTrigger />
                    </Flex>
                </PaginationRoot>
            </Flex>
        </>
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
