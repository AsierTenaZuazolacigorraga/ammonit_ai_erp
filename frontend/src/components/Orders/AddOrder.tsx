import { type ApiError, type OrderCreate, OrdersService } from "@/client"
import { Button } from "@/components/ui/button"
import {
  DialogBackdrop,
  DialogBody,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle
} from "@/components/ui/dialog"
import { Field } from "@/components/ui/field"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils"
import { Input } from "@chakra-ui/react"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { useDropzone } from "react-dropzone"
import { type SubmitHandler, useForm } from "react-hook-form"

interface AddOrderProps {
  open: boolean
  onClose: () => void
}

const AddOrder = ({ open, onClose }: AddOrderProps) => {

  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    formState: { isSubmitting, errors },
  } = useForm<OrderCreate>({
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: {
      date_local: "",
      date_utc: "",
      in_document: "",
      in_document_name: "",
    },
  })

  const mutation = useMutation({
    mutationFn: (data: OrderCreate) =>
      OrdersService.createOrder({ requestBody: data }),
    onSuccess: () => {
      showSuccessToast("Pedido creado correctamente.")
      reset()
      onClose()
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
        setValue("in_document", base64String)
      }

      reader.readAsArrayBuffer(file) // Read the file
    }
  }
  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] }, // accept only pdf files
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024, // 5MB
  })

  return (
    <>
      <DialogRoot
        open={open}
        onExitComplete={onClose}
        size={{ base: "sm", md: "md" }}
      >
        <DialogBackdrop />
        <DialogContent as="form" onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Añadir Pedido</DialogTitle>
            {/* <DialogCloseTrigger /> */}
          </DialogHeader>
          <DialogBody pb={6}>
            <Field
              required
              label="Documento de Pedido"
              invalid={!!errors.in_document_name}
              errorText={errors.in_document_name?.message}
            >
              <div {...getRootProps()} style={{ border: "2px dashed #ccc", padding: "10px" }}>
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
          </DialogBody>
          <DialogFooter gap={3}>
            <Button colorPalette="green" type="submit" loading={isSubmitting}>
              Guardar
            </Button>
            <Button onClick={onClose}>Cancelar</Button>
          </DialogFooter>
        </DialogContent>
      </DialogRoot>
    </>
  )
}

export default AddOrder
