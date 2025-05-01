import { Box, Center, HStack, Spinner } from '@chakra-ui/react';
import { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';
import {
    PaginationItems,
    PaginationNextTrigger,
    PaginationPrevTrigger,
    PaginationRoot
} from "../ui/pagination";

pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';

interface DocumentViewerProps {
    base64Document: string;
    title?: string;
    maxHeight?: string;
}

const DocumentViewer = ({ base64Document, maxHeight = '80vh' }: DocumentViewerProps) => {
    const [numPages, setNumPages] = useState<number | null>(null);
    const [pageNumber, setPageNumber] = useState<number>(1);

    const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
        setNumPages(numPages);
    };

    // const goToPrevPage = () => {
    //     if (pageNumber > 1) {
    //         setPageNumber(pageNumber - 1);
    //     }
    // };

    // const goToNextPage = () => {
    //     if (numPages && pageNumber < numPages) {
    //         setPageNumber(pageNumber + 1);
    //     }
    // };


    return (
        <Box
            width="595px"
            display="flex"
            flexDirection="column"
            alignItems="center"
            minW="0"
            pr={2}
        >
            <Box
                maxHeight={maxHeight}
                overflowY="auto"
                width="100%"
                display="flex"
                flexDirection="column"
                alignItems="center"
            >
                <Box border="1px solid" borderColor="gray.200" p={2} borderRadius="md">
                    <Document
                        file={`data:application/pdf;base64,${base64Document}`}
                        onLoadSuccess={onDocumentLoadSuccess}
                        loading={
                            <Center h="100%">
                                <Spinner />
                            </Center>
                        }
                    >
                        <Page pageNumber={pageNumber} />
                    </Document>
                </Box>
            </Box>
            {numPages && numPages > 1 && (
                <Box mt={3} width="100%">
                    <PaginationRoot
                        count={numPages}
                        pageSize={1}
                        page={pageNumber}
                        onPageChange={({ page }) => setPageNumber(page)}
                    >
                        <HStack justify="center">
                            <PaginationPrevTrigger />
                            <PaginationItems />
                            <PaginationNextTrigger />
                        </HStack>
                    </PaginationRoot>
                </Box>
            )}
        </Box>
    );
};

export default DocumentViewer; 