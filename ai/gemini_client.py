# Cliente para API Gemini
import google.generativeai as genai
from config.gemini_config import GEMINI_API_KEY, MODEL_NAME, configurar_gemini

class GeminiClient:
    """Cliente para interagir com a API Gemini"""
    
    def __init__(self):
        self.model, self.disponivel = configurar_gemini()
    
    def gerar_resposta(self, pergunta, dados):
        """Gera resposta usando Gemini"""
        if not self.disponivel or not self.model:
            return None
        
        try:
            contexto = self.criar_contexto(pergunta, dados)
            response = self.model.generate_content(contexto)
            return response.text if response.text else "Desculpe, não entendi sua pergunta."
        except Exception as e:
            print(f"❌ Erro ao gerar resposta: {e}")
            return None
    
    def criar_contexto(self, pergunta, dados):
        """Cria contexto para a pergunta"""
        return f"""Você é um especialista em engenharia elétrica chamado PowerGrid AI Assistant.

DADOS ATUAIS DO SISTEMA:
- Tensão: {dados['tensao']:.1f} V
- Corrente: {dados['corrente']:.3f} A  
- Potência Ativa: {dados['potencia_ativa']:.1f} W
- Fator de Potência: {dados['fator_potencia']:.3f}
- Consumo aproximado: {dados['potencia_ativa']/1000:.3f} kW

PERGUNTA: {pergunta}

Responda em português, de forma técnica mas clara, com dicas práticas. Seja conciso e útil.
Máximo: 300 palavras."""