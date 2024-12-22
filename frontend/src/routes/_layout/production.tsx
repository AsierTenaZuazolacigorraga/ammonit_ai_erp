import { Container, Text } from "@chakra-ui/react"
import { createFileRoute } from "@tanstack/react-router"
import { z } from "zod"


const usersSearchSchema = z.object({
  page: z.number().catch(1),
})
export const Route = createFileRoute("/_layout/production")({
  component: Production,
  validateSearch: (search) => usersSearchSchema.parse(search),

})

function Production() {

  return (
    <Container maxW="full">
      <Text>Welcome back, nice to see you again!</Text>
    </Container>
  )
}
