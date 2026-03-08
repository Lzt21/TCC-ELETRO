# Gerenciamento de dados e cálculos
import math
import random

class DataManager:
    """Gerencia os dados do sistema e cálculos elétricos"""
    
    def __init__(self, tensao_referencia=127.0):
        self.tensao_referencia = tensao_referencia
        self.faixa_tensao_min = 0
        self.faixa_tensao_max = 300
        
        self.dados = {
            'tensao': 0.0,
            'corrente': 0.0,
            'temperatura': 0.0,
            'potencia_ativa': 0.0,
            'fator_potencia': 0.0,
            'potencia_aparente': 0.0,
            'potencia_reativa': 0.0
        }
        
        # Histórico
        self.historico_tensao = []
        self.historico_corrente = []
        self.historico_potencia = []
        self.timestamps = []
    
    def atualizar_dados(self, tensao, corrente):
        """Atualiza dados básicos e calcula derivados"""
        self.dados['tensao'] = tensao
        self.dados['corrente'] = corrente
        self.calcular_dados_derivados()
    
    def calcular_dados_derivados(self):
        """Calcula todos os dados derivados"""
        v = self.dados['tensao']
        i = self.dados['corrente']
        
        # Potência aparente
        self.dados['potencia_aparente'] = v * i
        
        # Fator de potência (simulado com pequeno ângulo)
        angulo_fase_graus = random.uniform(0, 5)
        angulo_fase_rad = math.radians(angulo_fase_graus)
        self.dados['fator_potencia'] = math.cos(angulo_fase_rad)
        
        # Potência ativa e reativa
        self.dados['potencia_ativa'] = v * i * self.dados['fator_potencia']
        sin_phi = math.sqrt(max(0, 1 - self.dados['fator_potencia']**2))
        self.dados['potencia_reativa'] = v * i * sin_phi
        
        # Temperatura simulada
        self.dados['temperatura'] = 25 + (self.dados['potencia_ativa'] * 0.02)
    
    def adicionar_ao_historico(self):
        """Adiciona dados atuais ao histórico"""
        if self.dados['tensao'] > 0:
            timestamp = len(self.timestamps)
            self.timestamps.append(timestamp)
            self.historico_tensao.append(self.dados['tensao'])
            self.historico_corrente.append(self.dados['corrente'])
            self.historico_potencia.append(self.dados['potencia_ativa'])
    
    def definir_referencia(self, nova_referencia):
        """Define nova tensão de referência e ajusta faixa"""
        self.tensao_referencia = nova_referencia
        self.faixa_tensao_min = max(0, nova_referencia - 100)
        self.faixa_tensao_max = nova_referencia + 100
    
    def calcular_eficiencia(self):
        """Calcula eficiência baseada no FP"""
        return min(100, self.dados['fator_potencia'] * 100 * 1.1)
    
    def calcular_qualidade_energia(self):
        """Calcula qualidade da energia baseada na tensão"""
        margem = 15
        min_esperado = self.tensao_referencia - margem
        max_esperado = self.tensao_referencia + margem
        
        if min_esperado <= self.dados['tensao'] <= max_esperado:
            return 98.0
        return 85.0
    
    def adicionar_ao_historico(self):
        #Adiciona dados atuais ao histórico com limite
        if self.dados['tensao'] > 0:
            timestamp = len(self.timestamps)
            self.timestamps.append(timestamp)
            self.historico_tensao.append(self.dados['tensao'])
            self.historico_corrente.append(self.dados['corrente'])
            self.historico_potencia.append(self.dados['potencia_ativa'])
        
        # 🔥 LIMITE CRÍTICO - Manter apenas 100 pontos
        MAX_HISTORICO = 100
        if len(self.timestamps) > MAX_HISTORICO:
            self.timestamps = self.timestamps[-MAX_HISTORICO:]
            self.historico_tensao = self.historico_tensao[-MAX_HISTORICO:]
            self.historico_corrente = self.historico_corrente[-MAX_HISTORICO:]
            self.historico_potencia = self.historico_potencia[-MAX_HISTORICO:]