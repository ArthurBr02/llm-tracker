import openrouter
import ollama
import lmstudio
import mail

if __name__ == "__main__":
    print("Checking for new models...")
    print("----------------------------------")
    print("OpenRouter:")
    try:
        openrouter.execute()
    except Exception as e:
        print(f"Error executing OpenRouter: {e}")
        mail.send_error_notification("Erreur d'exécution - OpenRouter", str(e))

    print("----------------------------------")
    print("Ollama:")
    try:
        ollama.execute()
    except Exception as e:
        print(f"Error executing Ollama: {e}")
        mail.send_error_notification("Erreur d'exécution - Ollama", str(e))
        
    print("----------------------------------")
    print("LM Studio:")
    try:
        lmstudio.execute()
    except Exception as e:
        print(f"Error executing LM Studio: {e}")
        mail.send_error_notification("Erreur d'exécution - LM Studio", str(e))

    print("----------------------------------")
    print("Done.")