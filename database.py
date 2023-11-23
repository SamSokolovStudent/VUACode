import os
from pymongo import MongoClient
from dotenv import load_dotenv
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Load your environment variables
dotenv_path = '.env'
load_dotenv(dotenv_path)
MONGODB_ATLAS_CLUSTER_URI = os.getenv('MONGODB_URI')
os.environ['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY')


class ResearchPaperDB:
    def __init__(self, db_name, collection_name):
        self.client = MongoClient(MONGODB_ATLAS_CLUSTER_URI)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.embeddings = OpenAIEmbeddings(disallowed_special=())
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=150)

    def get_client(self):
        return self.client

    def get_collection(self):
        return self.collection

    def get_db(self):
        return self.db

    def insert_paper(self, title, abstract, year, body, authors, external_id, metadata):
        # Combine and embed the title and abstract
        title_abstract = title + " " + abstract
        title_abstract_embedding = self.embeddings.embed_documents([title_abstract])[0]

        # Split the body text
        body_chunks = self.text_splitter.split_text(body)

        # Structure document for MongoDB
        document = {
            "title": title,
            "abstract": abstract,
            "year": year,
            "embedding": title_abstract_embedding,
            "body": [{"chunk": chunk} for chunk in body_chunks],
            "authors": authors,
            "External ID": external_id,
            "metadata": metadata
        }

        # Insert the document into MongoDB
        self.collection.insert_one(document)

    def embed_query(self, text):
        # Get the embedding for the text
        return self.embeddings.embed_query(text)

    def find_similar_documents(self, embedding, index_name, embedding_field, limit=5):
        # Use MongoDB's $search operator with the vector function to find similar documents
        # index name is paperSearchIndex
        # embedding is the embedding of the query
        # embedding field is title_abstract_embedding
        documents = list(self.collection.aggregate([
            {
                "$vectorSearch": {
                    "queryVector": embedding,
                    "path": embedding_field,
                    "numCandidates": 50,
                    "limit": limit,
                    "index": index_name
                }
            }
        ]))
        return documents

DB_NAME = "twinning_papers"
COLLECTION_NAME = "papers"
db = ResearchPaperDB(DB_NAME, COLLECTION_NAME)

mockup_query = "The impact of quantum computing on the future of technology"

# Step 1: Embed the query
query_embedding = db.embed_query(mockup_query)

# Step 2: Find similar documents based on the embedding
# Index name and embedding field are given according to your specifications
similar_documents = db.find_similar_documents(
    embedding=query_embedding,
    index_name="paperSearchIndex",
    embedding_field="embedding"
)

# Display the similar documents
for document in similar_documents:
    print(document['title'])