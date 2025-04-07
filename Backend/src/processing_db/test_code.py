from src.exception import CustomException
from src.utils import search_similar_documents, display_results

if __name__ == "__main__":
    try:
        query = "consumer protection app"
        results = search_similar_documents(query)
        display_results(results)
        
    except CustomException as e:
        print(f"An error occurred: {e}")