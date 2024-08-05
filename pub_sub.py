import os
import json
import logging
from google.cloud import pubsub_v1, firestore
import prompt_template
from file_search import file_search

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Firestore client
db = firestore.Client()
project_id = os.getenv('GCLOUD_PROJECT')
subscription_name = os.getenv('GC_PUBSUB_EP_SUBSCRIPTION')

# Initialize Pub/Sub subscriber client
subscriber = pubsub_v1.SubscriberClient()
subscription_path = subscriber.subscription_path(project_id, subscription_name)

bookExtraction = prompt_template.BookExtraction
questionMaker = prompt_template.QuestionMaker

def callback(message):
    logging.debug(f"Received message: {message}")
    try:
        message_data = json.loads(message.data.decode('utf-8'))
        logging.debug(f"Message data: {message_data}")
        file_path = message_data['file_path']
        userId = message_data['userId']
        bookUrl = message_data['bookUrl']
        totalPages = message_data['totalPages']

        # Call your file_search function
        extractData = file_search(
            description=bookExtraction.description,
            instruction=bookExtraction.instruction,
            prompt_template=bookExtraction.bookExtractionTemplate,
            filePath=file_path
        )
        logging.debug(f"Extracted data: {extractData}")

        # Fetch books for the current user
        books_ref = db.collection('books')
        book_query = books_ref.where('userId', '==', userId).stream()

        # Check for duplicates
        is_duplicate = any(
            doc.to_dict().get('title') == extractData['title'] and
            doc.to_dict().get('author') == extractData['author']
            for doc in book_query
        )
        logging.debug(f"Is duplicate: {is_duplicate}")

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
                new_book_id = new_book_ref[1].id
                # Add new documents in the 'subjects' subcollection
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
            except Exception as e:
                logging.error(f'Error creating book document or adding subjects: {e}')
                message.nack()  # Re-deliver the message
                return

        message.ack()  # Acknowledge the message
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        message.nack()

# Subscribe to the topic
streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
logging.info(f'Listening for messages on {subscription_path}')

try:
    streaming_pull_future.result()
except KeyboardInterrupt:
    streaming_pull_future.cancel()
