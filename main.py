from flask import Flask, jsonify, request
from langchain_google_firestore import FirestoreVectorStore
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.pdf_loader import load_and_split_pdf
from dotenv import load_dotenv
import numpy as np
import os
import firebase_admin
from firebase_admin import credentials, firestore

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

# Initialize Flask app
app = Flask(__name__)

# Retrieve PROJECT_ID from environment variables
project_id = os.getenv('GCLOUD_PROJECT')

if not project_id:
    raise ValueError("GCLOUD_PROJECT is not set in the environment variables.")

# Initialize Firebase Admin SDK
cred = credentials.ApplicationDefault()
firebase_admin.initialize_app(cred, {
    'projectId': project_id,
})

db = firestore.client()

# Initialize the VertexAIEmbeddings
embedding = VertexAIEmbeddings(
    model_name="textembedding-gecko-multilingual@001",
    project=project_id,
)


@app.route('/search', methods=['POST'])
def search_endpoint():
    if request.content_type != 'application/json':
        return jsonify({'error': 'Request must be in JSON format'}), 400

    data = request.get_json()
    query_text = data.get('query_text')
    book_id = data.get('book_id')

    if not query_text:
        return jsonify({'error': 'Query text is required'}), 400

    if not book_id:
        return jsonify({'error': 'Book ID is required'}), 400

    try:
        # Fetch embeddings from Firestore
        vector_store_path = f'books/{book_id}/vector_store'
        vector_store = FirestoreVectorStore(
            collection=vector_store_path,
            embedding_service=embedding
        )   
        print(vector_store_path)
        results= vector_store.similarity_search(query_text, k=3)

        # Assuming `results` is a list of objects, extract the needed data
        serializable_results = []
        for result in results:
            # Otherwise, just convert the result to a dictionary
            serializable_results.append({ 
                "result": result.page_content
            })

        return jsonify({'results': serializable_results}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vector_store', methods=['POST'])
def vector_store_endpoint():
    if request.content_type != 'application/json':
        return jsonify({'error': 'Request must be in JSON format'}), 400


    data = request.get_json()
    pdf_path = data.get('pdf_path')
    book_id = 'book_1'

    if not pdf_path or not os.path.exists(pdf_path):
        return jsonify({'error': 'File not found'}), 400

    if not book_id:
        return jsonify({'error': 'Book ID is required'}), 400

    try:
        # Load and split the PDF content
        pages = load_and_split_pdf(pdf_path)
        texts = [str(page) for page in pages]  # Convert each page to a string

        # Store each page and its embedding using FirestoreVectorStore
        vector_store_path = f'books/{book_id}/vector_store'
        vector_store = FirestoreVectorStore(
            collection=vector_store_path,
            embedding_service=embedding
        )   
        vector_store.add_texts(texts, ids=[f'page_{i}' for i in range(len(texts))])
        
        return jsonify({'message': 'Texts and embeddings added successfully to the vector store'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/load_pdf', methods=['POST'])
def load_pdf():
    if request.content_type != 'application/json':
        return jsonify({'error': 'Request must be in JSON format'}), 400

    data = request.get_json()
    pdf_path = data.get('pdf_path')

    if not pdf_path or not os.path.exists(pdf_path):
        return jsonify({'error': 'File not found'}), 400

    try:
        pages = load_and_split_pdf(pdf_path)
        pages_str = [str(page) for page in pages]
        return jsonify({'pages': pages_str}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/')
def hello():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(debug=True)
