import { SkeletonText } from '@/components/ui/skeleton'
import { Container, Heading, Table } from '@chakra-ui/react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { useEffect } from 'react'
import { z } from 'zod'

import { OrdersService } from '@/client'
import ActionsMenu from '@/components/Common/ActionsMenu'
import EntityActionsBar from '@/components/Common/EntityActionsBar'
import { PaginationFooter } from '@/components/Common/PaginationFooter.tsx'
import AddOrder from '@/components/Orders/AddOrder'

const ordersSearchSchema = z.object({
    page: z.number().catch(1),
})

export const Route = createFileRoute('/_layout/orders')({
    component: Orders,
    validateSearch: (search) => ordersSearchSchema.parse(search),
})

const PER_PAGE = 5

function getOrdersQueryOptions({ page }: { page: number }) {
    return {
        queryFn: () =>
            OrdersService.readOrders({ skip: (page - 1) * PER_PAGE, limit: PER_PAGE }),
        queryKey: ['orders', { page }],
    }
}

function OrdersTable() {
    const queryClient = useQueryClient()
    const { page } = Route.useSearch()
    const navigate = useNavigate({ from: Route.fullPath })
    const setPage = (page: number) =>
        navigate({
            search: (prev: { [key: string]: number }) => ({ ...prev, page }),
        })

    const {
        data: orders,
        isPending,
        isPlaceholderData,
    } = useQuery({
        ...getOrdersQueryOptions({ page }),
        placeholderData: (prevData) => prevData,
    })

    const hasNextPage = !isPlaceholderData && orders?.data.length === PER_PAGE
    const hasPreviousPage = page > 1

    useEffect(() => {
        if (hasNextPage) {
            queryClient.prefetchQuery(getOrdersQueryOptions({ page: page + 1 }))
        }
        if (hasPreviousPage) {
            queryClient.prefetchQuery(getOrdersQueryOptions({ page: page - 1 }))
        }
    }, [page, queryClient, hasNextPage, hasPreviousPage])

    return (
        <>
            <Table.Root size={{ base: 'sm', md: 'md' }}>
                <Table.Header>
                    <Table.Row>
                        <Table.ColumnHeader>Fecha</Table.ColumnHeader>
                        <Table.ColumnHeader>Documento de Pedido</Table.ColumnHeader>
                        <Table.ColumnHeader>Documento Procesado</Table.ColumnHeader>
                        <Table.ColumnHeader>Acciones</Table.ColumnHeader>
                    </Table.Row>
                </Table.Header>
                {isPending ? (
                    <Table.Body>
                        <Table.Row>
                            {new Array(4).fill(null).map((_, index) => (
                                <Table.Cell key={index}>
                                    <SkeletonText lineClamp={1} paddingBlock="16px" />
                                </Table.Cell>
                            ))}
                        </Table.Row>
                    </Table.Body>
                ) : (
                    <Table.Body>
                        {orders?.data.map((order) => (
                            <Table.Row key={order.id} opacity={isPlaceholderData ? 0.5 : 1}>
                                <Table.Cell>
                                    {order.date_local}
                                </Table.Cell>
                                <Table.Cell truncate maxWidth="150px">
                                    {order.in_document_name}
                                </Table.Cell>
                                <Table.Cell truncate maxWidth="150px">
                                    B
                                </Table.Cell>
                                <Table.Cell>
                                    <ActionsMenu type={'Pedido'} value={order} />
                                </Table.Cell>
                            </Table.Row>
                        ))}
                    </Table.Body>
                )}
            </Table.Root>

            <PaginationFooter
                page={page}
                pageSize={PER_PAGE}
                count={orders?.count || 0}
                setPage={setPage}
            />
        </>
    )
}

function Orders() {
    return (
        <Container maxW="full">
            <Heading size="lg" textAlign={{ base: 'center', md: 'left' }}>
                Gestión de Pedidos
            </Heading>
            <EntityActionsBar type={'Pedido'} addModalAs={AddOrder} />
            <OrdersTable />
        </Container>
    )
}
