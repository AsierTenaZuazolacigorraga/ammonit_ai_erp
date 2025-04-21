import { IconButton } from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"

import type { UserPublic } from "@/client"
import DeleteUser from "@/components/Admin/DeleteUser"
import EditUser from "@/components/Admin/EditUser"
import { MenuContent, MenuRoot, MenuTrigger } from "@/components/ui/menu"

interface UserActionsMenuProps {
    user: UserPublic
    disabled?: boolean
}

export const UserActionsMenu = ({ user, disabled }: UserActionsMenuProps) => {
    return (
        <MenuRoot>
            <MenuTrigger asChild>
                <IconButton variant="ghost" color="inherit" disabled={disabled}>
                    <BsThreeDotsVertical />
                </IconButton>
            </MenuTrigger>
            <MenuContent>
                <EditUser user={user} />
                <DeleteUser id={user.id} />
            </MenuContent>
        </MenuRoot>
    )
}
export default UserActionsMenu