from flask import Flask, jsonify, logging, request
from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import credentials, firestore
from file_search import file_search
import prompt_template
from google.cloud import pubsub_v1

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

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, os.getenv('GC_PUBSUB_EP_TOPIC'))

# # Initialize the VertexAIEmbeddings
# embedding = VertexAIEmbeddings(
#     model_name="textembedding-gecko-multilingual@001",
#     project=project_id,
# )

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
def upload_file():
    file = request.files['file']
    userId = request.form.get('userId')
    bookUrl = request.form.get('bookUrl')
    totalPages = request.form.get('totalPages')

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    extractData = file_search(
        description=bookExtraction.description, 
        instruction=bookExtraction.instruction, 
        prompt_template=bookExtraction.bookExtractionTemplate, 
        filePath=file_path
    )

    print(f'extractData: {extractData}')

    # Fetch books for the current user
    books_ref = db.collection('books')
    book_query = books_ref.where('userId', '==', userId).stream()

    # Check for duplicates
    is_duplicate = any(
        doc.to_dict().get('title') == extractData['title'] and
        doc.to_dict().get('author') == extractData['author']
        for doc in book_query
    )

    if not is_duplicate:
        # Create a new document reference for the book
        try:
            new_book_ref = books_ref.add({
                "title": extractData['title'],
                "author": extractData['author'],
                "bookUrl": bookUrl,
                "totalPages": int(totalPages),
                "userId": userId
            })
        except Exception as e:
            print(f'Error creating book document: {e}')
            return jsonify({'error': 'Failed to create book document'}), 500
        
        print(f'new_book_ref: {new_book_ref[1].id}')  # Debug output
        new_book_id = new_book_ref[1].id
        # Add new documents in the 'subjects' subcollection
        try:
            subjects_ref = books_ref.document(new_book_id).collection('subjects')
            for i, subject in enumerate(extractData['topics']):
                subject_data = {
                    'title': subject['title'],
                    'description': subject['description'],
                    'questionSetIds': [],
                    'bookmarkId': new_book_id,
                    'sortIndex': i,
                }
                print(f'Adding subject: {subject_data}')  # Debug output
                subjects_ref.add(subject_data)
        except Exception as e:
            print(f'Error adding subjects: {e}')
            return jsonify({'error': 'Failed to add subjects'}), 500

    return jsonify({'data': extractData})
    




@app.route('/')
def hello():
    return "Hello, New World!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
