import { ApiError, OfferPublic, OffersService } from "@/client"
import { DataTable, type Column, type PaginatedData } from "@/components/Common/DataTable"
import { formatLocalDate } from "@/utils/date"
import {
    Container,
    Heading,
    HStack,
    Icon
} from "@chakra-ui/react"
import {
    type UseQueryOptions,
} from "@tanstack/react-query"
import { createFileRoute } from "@tanstack/react-router"
import { MdAccessTime } from "react-icons/md"
import { z } from "zod"

const offersSearchSchema = z.object({
    page: z.number().int().positive().catch(1),
})
type OffersSearch = z.infer<typeof offersSearchSchema>

const PER_PAGE = 10

const baseOffersQueryOptionsFn = (
    search: OffersSearch
): Omit<
    UseQueryOptions<PaginatedData<OfferPublic>, ApiError, PaginatedData<OfferPublic>>,
    "queryKey"
> => {
    return {
        queryFn: () =>
            OffersService.readOffers({
                skip: (search.page - 1) * PER_PAGE,
                limit: PER_PAGE,
            }),
        refetchInterval: 15000,
    }
}

export const Route = createFileRoute("/_layout/offers")({
    component: Offers,
    validateSearch: (search: Record<string, unknown>): OffersSearch =>
        offersSearchSchema.parse(search),
})

function Offers() {
    const columns: Column<OfferPublic>[] = [
        {
            header: "Fecha de Creación",
            accessor: (offer) => formatLocalDate(offer.created_at)
        },
        {
            header: "Estado",
            accessor: (_) => (
                <HStack gap={2}>
                    <Icon
                        as={MdAccessTime}
                        color="orange"
                        boxSize="16px"
                    />
                    Pendiente
                </HStack>
            )
        }
    ]

    return (
        <Container maxW="full">
            <Heading size="lg" py={6}>
                Gestión de Ofertas
            </Heading>
            <DataTable
                queryKeyBase="offers"
                baseQueryOptionsFn={baseOffersQueryOptionsFn}
                searchSchema={offersSearchSchema}
                route={Route}
                columns={columns}
                emptyStateTitle="No tienes ninguna oferta"
                emptyStateDescription="Las ofertas se crearán automáticamente cuando se reciban por email"
                pageSize={PER_PAGE}
            />
        </Container>
    )
}

