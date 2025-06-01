import { Input } from "@chakra-ui/react";
import React from "react";
import { useDropzone } from "react-dropzone";
import { Field } from "../ui/field";

interface DropZoneProps {
    onFileDrop: (file: File) => void;
    fileName: string | null;
    isDisabled?: boolean;
    error?: string;
    label?: string;
    placeholder?: string;
}

const DropZone = ({
    onFileDrop,
    fileName,
    isDisabled = false,
    error,
    label = "Documento de ejemplo (.pdf)",
    placeholder = "Nombre del documento"
}: DropZoneProps) => {
    const onDrop = (acceptedFiles: File[]) => {
        const file = acceptedFiles[0];
        if (file) {
            onFileDrop(file);
        }
    };

    const { getRootProps, getInputProps } = useDropzone({
        onDrop,
        accept: { "application/pdf": [".pdf"] },
        maxFiles: 1,
        maxSize: 5 * 1024 * 1024,
        disabled: isDisabled,
    });

    const dropzoneStyle = {
        border: "2.5px dashed #319795",
        borderRadius: "12px",
        boxShadow: "0 2px 8px rgba(49, 151, 149, 0.08)",
        padding: "18px 10px",
        textAlign: "center" as const,
        backgroundColor: isDisabled ? "#f5f5f5" : "#f9fafb",
        opacity: isDisabled ? 0.5 : 1,
        cursor: isDisabled ? "not-allowed" : "pointer",
        transition: "border-color 0.2s, box-shadow 0.2s, background 0.2s",
    };

    const handleMouseEnter = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!isDisabled) {
            e.currentTarget.style.borderColor = '#2b6cb0';
        }
    };

    const handleMouseLeave = (e: React.MouseEvent<HTMLDivElement>) => {
        if (!isDisabled) {
            e.currentTarget.style.borderColor = '#319795';
        }
    };

    return (
        <Field
            required
            label={label}
            invalid={!!error}
            errorText={error}
        >
            <div
                {...getRootProps()}
                style={dropzoneStyle}
                onMouseEnter={handleMouseEnter}
                onMouseLeave={handleMouseLeave}
            >
                <input {...getInputProps()} />
                <p>Arrastra y suelta el archivo aquí o haz clic para seleccionar uno (.pdf hasta 5MB)</p>
            </div>
            <Input
                placeholder={placeholder}
                value={fileName || ""}
                type="text"
                readOnly
                variant="subtle"
                mt={2}
            />
        </Field>
    );
};

export default DropZone; 