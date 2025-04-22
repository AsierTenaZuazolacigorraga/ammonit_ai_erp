import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
  Button,
  DialogActionTrigger,
  DialogTitle,
  Input,
  VStack
} from "@chakra-ui/react"
import { useState } from "react"
import { FaPlus } from "react-icons/fa"

import { type OrderCreate, OrdersService } from "@/client"
import type { ApiError } from "@/client/core/ApiError"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import { useDropzone } from "react-dropzone"
import {
  DialogBody,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTrigger
} from "../ui/dialog"
import { Field } from "../ui/field"

const AddOrder = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { errors, isSubmitting },
  } = useForm<OrderCreate>({
    mode: "onBlur",
    criteriaMode: "all"
  })

  const mutation = useMutation({
    mutationFn: (data: OrderCreate) =>
      OrdersService.createOrder({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Order created successfully.")
      reset()
      setIsOpen(false)
    },
    onError: (err: ApiError) => {
      handleError(err)
    },
    onSettled: () => {
      queryClient.invalidateQueries({ queryKey: ["orders"] })
    },
  })

  const onSubmit: SubmitHandler<OrderCreate> = async (data) => {
    // Set the current date
    const dateUtc = new Date().toISOString()
    const dateLocalRaw = new Date();
    const dateLocal = new Date(dateLocalRaw.getTime() - dateLocalRaw.getTimezoneOffset() * 60000).toISOString();
    setValue("date_utc", dateUtc)
    setValue("date_local", dateLocal)

    // Mutate all
    mutation.mutate({
      ...data,
      date_utc: dateUtc,
      date_local: dateLocal,
    })
  }

  // Dropzone file handling
  const onDrop = (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {

      // Set the filename to the form field
      setValue("in_document_name", file.name)

      const reader = new FileReader()
      reader.onloadend = () => {
        const base64String = (reader.result as string).split(",")[1] // Extract only Base64 data
        // Set the blob in the form
        setValue("in_document_base64", base64String)
      }

      // Use readAsDataURL to get a base64-encoded string
      reader.readAsDataURL(file);
    }
  }
  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] }, // accept only pdf files
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024, // 5MB
    disabled: isSubmitting || mutation.isPending, // Disable when submitting or loading
  })

  return (
    <DialogRoot
      size={{ base: "xs", md: "md" }}
      placement="center"
      open={isOpen}
      onOpenChange={({ open }) => setIsOpen(open)}
    >
      <DialogTrigger asChild>
        <Button value="add-order" my={4}>
          <FaPlus fontSize="16px" />
          Añadir Pedido
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Añadir Pedido</DialogTitle>
          </DialogHeader>
          <DialogBody>
            {/* <Text mb={4}>Rellena los detalles para añadir un nuevo pedido.</Text> */}
            <VStack gap={4}>
              <Field
                required
                label="Documento de Pedido"
                invalid={!!errors.in_document_name}
                errorText={errors.in_document_name?.message}
              >
                <div {...getRootProps()} style={{
                  border: "2px dashed #ccc",
                  padding: "10px",
                  backgroundColor: isSubmitting || mutation.isPending ? "#f5f5f5" : "transparent",
                  opacity: isSubmitting || mutation.isPending ? 0.6 : 1,
                  cursor: isSubmitting || mutation.isPending ? "not-allowed" : "pointer",
                }}>
                  <input {...getInputProps()} />
                  <p>Arrastra y suelta el archivo aquí o haz clic para seleccionar uno (.pdf hasta 5MB)</p>
                </div>
                <Input
                  {...register("in_document_name", {
                    required: "Se requiere el documento de pedido.",
                  })}
                  placeholder="Documento de Pedido"
                  type="text"
                  readOnly
                  variant="subtle"
                />
              </Field>
            </VStack>
          </DialogBody>

          <DialogFooter gap={2}>
            {!(isSubmitting || mutation.isPending) && (
              <DialogActionTrigger asChild>
                <Button
                  variant="subtle"
                  colorPalette="gray"
                  disabled={isSubmitting}
                >
                  Cancelar
                </Button>
              </DialogActionTrigger>
            )}
            <Button
              variant="solid"
              type="submit"
              loading={isSubmitting || mutation.isPending}
              loadingText="Procesando..."
            >
              Guardar
            </Button>
          </DialogFooter>
        </form>
        {/* <DialogCloseTrigger /> */}
      </DialogContent>
    </DialogRoot>
  )
}

export default AddOrder
