import { Box, Flex, Icon, Text } from "@chakra-ui/react"
import { Link as RouterLink } from "@tanstack/react-router"
import { FiHome, FiMail, FiSettings, FiUserPlus, FiUsers } from "react-icons/fi"
import type { IconType } from "react-icons/lib"

import useAuth from "@/hooks/useAuth"

const items = [
  { icon: FiHome, title: "Gestión de Documentos", path: "/orders" },
  { icon: FiUserPlus, title: "Gestión de Clientes", path: "/clients" },
  { icon: FiMail, title: "Configuración Outlook", path: "/emails" },
  { icon: FiSettings, title: "Ajustes de Usuario", path: "/settings" },
]


interface SidebarItemsProps {
  onClose?: () => void
}

interface Item {
  icon: IconType
  title: string
  path: string
}

const SidebarItems = ({ onClose }: SidebarItemsProps) => {
  const { user: currentUser } = useAuth()

  const finalItems: Item[] = currentUser?.is_superuser
    ? [...items, { icon: FiUsers, title: "Administrador", path: "/admin" }]
    : items

  const listItems = finalItems.map(({ icon, title, path }) => (
    <RouterLink key={title} to={path} onClick={onClose}>
      <Flex
        gap={4}
        px={4}
        py={2}
        _hover={{
          background: "gray.subtle",
        }}
        alignItems="center"
        fontSize="sm"
      >
        <Icon as={icon} alignSelf="center" />
        <Text ml={2}>{title}</Text>
      </Flex>
    </RouterLink>
  ))

  return (
    <>
      <Text fontSize="xs" px={4} py={2} fontWeight="bold">
        {/* Menu */}
      </Text>
      <Box>{listItems}</Box>
    </>
  )
}

export default SidebarItems