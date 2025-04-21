import type { OrderPublic, UserPublic } from "@/client"
import { IconButton } from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"
import { MenuContent, MenuRoot, MenuTrigger } from "../ui/menu"


interface ActionsMenuProps {
  type: string
  value: OrderPublic | UserPublic
  disabled?: boolean
}

export const ActionsMenu = ({ type }: ActionsMenuProps) => {
  console.log(type)
  return (
    <MenuRoot>
      <MenuTrigger asChild>
        <IconButton variant="ghost" color="inherit">
          <BsThreeDotsVertical />
        </IconButton>
      </MenuTrigger>
      <MenuContent>
        {/* <Edit item={type} />
        <Delete id={type.id} /> */}
      </MenuContent>
    </MenuRoot>
  )
}
export default ActionsMenu
