from app.services.llm_services import generate_response

def main():
    print("Testing local Ollama connection...\n")

    message = "Explain what Python is in one sentence."

    try:
        response = generate_response(message)

        print("Test Message:", message)
        print("\nLLM response:", response)
        print("\nLocal LLM connection successful!")

    except Exception as error:
        print("Local LLM connection failed.")
        print("Error:", error)


if __name__ == "__main__":
    main()

      

