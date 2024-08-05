from openai import OpenAI # Version 1.33.0
from openai.types.beta.threads.message_create_params import Attachment, AttachmentToolFileSearch
import json
from dotenv import load_dotenv
import os

# Load environment variables
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

MY_OPENAI_KEY = os.getenv('API_KEY')  # Add your OpenAI API key
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

    # Because the Assistant can't produce JSON (as we're using "file_search"),
    # it will likely output text + some JSON code. We can parse and extract just
    # the JSON part, and ignore everything else (eg. gpt4o will start with something
    # similar to "Of course, here's the parsed text: {useful_JSON_here}")
    if res_txt.startswith('```json'):
        res_txt = res_txt[6:]
    if res_txt.endswith('```'):
        res_txt = res_txt[:-3]
    res_txt = res_txt[:res_txt.rfind('}')+1]
    res_txt = res_txt[res_txt.find('{'):]
    res_txt.strip()


    # Parse the JSON output
    data = json.loads(res_txt)

    return data

    # Delete the file(s) afterward to preserve space (max 100gb/company)
    # delete_ok = client.files.delete(file.id)

if __name__ == '__main__':
    extractData= file_search(
                description="you are an assistant to retrieve information from file", 
                instruction="You are a helpful assistant designed to output only JSON. retrieve the exact information from the file that has been given.", 
                prompt_template="What is the title of the file? usually it's on the first page and in bold", 
                filePath="https://ff1d59341418f13dfb68dcaf69d2571b55df9fda0c3758677186ea0-apidata.googleusercontent.com/download/storage/v1/b/ektraksi-file-gpt-4.appspot.com/o/uploads%2Ft9A2vrKOd5ftGSlMlrS3j0AXymt2%2Fafe056718edc8058b7f712386bfabbcf5acdedb94dbd7d4af266bf0e560582ed.pdf?jk=AYBlUPBkDUuPaFm66tJ61WsT3C7OVgz2DJmja0ZpJqug0i9BxBe0WAksKPE22AswyaiJRB09JFkEH21KRuzxpBGvEu6zWN-nkr_1a0ibYvif71wMEIAaO50ejX-gWoCOnWH44MxAiH2O7gVdVHxefSAVb0Q2iKMQw3P0gHdSOAT4BaiG-_9kBCsaeJVHpLDj3sJwoM5rbaUaFxgk2FquFEGH-1JwI4ugtv0ndnpe-DTro1j75XagE-Y0D3SJPTYKKZ7N1KQvkTSavkbuxovNbkY_HBW7K5D2VPaNuZ6SAnuTm7pGoWdh-vbzOn1FuElVJqdlpUi7Vdpwq4jK-e6NCbjZXj4LJspaGiysOyxTIxpZMBnfyt6mXIegPB0U1bW1szRSt930FXmCzsuk9uP5WlJcs2mVBYdkkm2Z4ooA2O_54JjYEn9vAY6QkaSbEk0Dc3hXh4jnrvO3w8vFvWKze4f87M143VINo-ETzoqCrBKAOKL5BmyoXqyfu4HPBchyuSilYSdWytECJ4GrmRdUJgmkTQ1xIEQX1JWaqSKRciYI0Jh8Eu9wT1VBjKNvUJB3e4wgrla9KXsYNqs_CiTzdRauDoNm_t921QjVQysyfshD9XPJLkpAFeM4ewiMThbUyetMkhNi0NVedR9SZCYF-meUw3-ynCfnbF3ZKMn6ZqhP35hvw3eAGZIQh2jqVzgRHCjFsP1YX3PNBHiZdTLnjfxfA0q6G6ZvwI14mG6-aM4aSfeWb4Pb7OMKK-H5U2Am3rP8igRsMhZPMJzKnoDrzXy9nKYOlKS_8_KBP8l3p8whzWmX88nXNIHZQiB42co1hjUZkZHqp6zSc6Tt2h1lRLAQcUZJ1tt2dm6AjBUZaZ5nbuPkJy2Jfp3_hxXGQ2yKFY9EP9A0NuGTZDq86GUdN49-hrI4jiaX8mr4XVkCUfCeWNLMVRgdJ2NQAkJ-AUXrMqIitK0lrG5oW6vVUXzx19K4YwCvj7sHz--At4nZ29mNsyM6f4x15_PvSPrP1DFdGDlbvmUigYsiQ5x2c1lioNW3Nnmj2gRuN-IOesqGeRMNESWkRBb_H-RefWvhdlguENifZjJbFFq_OTb9X0U33PzVr3iMneckWvZAihRiWoX94M6l7dJYS8cDdFOkzVlVo50BwR8fs_94QoQq-xvwkmGfntPm_amQy_3At2i39yVqzugMb20D_m1DqNCMBA1zELPPfg7qQyFPMu4_AvW_uZU7YtSsd_bgu8KzUEKsSmM-fXmmmLqbEYqkmpR8i2QI1UiwaIbJZOXLe48NY775yNEDMzJiXb7CRqeZnbzgB84-URoThg&isca=1"
            )

    print(extractData)