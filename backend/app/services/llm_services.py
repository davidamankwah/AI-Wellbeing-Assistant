from langchain_ollama import ChatOllama
from langchain_core.messages import SystemMessage, HumanMessage

# Connect to Ollama model running locally
llm = ChatOllama(
    model="qwen2.5:3b",
    base_url="http://localhost:11434",
    temperature=0.2
)

def generate_response(message: str) -> str:
    """
    Test communication with the local LLM.

    This function is for development testing only.
    It is not yet connected to the student chat endpoint.
    """

    messages = [
        SystemMessage(
            content=(
                "You are participating in a software development "
                "connectivity test. Respond briefly and clearly. "
                "Do not provide mental health advice."
            )
        ),
        HumanMessage(content=message)
    ]

    response = llm.invoke(messages)

    return str(response.content)