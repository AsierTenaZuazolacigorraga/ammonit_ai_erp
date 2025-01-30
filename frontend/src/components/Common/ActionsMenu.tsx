import { Box, IconButton, useDisclosure } from "@chakra-ui/react"

import {
  MenuContent,
  MenuItem,
  MenuRoot,
  MenuTrigger,
} from "@/components/ui/menu"
import { BsThreeDotsVertical } from "react-icons/bs"
import { FiEdit, FiTrash } from "react-icons/fi"

import type { OrderPublic, UserPublic } from "@/client"
import EditUser from "../Admin/EditUser"
import EditOrder from "../Orders/EditOrder"
import Delete from "./DeleteAlert"

interface ActionsMenuProps {
  type: string
  value: OrderPublic | UserPublic
  disabled?: boolean
}

const ActionsMenu = ({ type, value, disabled }: ActionsMenuProps) => {
  const editUserModal = useDisclosure()
  const deleteModal = useDisclosure()

  return (
    <>
      <MenuRoot>
        <MenuTrigger asChild>
          <IconButton size="sm" variant="ghost" disabled={disabled}>
            <BsThreeDotsVertical />
          </IconButton>
        </MenuTrigger>
        <MenuContent>
          {type === "Usuario" ? (
            <MenuItem value="edit" onClick={editUserModal.onOpen}>
              <FiEdit fontSize="16px" />
              <Box flex="1">Editar {type}</Box>
            </MenuItem>
          ) : null}
          <MenuItem value="delete" onClick={deleteModal.onOpen} color="red">
            <FiTrash fontSize="16px" />
            <Box flex="1">Eliminar {type}</Box>
          </MenuItem>
          {type === "Usuario" ? (
            <EditUser
              user={value as UserPublic}
              open={editUserModal.open}
              onClose={editUserModal.onClose}
            />
          ) : (
            <EditOrder
              order={value as OrderPublic}
              open={editUserModal.open}
              onClose={editUserModal.onClose}
            />
          )}
          <Delete
            type={type}
            id={value.id}
            open={deleteModal.open}
            onClose={deleteModal.onClose}
          />
        </MenuContent>
      </MenuRoot>
    </>
  )
}

export default ActionsMenu
