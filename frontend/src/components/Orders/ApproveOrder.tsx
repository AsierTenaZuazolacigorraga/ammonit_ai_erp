import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from 'react';
import { type SubmitHandler, useForm } from "react-hook-form";

import {
    Button,
    DialogActionTrigger,
    DialogTitle
} from "@chakra-ui/react";
import { FaCheckCircle } from "react-icons/fa";

import { type OrderPublic, OrdersService } from "@/client";
import type { ApiError } from "@/client/core/ApiError";
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils";
import GridTable from "../Common/GridTable";
import {
    DialogBody,
    DialogContent,
    DialogFooter,
    DialogHeader,
    DialogRoot,
    DialogTrigger
} from "../ui/dialog";

interface ApproveOrderProps {
    order: OrderPublic
}

const ApproveOrder = ({ order }: ApproveOrderProps) => {
    const [isOpen, setIsOpen] = useState(false)
    const queryClient = useQueryClient()
    const { showSuccessToast } = useCustomToast()

    const {
        handleSubmit,
        formState: { isSubmitting },
    } = useForm<OrderPublic>({
        mode: "onBlur",
        criteriaMode: "all",
        defaultValues: order,
    })

    const mutation = useMutation({
        mutationFn: () => {
            return OrdersService.updateOrder({
                id: order.id,
                requestBody: {
                    is_approved: true,
                    date_approved: new Date().toISOString(),
                    // content_processed: convertGridToCSV(rows, columns) // Temporarily removed
                }
            })
        },
        onSuccess: () => {
            showSuccessToast("Pedido aprobado correctamente.")
            setIsOpen(false)
        },
        onError: (err: ApiError) => {
            handleError(err)
        },
        onSettled: () => {
            queryClient.invalidateQueries({ queryKey: ["orders"] })
        },
    })

    const onSubmit: SubmitHandler<OrderPublic> = async () => {
        mutation.mutate()
    }

    if (!!order.is_approved) {
        return (
            <Button
                variant="ghost"
                size="sm"
                colorScheme="green"
                opacity={0.2}
                cursor="not-allowed"
                disabled
            >
                <FaCheckCircle fontSize="16px" />
            </Button>
        )
    }

    return (
        <DialogRoot
            size={{ base: "sm", md: "xl" }}
            placement="center"
            open={isOpen}
            onOpenChange={({ open }) => setIsOpen(open)}
        >
            <DialogTrigger asChild>
                <Button
                    variant="ghost"
                    size="sm"
                    colorScheme="green"
                    disabled={isSubmitting}
                >
                    <FaCheckCircle fontSize="16px" />
                </Button>
            </DialogTrigger>
            <DialogContent>
                <form onSubmit={handleSubmit(onSubmit)}>
                    <DialogHeader>
                        <DialogTitle>Aprobar Pedido</DialogTitle>
                    </DialogHeader>
                    <DialogBody>
                        <GridTable inputData={order.content_processed || ''} />
                    </DialogBody>
                    <DialogFooter gap={2}>
                        <DialogActionTrigger asChild>
                            <Button
                                variant="subtle"
                                colorPalette="gray"
                                disabled={isSubmitting}
                            >
                                Cancelar
                            </Button>
                        </DialogActionTrigger>
                        <Button
                            variant="solid"
                            type="submit"
                            loading={isSubmitting}
                            colorScheme="green"
                        >
                            Aprobar
                        </Button>
                    </DialogFooter>
                </form>
            </DialogContent>
        </DialogRoot>
    )
}

export default ApproveOrder
