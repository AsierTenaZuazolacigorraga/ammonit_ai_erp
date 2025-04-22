import { SkeletonText, Table } from "@chakra-ui/react"

const PendingClients = () => {
    return (
        <Table.Root size={{ base: "sm", md: "md" }}>
            <Table.Header>
                <Table.Row>
                    <Table.ColumnHeader w="sm">Nombre</Table.ColumnHeader>
                    <Table.ColumnHeader w="sm">Clasificador</Table.ColumnHeader>
                    <Table.ColumnHeader w="sm">Estructura</Table.ColumnHeader>
                    <Table.ColumnHeader w="sm">Acciones</Table.ColumnHeader>
                </Table.Row>
            </Table.Header>
            <Table.Body>
                {Array.from({ length: 5 }).map((_, i) => (
                    <Table.Row key={i}>
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
}

export default PendingClients 