import ocrmypdf
import os
import sys
import logging
logger = logging.getLogger()
#export PATH=$HOME/.local/bin:$PATH
#export LD_LIBRARY_PATH=/usr/local/lib

def get_searchable_pdf(source_file, pages):
    output_file = source_file.replace(".pdf", "_converted.pdf")
    ocrmypdf.ocr(input_file=source_file, output_file=output_file, pages = pages,
                deskew=True, rotate_pages=True, clean=True, skip_text=True)
    return output_file