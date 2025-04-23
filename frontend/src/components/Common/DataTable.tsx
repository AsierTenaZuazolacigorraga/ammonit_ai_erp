import { ApiError } from "@/client"
import {
    PaginationItems,
    PaginationNextTrigger,
    PaginationPrevTrigger,
    PaginationRoot,
} from "@/components/ui/pagination.tsx"
import { EmptyState, Flex, Skeleton, Table, VStack } from "@chakra-ui/react"
import {
    useQuery,
    type QueryKey,
    type UseQueryOptions
} from "@tanstack/react-query"
import { AnyRoute, useNavigate } from "@tanstack/react-router"
import { ReactNode } from "react"
import { FiSearch } from "react-icons/fi"
import { z, ZodSchema } from "zod"

// Define the expected paginated data structure
export interface PaginatedData<T> {
    data: T[]
    count: number
}

// Default search schema if none is provided (only page)
const defaultSearchSchema = z.object({
    page: z.number().int().positive().catch(1),
})


// Base query options function type
type BaseQueryOptionsFn<T, TSearch> = (
    search: TSearch
) => Omit<UseQueryOptions<PaginatedData<T>, ApiError, PaginatedData<T>, QueryKey>, "queryKey">

export interface Column<T> {
    header: string
    accessor: (item: T) => ReactNode
    width?: string
}

// Props required for the refactored DataTable
// Relaxed TSearch constraint to just require a 'page' number
interface DataTableProps<T, TSearch extends { page: number }> {
    columns: Column<T>[]
    queryKeyBase: string // e.g., "clients"
    baseQueryOptionsFn: BaseQueryOptionsFn<T, TSearch>
    // Allow schema with flexible input type, as long as output matches TSearch
    searchSchema?: ZodSchema<TSearch, any, any>
    route: AnyRoute // Route object from createFileRoute
    emptyStateTitle: string
    emptyStateDescription: string
    pageSize?: number
}

const DEFAULT_PAGE_SIZE = 10

// Use the relaxed TSearch constraint here too
export function DataTable<T, TSearch extends { page: number }>({
    columns,
    queryKeyBase,
    baseQueryOptionsFn,
    // Cast default schema to satisfy the ZodSchema<TSearch> type requirement
    searchSchema = defaultSearchSchema as unknown as ZodSchema<TSearch, any, any>,
    route,
    emptyStateTitle,
    emptyStateDescription,
    pageSize = DEFAULT_PAGE_SIZE,
}: DataTableProps<T, TSearch>) {
    // Get search params and navigation from the specific route context
    const search = route.useSearch() as TSearch
    const navigate = useNavigate({ from: route.fullPath })

    // Validate/parse search params (though route should handle this)
    const validatedSearch = searchSchema.parse(search) as TSearch
    const page = validatedSearch.page

    // Construct query options
    const queryOptions = {
        ...baseQueryOptionsFn(validatedSearch),
        queryKey: [queryKeyBase, validatedSearch],
        placeholderData: (prevData: PaginatedData<T> | undefined) => prevData,
    }

    // Fetch data
    const { data, isLoading, isPlaceholderData } = useQuery(queryOptions)

    // Pagination handler
    const setPage = (newPage: number) =>
        navigate({
            search: (prev: TSearch) => ({ ...prev, page: newPage }),
            replace: true,
        })

    const items = data?.data.slice(0, pageSize) ?? []
    const count = data?.count ?? 0

    // --- Render generic loading skeleton --- 
    if (isLoading && !isPlaceholderData) {
        const skeletonRowCount = pageSize / 2; // Show ~half page of skeletons
        return (
            <Table.Root size={{ base: "sm", md: "md" }} tableLayout="auto">
                <Table.Header>
                    <Table.Row>
                        {columns.map((column, index) => (
                            <Table.ColumnHeader
                                key={index}
                                w={column.width || "auto"}
                                // Add border, except for the last header
                                borderRightWidth={index === columns.length - 1 ? 0 : "1px"}
                                borderRightColor="gray.200"
                            >
                                {column.header}
                            </Table.ColumnHeader>
                        ))}
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {[...Array(skeletonRowCount)].map((_, rowIndex) => (
                        <Table.Row
                            key={rowIndex}
                            bg={rowIndex % 2 === 0 ? "gray.50" : "transparent"}
                        >
                            {columns.map((_, colIndex) => (
                                <Table.Cell
                                    key={colIndex}
                                    w={columns[colIndex].width || "auto"}
                                    // Add border, except for the last cell
                                    borderRightWidth={colIndex === columns.length - 1 ? 0 : "1px"}
                                    borderRightColor="gray.200"
                                >
                                    <Skeleton height="20px" />
                                </Table.Cell>
                            ))}
                        </Table.Row>
                    ))}
                </Table.Body>
            </Table.Root>
        )
    }

    // --- Render empty state ---
    if (!isLoading && items.length === 0) {
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

    // --- Render actual data table ---
    return (
        <>
            <Table.Root size={{ base: "sm", md: "md" }} tableLayout="auto">
                <Table.Header>
                    <Table.Row>
                        {columns.map((column, index) => (
                            <Table.ColumnHeader
                                key={index}
                                w={column.width || "auto"}
                                // Add border, except for the last header
                                borderRightWidth={index === columns.length - 1 ? 0 : "1px"}
                                borderRightColor="gray.200"
                            >
                                {column.header}
                            </Table.ColumnHeader>
                        ))}
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {items.map((item: T, rowIndex: number) => (
                        <Table.Row
                            key={rowIndex}
                            opacity={isPlaceholderData ? 0.5 : 1}
                            bg={rowIndex % 2 === 0 ? "gray.50" : "transparent"}
                            _hover={{ bg: "gray.100" }}
                        >
                            {columns.map((column, colIndex) => (
                                <Table.Cell
                                    key={colIndex}
                                    w={columns[colIndex].width || "auto"}
                                    // Add border, except for the last cell
                                    borderRightWidth={colIndex === columns.length - 1 ? 0 : "1px"}
                                    borderRightColor="gray.200"
                                >
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
                    // Use current page from search params for initial state
                    page={page}
                    onPageChange={({ page: newPage }) => setPage(newPage)}
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