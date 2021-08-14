#helper.py
import numpy as np
import os
import logging

def get_file_extension(source_file):
    return os.path.splitext(source_file)[1]

def get_logger():
    logging.basicConfig(level=logging.DEBUG,
                        format="[%(levelname)-5s] %(asctime)s.%(msecs)d %(filename)s:%(lineno)s (%(name)s) %(message)s",
                        datefmt='%H:%M:%S',
                        )   
    logging.getLogger("pdfminer").setLevel(logging.ERROR)
    logging.getLogger("ocrmypdf").setLevel(logging.ERROR)
    logging.getLogger("PIL").setLevel(logging.ERROR)
    logging.getLogger("img2pdf").setLevel(logging.ERROR)