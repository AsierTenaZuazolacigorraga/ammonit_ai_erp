import { Box, Button, Center, HStack, Spinner, Text } from '@chakra-ui/react';
import { useState } from 'react';
import { Document, Page, pdfjs } from 'react-pdf';
import 'react-pdf/dist/esm/Page/AnnotationLayer.css';
import 'react-pdf/dist/esm/Page/TextLayer.css';

pdfjs.GlobalWorkerOptions.workerSrc = '/pdf.worker.min.js';

interface DocumentViewerProps {
    base64Document: string;
    title?: string;
}

const DocumentViewer = ({ base64Document }: DocumentViewerProps) => {
    const [numPages, setNumPages] = useState<number | null>(null);
    const [pageNumber, setPageNumber] = useState<number>(1);

    const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
        setNumPages(numPages);
    };

    const goToPrevPage = () => {
        if (pageNumber > 1) {
            setPageNumber(pageNumber - 1);
        }
    };

    const goToNextPage = () => {
        if (numPages && pageNumber < numPages) {
            setPageNumber(pageNumber + 1);
        }
    };


    return (
        <Box>
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
                {numPages && numPages > 1 && (
                    <HStack justify="center" mt={2}>
                        <Button
                            size="sm"
                            onClick={goToPrevPage}
                            disabled={pageNumber <= 1}
                        >
                            Anterior
                        </Button>
                        <Text>
                            Página {pageNumber} de {numPages}
                        </Text>
                        <Button
                            size="sm"
                            onClick={goToNextPage}
                            disabled={pageNumber >= numPages}
                        >
                            Siguiente
                        </Button>
                    </HStack>
                )}
            </Box>
        </Box>
    );
};

export default DocumentViewer; 