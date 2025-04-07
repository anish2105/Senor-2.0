import processing_db.test_code as test_code
from exception import CustomException

if __name__ == "__main__":
    try:
        query = "what happens to sellers when the product is defective"
        results = test_code.search_similar_documents(query)
        test_code.display_results(results)
        
    except CustomException as e:
        print(f"An error occurred: {e}")
