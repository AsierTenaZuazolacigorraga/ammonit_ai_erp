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

import { OrdersService } from "@/client"
import { ApiError } from "@/client/core/ApiError"
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

// Define local type for the form's state
interface AddOrderFormData {
  base_document: File | null;
  base_document_name: string | null;
}

const AddOrder = () => {
  const [isOpen, setIsOpen] = useState(false)
  const queryClient = useQueryClient()
  const { showSuccessToast } = useCustomToast()
  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch, // Keep watch to display filename
    formState: { errors, isSubmitting },
  } = useForm<AddOrderFormData>({ // Use local form type
    mode: "onBlur",
    criteriaMode: "all",
    defaultValues: { // Add default values
      base_document: null,
      base_document_name: null
    }
  })

  // Watch filename for display input
  const currentFileName = watch("base_document_name");

  const mutation = useMutation({
    mutationFn: (data: AddOrderFormData) => {
      if (!(data.base_document instanceof File)) {
        return Promise.reject(new Error("Archivo de documento no válido."));
      }
      // Cast to any to bypass outdated generated type check
      return OrdersService.createOrder({
        formData: {
          base_document: data.base_document,
        }
      });
    },
    onSuccess: () => {
      showSuccessToast("Documento creado correctamente.")
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

  // onSubmit uses local form type
  const onSubmit: SubmitHandler<AddOrderFormData> = async (data) => {
    // Only mutate needed, no date setting
    mutation.mutate(data)
  }

  // onDrop sets fields for local form type (no change needed)
  const onDrop = (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (file) {
      setValue("base_document_name", file.name, { shouldValidate: true })
      setValue("base_document", file, { shouldValidate: true })
    }
  }
  // useDropzone setup (no change needed)
  const { getRootProps, getInputProps } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    maxFiles: 1,
    maxSize: 5 * 1024 * 1024,
    disabled: isSubmitting || mutation.isPending,
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
          Añadir Documento
        </Button>
      </DialogTrigger>
      <DialogContent>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogHeader>
            <DialogTitle>Añadir Documento</DialogTitle>
          </DialogHeader>
          <DialogBody>
            <VStack gap={4}>
              <Field
                required
                label="Documento"
                // Use correct field names for errors
                invalid={!!errors.base_document_name || !!errors.base_document}
                errorText={errors.base_document_name?.message || errors.base_document?.message}
              >
                <div {...getRootProps()} style={{
                  border: "2px dashed #ccc",
                  padding: "10px",
                  textAlign: "center", // Center text
                  backgroundColor: isSubmitting || mutation.isPending ? "#f5f5f5" : "transparent",
                  opacity: isSubmitting || mutation.isPending ? 0.5 : 1,
                  cursor: isSubmitting || mutation.isPending ? "not-allowed" : "pointer",
                }}>
                  <input {...getInputProps()} />
                  <p>Arrastra y suelta el archivo aquí o haz clic para seleccionar uno (.pdf hasta 5MB)</p>
                </div>
                <Input
                  {...register("base_document_name", { // Register for validation
                    required: "Se requiere el documento.",
                  })}
                  placeholder="Nombre del documento"
                  value={currentFileName || ""} // Display watched name
                  type="text"
                  readOnly
                  variant="subtle"
                  mt={2} // Add margin
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
      </DialogContent>
    </DialogRoot>
  )
}

export default AddOrder
