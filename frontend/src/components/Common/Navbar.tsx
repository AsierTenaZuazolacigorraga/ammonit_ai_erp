import { Box, Flex, Image, useBreakpointValue } from "@chakra-ui/react"
import { Link } from "@tanstack/react-router"

import UserMenu from "./UserMenu"
import Logo from "/assets/images/ammonit_generic_logo.svg"

function Navbar() {
  const display = useBreakpointValue({ base: "none", md: "flex" })

  return (
    <Flex
      display={display}
      justify="space-between"
      position="sticky"
      color="white"
      align="center"
      bg="bg.muted"
      w="100%"
      top={0}
      left={0}
      height={12}
      boxShadow="md"
      zIndex={100}
    >
      <Box h="full" p={1}>
        <Link to="/">
          <Image src={Logo} alt="Logo" h="full" />
        </Link>
      </Box>
      <Flex gap={2} alignItems="center">
        <UserMenu />
      </Flex>
    </Flex >
  )
}

export default Navbar
