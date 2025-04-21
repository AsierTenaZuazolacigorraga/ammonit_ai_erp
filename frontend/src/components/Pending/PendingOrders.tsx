import { Table } from "@chakra-ui/react"
import { SkeletonText } from "../ui/skeleton"

const PendingOrders = () => (
    <Table.Root size={{ base: "sm", md: "md" }}>
        <Table.Header>
            <Table.Row>
                <Table.ColumnHeader w="sm">Fecha</Table.ColumnHeader>
                <Table.ColumnHeader w="sm">Documento de Pedido</Table.ColumnHeader>
                <Table.ColumnHeader w="sm">Documento Procesado</Table.ColumnHeader>
                <Table.ColumnHeader w="sm">Acciones</Table.ColumnHeader>
            </Table.Row>
        </Table.Header>
        <Table.Body>
            {[...Array(4)].map((_, index) => (
                <Table.Row key={index}>
                    <Table.Cell>
                        <SkeletonText noOfLines={1} />
                    </Table.Cell>
                    <Table.Cell>
                        <SkeletonText noOfLines={1} />
                    </Table.Cell>
                    <Table.Cell>
                        <SkeletonText noOfLines={1} />
                    </Table.Cell>
                    <Table.Cell>
                        <SkeletonText noOfLines={1} />
                    </Table.Cell>
                </Table.Row>
            ))}
        </Table.Body>
    </Table.Root>
)

export default PendingOrders