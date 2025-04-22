import { IconButton } from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"

import type { ClientPublic } from "@/client"
import DeleteClient from "@/components/Clients/DeleteClient"
import EditClient from "@/components/Clients/EditClient"
import { MenuContent, MenuRoot, MenuTrigger } from "@/components/ui/menu"

interface ClientActionsMenuProps {
    client: ClientPublic
}

export const ClientActionsMenu = ({ client }: ClientActionsMenuProps) => {
    return (
        <MenuRoot>
            <MenuTrigger asChild>
                <IconButton variant="ghost" color="inherit" >
                    <BsThreeDotsVertical />
                </IconButton>
            </MenuTrigger>
            <MenuContent>
                <EditClient client={client} />
                <DeleteClient id={client.id} />
            </MenuContent>
        </MenuRoot>
    )
}
export default ClientActionsMenu