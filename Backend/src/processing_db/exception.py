import sys
from logger import logger  

def error_message_detail(error, error_detail: sys):
    """Extracts detailed error message including file name and line number."""
    _, _, exc_tb = error_detail.exc_info()
    file_name = exc_tb.tb_frame.f_code.co_filename
    error_message = (
        f"Error occurred in script [{file_name}] at line [{exc_tb.tb_lineno}]: {str(error)}"
    )
    return error_message

class CustomException(Exception):
    """Custom Exception class to handle and log errors."""
    def __init__(self, error_message, error_detail: sys):
        super().__init__(error_message)
        self.error_message = error_message_detail(error_message, error_detail)

        # Log the error
        logger.error(self.error_message)

    def __str__(self):
        return self.error_message

def divide_by_zero():
    """Function to trigger an exception."""
    try:
        result = 10 / 0  # This will cause a ZeroDivisionError
    except Exception as e:
        logger.error("Exception occurred!", exc_info=True)
        raise CustomException(e, sys)

if __name__ == "__main__":
    divide_by_zero()