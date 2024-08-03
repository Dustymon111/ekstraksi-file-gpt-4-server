from langchain_google_firestore import FirestoreVectorStore
from langchain_google_vertexai import VertexAIEmbeddings

embedding = VertexAIEmbeddings(
    model_name="textembedding-gecko@latest",
    # project=PROJECT_ID,
)

# Sample data
ids = ["apple", "banana", "orange"]
fruits_texts = ['{"name": "apple"}', '{"name": "banana"}', '{"name": "orange"}']

# Specify the subcollection path
subcollection_path = "fruits/vector_data"

# Create a vector store with the subcollection path
vector_store = FirestoreVectorStore(
    collection=subcollection_path,
    embedding=embedding,
)

# Add the fruits to the vector store
vector_store.add_texts(fruits_texts, ids=ids)
