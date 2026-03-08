# Simulador de respostas (fallback quando Gemini não está disponível)

class ResponseSimulator:
    """Simula respostas quando Gemini não está disponível"""
    
    def __init__(self, dados, tensao_referencia):
        self.dados = dados
        self.tensao_referencia = tensao_referencia
    
    def simular_resposta(self, pergunta):
        """Retorna resposta simulada baseada na pergunta"""
        pergunta_lower = pergunta.lower()
        
        respostas = {
            'economizar': self.resposta_economia(),
            'analisar': self.resposta_analise(),
            'custo': self.resposta_custo(),
            'dica': self.resposta_dicas()
        }
        
        for key, resposta in respostas.items():
            if key in pergunta_lower:
                return resposta
        
        return self.resposta_padrao(pergunta)
    
    def resposta_economia(self):
        return f"""💡 **DICAS PARA ECONOMIZAR ENERGIA:**

• **Desligue aparelhos em standby**: A TV, computador e carregadores consomem mesmo desligados
• **Use iluminação LED**: Consome até 80% menos que lâmpadas incandescentes
• **Aproveite a luz natural**: Abra cortinas durante o dia
• **Controle o ar condicionado**: Mantenha em 24°C, limpe os filtros mensalmente
• **Use eletrodomésticos eficientes**: Procure selo Procel A
• **Banhos mais curtos**: Cada minuto a menos economiza 0,5 kWh

Com seus {self.dados['potencia_ativa']:.0f}W atuais, você gasta aproximadamente {self.dados['potencia_ativa']*24/1000:.2f} kWh por dia."""
    
    def resposta_analise(self):
        return f"""📊 **ANÁLISE DOS SEUS DADOS:**

**Dados atuais:**
• Tensão: {self.dados['tensao']:.1f} V ({(self.dados['tensao']-self.tensao_referencia):+.1f}V da referência)
• Corrente: {self.dados['corrente']:.3f} A
• Potência: {self.dados['potencia_ativa']:.1f} W
• Fator de Potência: {self.dados['fator_potencia']:.3f} ({"Excelente" if self.dados['fator_potencia'] > 0.95 else "Bom"})

**Interpretação:**
1. Seu consumo equivale a uma lâmpada de {self.dados['potencia_ativa']:.0f}W
2. Custo diário: R$ {self.dados['potencia_ativa']*24*0.75/1000:.2f} (considerando R$ 0,75/kWh)
3. Consumo mensal: {self.dados['potencia_ativa']*24*30/1000:.1f} kWh

**Recomendações:**
• Verifique se há equipamentos desnecessários ligados
• Considere usar temporizadores para aparelhos"""
    
    def resposta_custo(self):
        return f"""💰 **CÁLCULO DE CUSTOS:**

**Consumo atual:** {self.dados['potencia_ativa']:.1f} W

**Custos estimados:**
• Por hora: {self.dados['potencia_ativa']/1000:.3f} kWh × R$ 0,75 = R$ {(self.dados['potencia_ativa']/1000)*0.75:.3f}
• Por dia (24h): R$ {(self.dados['potencia_ativa']*24*0.75/1000):.2f}
• Por mês (30 dias): R$ {(self.dados['potencia_ativa']*24*30*0.75/1000):.2f}

**Economia potencial:**
• Reduzindo 10% do consumo: R$ {self.dados['potencia_ativa']*24*30*0.75*0.1/1000:.2f}/mês
• Desligando 8h/dia: R$ {self.dados['potencia_ativa']*8*30*0.75/1000:.2f}/mês"""
    
    def resposta_dicas(self):
        return """🔧 **DICAS DE EFICIÊNCIA ENERGÉTICA:**

1. **Iluminação:**
   • Substitua por LEDs (economia: 50-80%)
   • Use sensores de presença em áreas comuns

2. **Eletrodomésticos:**
   • Máquina de lavar: use carga completa
   • Geladeira: mantenha 5cm de distância da parede
   • Forno: evite abrir durante o uso

3. **Climatização:**
   • Ventilador em vez de ar condicionado quando possível
   • Mantenha portas e janelas fechadas com AC ligado

4. **Hábitos:**
   • Desligue luzes ao sair do ambiente
   • Use tomadas com interruptor para eliminar standby
   • Programe horários para equipamentos"""
    
    def resposta_padrao(self, pergunta):
        return f"""🤖 **RESPOSTA SIMULADA**

Sua pergunta: "{pergunta[:50]}..."

**Dicas gerais de economia:**
• Verifique sempre o selo Procel dos equipamentos
• Faça manutenção preventiva dos aparelhos
• Use régua com filtro de linha para proteger equipamentos

**Com seus {self.dados['potencia_ativa']:.0f}W atuais:**
• Consumo diário: {self.dados['potencia_ativa']*24/1000:.2f} kWh
• Custo mensal: R$ {self.dados['potencia_ativa']*24*30*0.75/1000:.2f}"""