# Configuração da API Gemini
import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyD6kAM6SUKioe956zaSxURcP3l8a9p1iLM"
MODEL_NAME = "gemini-2.5-flash"

def configurar_gemini():
    """Configura e testa conexão com Gemini"""
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(MODEL_NAME)
        return model, True
    except Exception as e:
        print(f"❌ Erro ao configurar Gemini: {e}")
        return None, False