import { toaster } from "@/components/ui/toaster"

const useCustomToast = () => {
  const showToast = (
    title: string,
    description: string,
    type: "success" | "error",
  ) => {
    toaster.create({
      title,
      description,
      type,
      meta: { closable: true },
    })
  }

  const showErrorToast = (description: string) => {
    showToast("Error!", description, "error")
  }

  const showSuccessToast = (description: string) => {
    showToast("Éxito!", description, "success")
  }

  return { showToast, showSuccessToast, showErrorToast }
}

export default useCustomToast
