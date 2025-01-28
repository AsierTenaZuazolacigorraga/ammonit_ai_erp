import {
  MenuContent,
  MenuItem,
  MenuRoot,
  MenuTrigger,
} from "@/components/ui/menu"
import { Box, IconButton, Theme } from "@chakra-ui/react"

import { Link as RouteLink } from "@tanstack/react-router"
import { FaUserAstronaut } from "react-icons/fa"
import { FiLogOut, FiUser } from "react-icons/fi"

import useAuth from "@/hooks/useAuth"

const UserMenu = () => {
  const { logout } = useAuth()

  const handleLogout = async () => {
    logout()
  }

  return (
    <>

      <Box>
        <Theme appearance="light">
          <MenuRoot>
            <MenuTrigger asChild>
              <IconButton
                m={2}
                aria-label="Options"
                size="xs"
                rounded="full"
                data-testid="user-menu"
                colorPalette="green"
              >
                <FaUserAstronaut color="white" />
              </IconButton>
            </MenuTrigger>
            <MenuContent>
              <MenuItem value="profile" asChild>
                <RouteLink to="/settings">
                  <FiUser fontSize="18px" />
                  <Box flex="1">Mi perfil</Box>
                </RouteLink>
              </MenuItem>
              <MenuItem
                value="logout"
                onClick={handleLogout}
                fontWeight="bold"
                color="red"
              >
                <FiLogOut fontSize="18px" />
                <Box flex="1" >Log out</Box>
              </MenuItem>
            </MenuContent>
          </MenuRoot>
        </Theme>
      </Box>

    </>
  )
}

export default UserMenu
