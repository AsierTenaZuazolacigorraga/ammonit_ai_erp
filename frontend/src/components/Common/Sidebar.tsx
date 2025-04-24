import { Box, Flex, IconButton, Text } from "@chakra-ui/react"
import { useQueryClient } from "@tanstack/react-query"
import { useState } from "react"
import { FaBars } from "react-icons/fa"
import { FiLogOut } from "react-icons/fi"
import { HiMiniChevronDoubleLeft, HiMiniChevronDoubleRight } from "react-icons/hi2"

import type { UserPublic } from "@/client"
import useAuth from "@/hooks/useAuth"
import {
  DrawerBackdrop,
  DrawerBody,
  DrawerCloseTrigger,
  DrawerContent,
  DrawerRoot,
  DrawerTrigger,
} from "../ui/drawer"
import SidebarItems from "./SidebarItems"

const Sidebar = () => {
  const queryClient = useQueryClient()
  const currentUser = queryClient.getQueryData<UserPublic>(["currentUser"])
  const { logout } = useAuth()
  const [open, setOpen] = useState(false)
  const [isDesktopVisible, setIsDesktopVisible] = useState(true)

  return (
    <>
      {/* Mobile */}
      <DrawerRoot
        placement="start"
        open={open}
        onOpenChange={(e) => setOpen(e.open)}
      >
        <DrawerBackdrop />
        <DrawerTrigger asChild>
          <IconButton
            variant="ghost"
            color="inherit"
            display={{ base: "flex", md: "none" }}
            aria-label="Open Menu"
            position="absolute"
            zIndex="100"
            m={4}
          >
            <FaBars />
          </IconButton>
        </DrawerTrigger>
        <DrawerContent maxW="xs">
          <DrawerCloseTrigger />
          <DrawerBody>
            <Flex flexDir="column" justify="space-between">
              <Box>
                <SidebarItems onClose={() => setOpen(false)} />
                <Flex
                  as="button"
                  onClick={() => {
                    logout()
                  }}
                  alignItems="center"
                  gap={4}
                  px={4}
                  py={2}
                >
                  <FiLogOut />
                  <Text>Log Out</Text>
                </Flex>
              </Box>
              {currentUser?.email && (
                <Text fontSize="sm" p={2} truncate maxW="sm">
                  Logged in as: {currentUser.email}
                </Text>
              )}
            </Flex>
          </DrawerBody>
          <DrawerCloseTrigger />
        </DrawerContent>
      </DrawerRoot>

      {/* Desktop */}

      <IconButton
        variant="ghost"
        color="gray.600"
        bg="transparent"
        _hover={{
          color: "gray.900"
        }}
        size="sm"
        onClick={() => setIsDesktopVisible(v => !v)}
        position="fixed"
        zIndex="sticky"
        gap={4}
        px={4}
        py={2}
        alignItems="center"
        fontSize="sm"
      >
        {isDesktopVisible ? (
          <HiMiniChevronDoubleLeft size={20} style={{ strokeWidth: 0.5 }} />
        ) : (
          <HiMiniChevronDoubleRight size={20} style={{ strokeWidth: 0.5 }} />
        )}
      </IconButton>

      {isDesktopVisible && (
        <Box
          bg="bg.subtle"
          boxShadow="md"
          pt={8}
        >
          <Box >
            <SidebarItems />
          </Box>
        </Box>
      )}
    </>
  )
}

export default Sidebar