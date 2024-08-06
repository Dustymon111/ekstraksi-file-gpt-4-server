from openai import OpenAI # Version 1.33.0
from openai.types.beta.threads.message_create_params import Attachment, AttachmentToolFileSearch
import json
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

MY_OPENAI_KEY = os.environ.get('API_KEY')  # Add your OpenAI API key
client = OpenAI(api_key=MY_OPENAI_KEY)


def file_search(description, instruction, prompt_template, filePath):
    # Upload your pdf(s) to the OpenAI API
    file = client.files.create(
        file=open(filePath, 'rb'),
        purpose='assistants'
    )

    # Create thread
    thread = client.beta.threads.create()

    # Create an Assistant (or fetch it if it was already created). It has to have
    # "file_search" tool enabled to attach files when prompting it.
    def get_assistant():
        for assistant in client.beta.assistants.list():
            if assistant.name == 'My Assistant Name':
                return assistant

        # No Assistant found, create a new one
        return client.beta.assistants.create(
            model='gpt-4o',
            description= description,
            instructions= instruction,
            tools=[{"type": "file_search"}],
            # response_format={"type": "json_object"}, # Isn't possible with "file_search"
            name='My Assistant Name',
        )

    # Add your prompt here
    prompt = prompt_template

    client.beta.threads.messages.create(
        thread_id = thread.id,
        role='user',
        content=prompt,
        attachments=[Attachment(file_id=file.id, tools=[AttachmentToolFileSearch(type='file_search')])]
    )

    # Run the created thread with the assistant. It will wait until the message is processed.
    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=get_assistant().id,
        timeout=300, # 5 minutes
        # response_format={"type": "json_object"}, # Isn't possible
    )

    # Eg. issue with openai server
    if run.status != "completed":
        raise Exception('Run failed:', run.status)

    # Fetch outputs of the thread
    messages_cursor = client.beta.threads.messages.list(thread_id=thread.id)
    messages = [message for message in messages_cursor]

    message = messages[0] # This is the output from the Assistant (second message is your message)
    assert message.content[0].type == "text"

    # Output text of the Assistant
    res_txt = message.content[0].text.value

    # # Because the Assistant can't produce JSON (as we're using "file_search"),
    # # it will likely output text + some JSON code. We can parse and extract just
    # # the JSON part, and ignore everything else (eg. gpt4o will start with something
    # # similar to "Of course, here's the parsed text: {useful_JSON_here}")
    if res_txt.startswith('```json'):
        res_txt = res_txt[7:]
    if res_txt.endswith('```'):
        res_txt = res_txt[:-3]
    # res_txt = res_txt[:res_txt.rfind('}')+1]
    # res_txt = res_txt[res_txt.find('{'):]
    res_txt.strip()
    # Parse the JSON output
    data = json.loads(res_txt)
    client.files.delete(file.id)

    return data

    # Delete the file(s) afterward to preserve space (max 100gb/company)