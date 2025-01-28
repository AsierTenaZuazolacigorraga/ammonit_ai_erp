import { Box, Text } from "@chakra-ui/react"
import { createFileRoute, redirect } from "@tanstack/react-router"
import { z } from 'zod'

import useAuth from "@/hooks/useAuth"

const ordersSearchSchema = z.object({
  page: z.number().catch(1),
})


export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  beforeLoad: async () => {
    throw redirect({
      to: "/orders",
      search: (search) => ordersSearchSchema.parse(search),

    })
  }
})

function Dashboard() {
  const { user: currentUser } = useAuth()

  return (
    <>
      <Box>
        <Text fontSize="2xl">
          Hi, {currentUser?.full_name || currentUser?.email} 👋🏼
        </Text>
        <Text>Welcome back, nice to see you again!</Text>
      </Box>
    </>
  )
}
