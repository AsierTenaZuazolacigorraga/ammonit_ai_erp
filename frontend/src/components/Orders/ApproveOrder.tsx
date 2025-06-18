import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from 'react';
import { type SubmitHandler, useForm } from "react-hook-form";

import {
    Box,
    Button,
    DialogActionTrigger,
    DialogTitle,
    Grid,
    Text
} from "@chakra-ui/react";
import { FaCheckCircle, FaEye } from "react-icons/fa";

import { type OrderPublic, OrdersService } from "@/client";
import type { ApiError } from "@/client/core/ApiError";
import DocumentViewer from "@/components/Common/DocumentViewer";
import TableViewer from '@/components/Common/TableViewer';
import useCustomToast from "@/hooks/useCustomToast";
import { handleError } from "@/utils/utils";
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
    const [updatedContent, setUpdatedContent] = useState<string>(order.content_processed || '')
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
            return OrdersService.approveOrder({
                id: order.id,
                requestBody: {
                    content_processed: updatedContent
                }
            })
        },
        onSuccess: () => {
            showSuccessToast("Documento aprobado correctamente.")
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

    const handleDataChange = (csvData: string) => {
        setUpdatedContent(csvData);
    };

    if (order.state !== "PENDING") {
        return (
            <DialogRoot
                size="xl"
                placement="center"
                open={isOpen}
                onOpenChange={({ open }) => setIsOpen(open)}
            >
                <DialogTrigger asChild>
                    <Button
                        variant="ghost"
                        size="sm"
                        colorScheme="gray"
                        opacity={0.5}
                    >
                        <FaEye fontSize="16px" />
                    </Button>
                </DialogTrigger>
                <DialogContent maxW="95vw">
                    <DialogHeader>
                        <DialogTitle>Ver Documento</DialogTitle>
                    </DialogHeader>
                    <DialogBody>
                        <Grid templateColumns="auto 1fr" gap={8} alignItems="flex-start">
                            <Box
                                width="595px"
                                display="flex"
                                flexDirection="column"
                                alignItems="center"
                                minW="0"
                                pr={2}
                            >
                                <Text fontWeight="bold" mb={2} alignSelf="flex-start">Documento Base</Text>
                                <DocumentViewer base64Document={order.base_document || ''} />
                            </Box>
                            <Box maxH="80vh" overflow="auto" minW={0} width="100%">
                                <Text fontWeight="bold" mb={2}>Información Extraída</Text>
                                <TableViewer
                                    inputData={order.content_processed || ''}
                                    readOnly={true}
                                    allowRowEdit={false}
                                />
                            </Box>
                        </Grid>
                    </DialogBody>
                    <DialogFooter>
                        <DialogActionTrigger asChild>
                            <Button
                                variant="subtle"
                                colorPalette="gray"
                            >
                                Cerrar
                            </Button>
                        </DialogActionTrigger>
                    </DialogFooter>
                </DialogContent>
            </DialogRoot>
        )
    }

    return (
        <DialogRoot
            size="xl"
            placement="center"
            open={isOpen}
            onOpenChange={({ open }) => setIsOpen(open)}
        >
            <DialogTrigger asChild>
                <Button
                    variant="ghost"
                    size="sm"
                    colorScheme="orange"
                    disabled={isSubmitting}
                >
                    <FaCheckCircle fontSize="16px" />
                </Button>
            </DialogTrigger>
            <DialogContent maxW="95vw">
                <form onSubmit={handleSubmit(onSubmit)}>
                    <DialogHeader>
                        <DialogTitle>Aprobar Documento</DialogTitle>
                    </DialogHeader>
                    <DialogBody>
                        <Grid templateColumns="auto 1fr" gap={8} alignItems="flex-start">
                            <Box
                                width="595px"
                                display="flex"
                                flexDirection="column"
                                alignItems="center"
                                minW="0"
                                pr={2}
                            >
                                <Text fontWeight="bold" mb={2} alignSelf="flex-start">Documento Base</Text>
                                <DocumentViewer base64Document={order.base_document || ''} />
                            </Box>
                            <Box maxH="80vh" overflow="auto" minW={0} width="100%">
                                <Text fontWeight="bold" mb={2}>Información Extraída</Text>
                                <TableViewer
                                    inputData={updatedContent}
                                    onDataChange={handleDataChange}
                                    readOnly={false}
                                    allowRowEdit={true}
                                />
                            </Box>
                        </Grid>
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
