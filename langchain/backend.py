from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # api_key="...",
    # base_url="...",
    # organization="...",
    # other params...
)

messages = [
    (
        "system",
        "You are a helpful translator. Translate the user sentence to French.",
    ),
    ("human", "I love programming."),
]
ai_msg = llm.invoke(messages)
ai_msg.usage_metadata


# from typing import Optional

# from langchain_core.pydantic_v1 import BaseModel, Field


# class Joke(BaseModel):
#     '''Joke to tell user.'''

#     setup: str = Field(description="The setup of the joke")
#     punchline: str = Field(description="The punchline to the joke")
#     rating: Optional[int] = Field(description="How funny the joke is, from 1 to 10")


# structured_llm = llm.with_structured_output(Joke)
# structured_llm.invoke("Tell me a joke about cats")

# json_llm = llm.bind(response_format={"type": "json_object"})
# ai_msg = json_llm.invoke(
#     "Return a JSON object with key 'random_ints' and a value of 10 random ints in [0-99]"
# )
# ai_msg.content