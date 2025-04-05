import os
import sys
import sqlite3
from src.exception import CustomException
from src.logger import logger
import fitz


def read_pdf_to_string(path,start = 0):
    """
    Returns:
        str: The concatenated text content of all pages in the PDF document.
    """
    doc = fitz.open(path)
    content = ""
    for page_num in range(start,len(doc)):
        page = doc[page_num]
        content += page.get_text()
    return content
