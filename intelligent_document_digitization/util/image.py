import os

def get_page_image():    
    page_image_file = os.path.join("/mnt/d/Data_Science_Work/intelligent_document_digitization/examples","page_1.png")
    first_page.to_image(resolution = 300).save(os.path.join("/mnt/d/Data_Science_Work/intelligent_document_digitization/examples","page_1.png"))