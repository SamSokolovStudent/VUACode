# Test document to set up the database for the project using chromadb

import chromadb

chroma_client = chromadb.Client()


def setup():
    collection = chroma_client.create_collection(name="my_collection")
    collection.add(documents=["This is a test document", "This is another test document"],
               metadatas=[{"name": "test1", "value": "test1"}, {"name": "test2", "value": "test2"}],
               ids=["id1", "id2"])


def retrieve():
    collection = chroma_client.get_collection(name="my_collection")
    results = collection.query(query_texts=["this is for testing"], n_results=2)
    print(results)


if __name__ == '__main__':
    setup()
    retrieve()
