import {
    PaginationItems,
    PaginationNextTrigger,
    PaginationPrevTrigger,
    PaginationRoot,
} from "@/components/ui/pagination.tsx"
import {
    EmptyState,
    Flex,
    Table,
    VStack
} from "@chakra-ui/react"
import { ReactNode } from "react"
import { FiSearch } from "react-icons/fi"

export interface Column<T> {
    header: string
    accessor: (item: T) => ReactNode
    width?: string
}

interface DataTableProps<T> {
    data: T[]
    columns: Column<T>[]
    isLoading: boolean
    isPlaceholderData: boolean
    count: number
    pageSize: number
    onPageChange: (page: number) => void
    emptyStateTitle: string
    emptyStateDescription: string
    LoadingComponent: React.ComponentType
}

export function DataTable<T>({
    data,
    columns,
    isLoading,
    isPlaceholderData,
    count,
    pageSize,
    onPageChange,
    emptyStateTitle,
    emptyStateDescription,
    LoadingComponent
}: DataTableProps<T>) {
    if (isLoading) {
        return <LoadingComponent />
    }

    if (data.length === 0) {
        return (
            <EmptyState.Root>
                <EmptyState.Content>
                    <EmptyState.Indicator>
                        <FiSearch />
                    </EmptyState.Indicator>
                    <VStack textAlign="center">
                        <EmptyState.Title>{emptyStateTitle}</EmptyState.Title>
                        <EmptyState.Description>
                            {emptyStateDescription}
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
                        {columns.map((column, index) => (
                            <Table.ColumnHeader key={index} w={column.width || "sm"}>
                                {column.header}
                            </Table.ColumnHeader>
                        ))}
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {data.map((item, rowIndex) => (
                        <Table.Row key={rowIndex} opacity={isPlaceholderData ? 0.5 : 1}>
                            {columns.map((column, colIndex) => (
                                <Table.Cell key={colIndex}>
                                    {column.accessor(item)}
                                </Table.Cell>
                            ))}
                        </Table.Row>
                    ))}
                </Table.Body>
            </Table.Root>
            <Flex justifyContent="flex-end" mt={4}>
                <PaginationRoot
                    count={count}
                    pageSize={pageSize}
                    onPageChange={({ page }) => onPageChange(page)}
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