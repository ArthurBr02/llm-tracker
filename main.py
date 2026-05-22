import openrouter
import ollama
import lmstudio


if __name__ == "__main__":
    print("Checking for new models...")
    print("----------------------------------")
    print("OpenRouter:")
    openrouter.execute()
    print("----------------------------------")
    print("Ollama:")
    ollama.execute()
    print("----------------------------------")
    print("LM Studio:")
    lmstudio.execute()