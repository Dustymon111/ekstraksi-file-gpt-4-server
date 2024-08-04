from flask import Flask, jsonify, logging, request
from langchain_google_firestore import FirestoreVectorStore
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.pdf_loader import load_and_split_pdf
from dotenv import load_dotenv
import numpy as np
import os
import firebase_admin
from firebase_admin import credentials, firestore
from file_search import file_search
import prompt_template

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

bookExtraction = prompt_template.BookExtraction
questionMaker = prompt_template.QuestionMaker

# Get the base upload directory from the environment variable or use 'uploads' as default
base_upload_dir = os.getenv('TEMP_DIR', 'uploads')

# Customize the folder path, e.g., TEMP_DIR/temp
custom_upload_dir = os.path.join(base_upload_dir, 'temp')

# Ensure the custom directory exists
os.makedirs(custom_upload_dir, exist_ok=True)
app.config['UPLOAD_FOLDER'] = custom_upload_dir


@app.route('/ekstrak-info', methods=['POST'])
def uploadFile():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        return jsonify({'data':  file_search(
            description=bookExtraction.description, 
            instruction=bookExtraction.instruction, 
            prompt_template=bookExtraction.bookExtractionTemplate, 
            filePath=file_path
        )})
    except Exception as e: 
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while processing the request'}), 500




@app.route('/')
def hello():
    return "Hello, New World!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
