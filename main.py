from flask import Flask, jsonify, logging, request
from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import credentials, firestore
from file_search import file_search
import prompt_template
from datetime import date

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
    # Fetch books for the current user
    books_ref = db.collection('books')
    book_query = books_ref.where('userId', '==', userId).stream()
    user_ref = db.collection('users').document(userId)

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
            return jsonify({'error': 'Failed to create book document'}), 500
        

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
                subjects_ref.add(subject_data)
                if i == len(extractData['topics']) - 1:
                    subjects_ref.add({
                        'title': "Custom Topic",
                        'description': "Exercises for custom topic",
                        'questionSetIds': [],
                        'bookmarkId': new_book_id,
                        'sortIndex': i + 1,
                    })
        except Exception as e:  
            return jsonify({'error': 'Failed to add subjects'}), 500
        
        try:
            # Reference to the user document
            user_ref = db.collection('users').document(userId)

            # Get the current bookmarkIds
            user_doc = user_ref.get()
            if not user_doc.exists:
                return jsonify({"message": "User does not exist"}), 404

            current_data = user_doc.to_dict()
            current_bookmark_ids = current_data.get('bookmarkIds', [])

            # Add the new bookmarkId to the list if it's not already present
            if new_book_id not in current_bookmark_ids:
                current_bookmark_ids.append(new_book_id)
                # Update the document
                user_ref.update({"bookmarkIds": current_bookmark_ids})

        except Exception as e:
            return jsonify({"message": f"Cannot add bookmark ID to user's list: {str(e)}"}), 500

    return jsonify({'data': extractData, 'message': "succesfully extracting data from file"})

@app.route('/question-maker', methods=['POST'])
def question_maker():

    data = request.get_json()
    topic = data.get('topics')
    title = data.get('title')
    m_choice_number = data.get('m_choice_number')
    essay_number = data.get('essay_number')
    difficulty = data.get('difficulty')
    language = data.get('language')
    userId = data.get('userId')
    filename = data.get('filename')
    subjectId = data.get('subjectId')
    bookId = data.get('bookId')
    questionMaker = prompt_template.QuestionMaker(topic=topic, m_choice_number=m_choice_number, essay_number=essay_number, difficulty=difficulty, language=language)
    filepath = "./uploads/{}/{}".format(userId, filename)

    questionSetData = file_search(
        description=questionMaker.description, 
        instruction=questionMaker.instruction, 
        prompt_template=questionMaker.questionMakerTemplate(), 
        filePath=filepath
    )

    questionSetRef = db.collection('question_set')
    subject_ref = db.collection('books').document(bookId).collection('subjects')
    user_ref = db.collection('users').document(userId)
    custom_topic_docs = subject_ref.where('title', '==', 'Custom Topic').stream()

     # Initialize a variable to hold the subject ID
    custom_topic_id = None
    
    # Get the first document that matches the "Custom Topic"
    for doc in custom_topic_docs:
        custom_topic_id = doc.id
        break  # Stop after the first match since we only need one

    # Determine the subject ID to use
    selected_subject_id = custom_topic_id if len(topic) != 1 else subjectId

    try:
        new_questionSet_ref = questionSetRef.add({
            "point": 0,
            "title": title,
            "status": "Belum Selesai",
            "selectedOptions": {},
            "subjectId": selected_subject_id,
            "questionCount": len(questionSetData),
            "createdAt": date.today().isoformat()
        })
    except Exception as e:
        return jsonify({'error': 'Failed to create question set document'}), 500
    
    new_questionSet_id = new_questionSet_ref[1].id

    subject_ref.document(selected_subject_id).update({
        'questionSetIds': firestore.ArrayUnion([new_questionSet_id])
    })
    user_ref.update({
        'questionSetIds': firestore.ArrayUnion([new_questionSet_id])
    })

    # Add new documents in the 'subjects' subcollection
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
            question_ref.add(question_data)
    except Exception as e:
        return jsonify({'error': 'Failed adding questions to question set'}), 500


    return jsonify({'data': questionSetData, 'message': "succesfully making question Set from file"})


@app.route('/essay-checker', methods=['POST'])
def essay_checker():

    data = request.get_json()
    answers = data.get('answers')
    userId = data.get('userId')
    filename = data.get('filename')
    questionSetId = data.get('questionSetId')
    duration = data.get('duration')
    essay_check_template = prompt_template.EssayChecker(answers=answers)
    filepath = "./uploads/{}/{}".format(userId, filename)

    check_result = file_search(
        description=essay_check_template.description,
        instruction=essay_check_template.description,
        prompt_template=essay_check_template.essayCheckerTemplate(),
        filePath=filepath
    )

    questionSetRef = db.collection('question_set').document(questionSetId)
    question_collection = questionSetRef.collection('question')

    questionSetRef.set({
        'finishedAt': date.today().isoformat(),
        'duration' : duration
    }, merge=True) 

    # Iterate over the check_result['answers']
    for result in check_result['answers']:
        # Query to find the document with the matching question text
        question_doc = question_collection.where('text', '==', result['question'])
        # Update the correctOption in the matching document(s)
        for doc in question_doc.stream():
            doc.reference.update({
                'correctOption': result['correctOption']
            })

    return jsonify({"data": check_result,'message': "succesfully checking answer"})
    


@app.route('/')
def hello():
    return "Hello, New World!"

if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", '8080')),host='0.0.0.0',debug=True)
