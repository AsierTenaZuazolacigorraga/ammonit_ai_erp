import {
  Button,
  Container,
  Heading,
  Text,
  useDisclosure,
} from "@chakra-ui/react"

import DeleteConfirmation from "./DeleteConfirmation"

const DeleteAccount = () => {
  const confirmationModal = useDisclosure()

  return (
    <>
      <Container maxW="full">
        <Heading size="sm" py={4}>
          Eliminar Cuenta
        </Heading>
        <Text>
          Eliminar permanentemente todos tus datos y actividad, así como el perfil de usuario.
        </Text>
        <Button colorPalette="red" mt={4} onClick={confirmationModal.onOpen}>
          Eliminar
        </Button>
        <DeleteConfirmation
          open={confirmationModal.open}
          onClose={confirmationModal.onClose}
        />
      </Container>
    </>
  )
}
export default DeleteAccount
