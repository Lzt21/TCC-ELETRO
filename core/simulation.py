# Simulação de dados
import random

class SimulationManager:
    """Gerencia simulação de dados quando não há conexão serial"""
    
    def __init__(self, tensao_referencia=127.0):
        self.tensao_referencia = tensao_referencia
    
    def gerar_dados(self):
        """Gera dados simulados"""
        if self.tensao_referencia > 0:
            base_tensao = self.tensao_referencia
        else:
            base_tensao = 127.0
        
        # Variação de tensão
        variacao_tensao = random.uniform(-5, 5)
        
        # Corrente baseada na potência (60W)
        potencia_aproximada = 60
        corrente_esperada = potencia_aproximada / base_tensao
        variacao_corrente = random.uniform(-0.05, 0.05)
        
        return {
            'tensao': base_tensao + variacao_tensao,
            'corrente': corrente_esperada + variacao_corrente
        }