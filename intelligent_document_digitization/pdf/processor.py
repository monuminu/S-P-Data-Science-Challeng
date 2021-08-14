import numpy as np
import pdfplumber
from pikepdf import Pdf
from .. import ocr, segmentation
import os
import sys
import shutil
import logging
logger = logging.getLogger(__name__)

class pdfprocessor():
    """ PDF Processing Class """
    def __init__(self, source_file, dest, *args, **kwargs):
        self.source_file = source_file
        self.dest = dest
        self.page_pdfs_dir = os.path.join(self.dest, "page_pdfs")
        os.makedirs(self.page_pdfs_dir, exist_ok = True)
        self.page_images_dir = os.path.join(self.dest, "page_images")
        os.makedirs(self.page_images_dir, exist_ok = True)
        
    def process(self):
        """
            Process the PDF file parallely
        """
        processed_pages_details = []
        with pdfplumber.open(self.source_file) as pdf:
            for page in pdf.pages:
                processed_pages_details.append(self.process_page(page))
        self.cleanup_directory()
        return processed_pages_details
    
    def process_page(self, page):
        page_component = self.get_page_component(page)
        segments = self.get_page_segment(page, page_component)
        return segments

    def get_page_component(self, page):
        """
            process PDF page 
        """
        page_number = page.page_number
        logger.debug(f"Processing Page Number {page_number}")
        isPageImage = False
        image_blocks = []
        words = []
        image_objects = page.images
    
        if image_objects:
            page_pdf_file = self.get_pdf_from_page(page_number)
            page_pdf_file = ocr.get_searchable_pdf(page_pdf_file, None)
            with pdfplumber.open(page_pdf_file) as pdf:
                page = pdf.pages[0]
                words = page.extract_words(x_tolerance=2, y_tolerance=2)
                page_width = page.width
                page_height = page.height
                for image_object in image_objects:
                    if float(image_object.get("height")) >= 0.95 * float(page_height) and float(image_object.get("width")) >= 0.95 * float(page_width):
                        logger.debug(f'Page number {page_number} is a scanned !')
                        isPageImage = True
                        break
                    else:
                        image_block = {"width" : float(image_object.get("width")) , "height" : float(image_object.get("height")),
                                       "x0" : image_object.get("x0"), "x0" : image_object.get("y0"),
                                       "x1" : image_object.get("x1"), "x0" : image_object.get("y0")}
                        image_blocks = image_blocks.append(image_block)
        else:
            logger.debug(f'Page number {page_number} is a text based !')
            page_width = page.width
            page_height = page.height
            words = page.extract_words(x_tolerance=2, y_tolerance=2)
        
        logger.debug(f"No of words in Page is {len(words)}")
        
        return {"image_blocks" : image_blocks, "words" : words, "isPageImage" : isPageImage, "page_number" : page_number,
                "page_width" : page_width , "page_height" : page_height}

    def get_page_segment(self,page, page_component):
        words, width, height = page_component.get("words"), int(page_component.get("page_width")), int(page_component.get("page_height"))
        median_word_height = np.median([word["bottom"] - word["top"] for word in page_component.get("words")])
        page_matrix = segmentation.get_image_from_words(words, width, height)
        tb_cuts, lr_cuts = segmentation.get_lr_tb_cuts(page_matrix)
        segments = segmentation.label_segment(tb_cuts, lr_cuts, median_word_height)
        segmentation.debug_segmentation(page, width, height, segments, os.path.join(self.page_images_dir, str(page.page_number) + "_debug_.png"))
        return segments

    def get_pdf_from_page(self, page_number):
        with Pdf.open(self.source_file) as pdf:
            pdf_page = Pdf.new()
            pdf_page.pages.append(pdf.pages[page_number - 1])
            page_pdf_file = os.path.join(self.page_pdfs_dir, str(page_number) + ".pdf")
            pdf_page.save(page_pdf_file)
        return page_pdf_file
    
    def get_page_image_file(self, page, page_number):    
        page_image_file = os.path.join(self.dest, str(page_number) + ".png")
        page.to_image(resolution = 300).save(page_image_file)
        return page_image_file

    def cleanup_directory(self):
        shutil.rmtree(self.page_pdfs_dir)
        #shutil.rmtree(self.page_images_dir)

def run(source_file, dest, *args, **kwargs):
    obj_pdfprocessor = pdfprocessor(source_file, dest, *args, **kwargs)
    return obj_pdfprocessor.process()

