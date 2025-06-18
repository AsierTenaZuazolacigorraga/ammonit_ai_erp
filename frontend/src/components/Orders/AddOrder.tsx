import { useMutation, useQueryClient } from "@tanstack/react-query"
import { type SubmitHandler, useForm } from "react-hook-form"

import {
  Button,
  DialogTitle,
  VStack
} from "@chakra-ui/react"
import { useState } from "react"
import { FaPlus } from "react-icons/fa"

import { OrdersService } from "@/client"
import { ApiError } from "@/client/core/ApiError"
import DropZone from "@/components/Common/DropZone"
import useCustomToast from "@/hooks/useCustomToast"
import { handleError } from "@/utils/utils"
import {
  DialogBody,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTrigger
} from "../ui/dialog"

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

  // File drop handler
  const handleFileDrop = (file: File) => {
    setValue("base_document_name", file.name, { shouldValidate: true })
    setValue("base_document", file, { shouldValidate: true })
  }

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
              <DropZone
                onFileDrop={handleFileDrop}
                fileName={currentFileName}
                isDisabled={isSubmitting || mutation.isPending}
                error={errors.base_document_name?.message || errors.base_document?.message}
                label="Documento"
              />
            </VStack>
          </DialogBody>
          <DialogFooter gap={2}>
            <Button variant="subtle" colorPalette="gray" disabled={isSubmitting || mutation.isPending}>
              Cancelar
            </Button>
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
