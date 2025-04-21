import { IconButton } from "@chakra-ui/react"
import { BsThreeDotsVertical } from "react-icons/bs"

import type { OrderPublic } from "@/client"

import DeleteOrder from "@/components/Orders/DeleteOrder"
// import EditOrder from "@/components/Orders/EditOrder"
import { MenuContent, MenuRoot, MenuTrigger } from "@/components/ui/menu"

interface OrderActionsMenuProps {
    order: OrderPublic
}

export const OrderActionsMenu = ({ order }: OrderActionsMenuProps) => {
    return (
        <MenuRoot>
            <MenuTrigger asChild>
                <IconButton variant="ghost" color="inherit">
                    <BsThreeDotsVertical />
                </IconButton>
            </MenuTrigger>
            <MenuContent>
                {/* <EditOrder order={order} /> */}
                <DeleteOrder id={order.id} />
            </MenuContent>
        </MenuRoot>
    )
}
export default OrderActionsMenu
