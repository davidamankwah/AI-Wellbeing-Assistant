
from app.schemas import ChatResponse, ChatSource


# Test 1: Response with a retrieved source
response = ChatResponse(
    response="Consider planning your revision.",
    status="LOW",
    sources=[
        ChatSource(
            id="cccu-exam-anxiety",
            title="Exams",
            publisher="Canterbury Christ Church University",
            url="https://students.canterbury.ac.uk/learning-skills-hub/exams"
        )
    ]
)

result = response.model_dump()

assert len(result["sources"]) == 1
assert result["sources"][0]["title"] == "Exams"

print("PASS: Source metadata included")


# Test 2: Static safeguarding response
high_response = ChatResponse(
    response="Please seek immediate support.",
    status="HIGH"
)

assert high_response.sources == []

print("PASS: Static response has no RAG sources")


# Test 3: No shared mutable default list
first = ChatResponse(response="First", status="LOW")
second = ChatResponse(response="Second", status="LOW")

first.sources.append(
    ChatSource(
        id="test",
        title="Test",
        publisher="Test publisher"
    )
)

assert second.sources == []

print("PASS: Source lists are independent")

print("\nAll source schema tests passed!")
