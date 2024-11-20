import base64
import logging
import os
from typing import List

from constants import *
from pdf2image import convert_from_path
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter


def merge_pdfs(pdf_folder: str, pdf_file: str) -> str:

    # Create a PDF writer object
    writer = PdfWriter()

    # List all files in the folder and filter to include only PDFs
    pdf_files_in_folder = [
        f
        for f in os.listdir(pdf_folder)
        if f.endswith(".pdf") and not f == os.path.basename(pdf_file)
    ]
    pdf_files_in_folder.sort()  # Optional: Sort files alphabetically if needed

    # Check if there are any PDF files in the folder
    if not pdf_files_in_folder:
        logging.warning("No PDF files found in the folder.")
        return

    # Loop through each PDF file and add its pages to the writer
    for pdf_file_in_folder in pdf_files_in_folder:
        pdf_path = os.path.join(pdf_folder, pdf_file_in_folder)
        reader = PdfReader(pdf_path)

        # Add all pages from the current PDF to the writer
        for page in reader.pages:
            writer.add_page(page)

    # Write the combined pages to the output file
    with open(pdf_file, "wb") as f:
        writer.write(f)

    logging.info(f"Merged PDF saved as: {pdf_file}")

    return pdf_file


def png_2_base64(image_file: str) -> str:
    if os.path.isfile(image_file) and os.path.splitext(image_file)[1].lower() == ".png":
        with open(image_file, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    else:
        logging.warning(f"Image file not found: {image_file}")
    return ""


def pngs_2_base64(image_files: List[str]) -> List[str]:
    images_base64 = []
    for image_file in image_files:
        images_base64.append(png_2_base64(image_file))
    return images_base64


def pdf_2_pngs(
    pdf_file: str,
    png_folder: str,
) -> List[str]:

    # Ensure the output folder exists
    if not os.path.exists(png_folder):
        os.makedirs(png_folder)

    # Loop through each image (page)
    i = 0
    images = convert_from_path(pdf_file)
    images_files = []
    for image in images:

        # Define the PNG file name
        images_files.append(os.path.join(png_folder, f"page_{i + 1}.png"))

        # Save the image as PNG
        image.save(images_files[i], "PNG")

        # Manage index
        i += 1

    return images_files


def organise_students_pngs(png_files: List[str]) -> List[List[str]]:
    return [
        [
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_1_page_1.png",
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_1_page_2.png",
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_1_page_3.png",
        ],
        [
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_2_page_1.png",
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_2_page_2.png",
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_2_page_3.png",
        ],
        [
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_3_page_1.png",
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_3_page_2.png",
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_3_page_3.png",
        ],
        [
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_4_page_1.png",
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_4_page_2.png",
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_4_page_3.png",
        ],
        [
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_5_page_1.png",
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_5_page_2.png",
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_5_page_3.png",
        ],
        [
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_6_page_1.png",
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_6_page_2.png",
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_6_page_3.png",
        ],
        [
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_7_page_1.png",
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_7_page_2.png",
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_7_page_3.png",
        ],
        [
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_8_page_1.png",
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_8_page_2.png",
            "/home/atena/my_projects/proff_ai/.gitignores/kepa/fiki_production/students_png/student_8_page_3.png",
        ],
    ]
