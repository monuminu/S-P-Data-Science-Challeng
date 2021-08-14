#digitize.py
import os
import numpy as np
from .util import helper
from .pdf import processor as pdf_processor
import logging
logger = logging.getLogger()

class digitize:
    def __init__(self):
        pass
    def run(self, source_file, dest, *args, **kwargs):
        source_file_extension = helper.get_file_extension(source_file)
        if source_file_extension == ".pdf":
            return pdf_processor.run(source_file, dest)
    
def digitize_document(source_file, dest, *args, **kwargs):
    helper.get_logger()
    logging.info(f'Source file is {source_file}')
    obj_digitize = digitize()
    return obj_digitize.run(source_file, dest, *args, **kwargs)
    
if __name__ == '__main__':
    digitize_document('/mnt/d/Data_Science_Work/intelligent_document_digitization/examples/2.pdf', 
                    '/mnt/d/Data_Science_Work/intelligent_document_digitization/dest')  

