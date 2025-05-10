import base64
from io import BytesIO

import PyPDF2
from app.logger import get_logger
from app.models import User

logger = get_logger(__name__)


def _remove_pages_from_pdf(irrelevant_keywords: list[str], pdf_binary: bytes) -> bytes:

    # Create a new PDF writer
    pdf_writer = PyPDF2.PdfWriter()

    # Read the PDF from binary data
    pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_binary))

    # Process each page until we find irrelevant content
    for i in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[i]
        text = page.extract_text().lower()

        # Check if page contains irrelevant content
        if any(keyword.lower() in text for keyword in irrelevant_keywords):
            # Stop processing once we find irrelevant content
            break

        # Add relevant page to the new PDF
        pdf_writer.add_page(page)

    # If we filtered out all pages, keep at least the first page
    if len(pdf_writer.pages) == 0 and len(pdf_reader.pages) > 0:
        pdf_writer.add_page(pdf_reader.pages[0])

    # Instead of saving to a file, write to a BytesIO object
    output_buffer = BytesIO()
    pdf_writer.write(output_buffer)

    # Get the binary data from the buffer
    output_buffer.seek(0)
    return output_buffer.getvalue()


def _preprocess_document(document: bytes, document_name: str, user: User) -> bytes:

    ##############################################################
    # Generics here

    ##############################################################
    if user.email == "asier.tena.zu@outlook.com":

        if document_name.endswith(".pdf"):
            document = _remove_pages_from_pdf(
                [
                    'Conditions Générales d\'Achat entre MATISA Matériel Industriel SA ("Matisa") et ses Fournisseurs ("Fournisseur")',
                ],
                document,
            )

    return document
