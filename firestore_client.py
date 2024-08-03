from google.cloud import firestore
import os

def get_firestore_client():
    project_id = os.getenv('GCLOUD_PROJECT')
    if not project_id:
        raise ValueError("GCLOUD_PROJECT is not set in the environment variables.")
    return firestore.Client(project=project_id)
