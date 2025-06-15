import {
    Container,
    Heading,
    Text
} from "@chakra-ui/react"
// import AddOrder from "@/components/Orders/AddOrder"
import { createFileRoute } from "@tanstack/react-router"

export const Route = createFileRoute("/_layout/offers")({
    component: Offers,

})

function Offers() {
    return (
        <Container maxW="full">
            <Heading size="lg" py={6}>
                Gestión de Ofertas
            </Heading>
            <Text>En desarrollo ...</Text>
        </Container>
    )
}

