from flask import Flask, jsonify, logging, request
from dotenv import load_dotenv
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


bookExtraction = prompt_template.BookExtraction



@app.route('/ekstrak-info', methods=['POST'])
def upload_file():
    file = request.files['file']
    userId = request.form.get('userId')
    bookUrl = request.form.get('bookUrl')
    totalPages = request.form.get('totalPages')

    # Get the base upload directory from the environment variable or use 'uploads' as default
    base_upload_dir = "./uploads/{}".format(userId)


    # Ensure the custom directory exists
    os.makedirs(base_upload_dir, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = base_upload_dir

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
                "userId": userId,
                "filename": file.filename
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

    return jsonify({'data': extractData, 'message': "succesfully extracting data from file"})

@app.route('/question-maker', methods=['POST'])
def question_maker():

    data = request.get_json()
    topic = data.get('topic')
    m_choice_number = data.get('m_choice_number')
    essay_number = data.get('essay_number')
    difficulty = data.get('difficulty')
    userId = data.get('userId')
    filename = data.get('filename')
    subjectId = data.get('subjectId')
    questionMaker = prompt_template.QuestionMaker(topic=topic, m_choice_number=m_choice_number, essay_number=essay_number, difficulty=difficulty)
    filepath = "./uploads/{}/{}".format(userId, filename)

    print("processing...")
    questionSetData = file_search(
        description=questionMaker.description, 
        instruction=questionMaker.instruction, 
        prompt_template=questionMaker.questionMakerTemplate(), 
        filePath=filepath
    )

    print(f'Question Set: {questionSetData}')
    questionSetRef = db.collection('question_set')
    try:
        new_questionSet_ref = questionSetRef.add({
            "point": 0,
            "status": "Belum Selesai",
            "selectedOptions": {},
            "subjectId": subjectId,
        })
    except Exception as e:
        print(f'Error creating question set document: {e}')
        return jsonify({'error': 'Failed to create question set document'}), 500
    
    print(f'new_questionSet_ref: {new_questionSet_ref[1].id}')  # Debug output
    new_questionSet_id = new_questionSet_ref[1].id
    # Add new documents in the 'subjects' subcollection
    print(new_questionSet_id)
    print(questionSetData)
    try:
        question_ref = questionSetRef.document(new_questionSet_id).collection('question')
        for question in questionSetData:
            question_data = {
                'text': question['text'],
                'options': question['options'] if not None else [],
                'questionSetId': new_questionSet_id,
                'type': question['type'],
                'correctOption' : question['correctOption'] if not None else ""
            }
            print(f'Adding question: {question_data}')  # Debug output
            question_ref.add(question_data)
    except Exception as e:
        print(f'Error adding Question: {e}')
        return jsonify({'error': 'Failed to Question Set'}), 500


    return jsonify({'data': questionSetData, 'message': "succesfully making question Set from file"})
    




@app.route('/')
def hello():
    return "Hello, New World!"

if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", '8080')),host='0.0.0.0',debug=True)
