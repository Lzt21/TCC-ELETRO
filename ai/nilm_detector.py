"""
Módulo de Detecção de Equipamentos usando NILM (Non-Intrusive Load Monitoring)
"""
import numpy as np
import json
import os
from datetime import datetime
from collections import deque
import joblib
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings('ignore')

class NILMDetector:
    """
    Detector de equipamentos baseado em assinaturas elétricas
    """
    def __init__(self, modelo_path='models/equipamentos_model.pkl'):
        self.modelo_path = modelo_path
        self.modelo = None
        self.equipamentos = []
        self.modo_treinamento = False
        self.equipamento_atual = None
        self.buffer_treinamento = []
        self.tamanho_buffer = 50  # 50 amostras para treinar
        
        # Buffer para detecção em tempo real
        self.buffer_recente = deque(maxlen=10)
        
        # Dataset de assinaturas conhecidas (pré-treinadas)
        self.assinaturas_conhecidas = self.carregar_assinaturas_padrao()
        
        # Carregar modelo se existir
        self.carregar_modelo()
    
    def carregar_assinaturas_padrao(self):
        """
        Assinaturas elétricas típicas de equipamentos comuns
        Baseado em dados da literatura de NILM
        """
        return {
            'lampada_led': {
                'potencia_media': 9,
                'potencia_std': 1,
                'fp_medio': 0.95,
                'reativa_media': 2,
                'tipo': 'resistiva',
                'transiente': 'instantaneo'
            },
            'lampada_incandescente': {
                'potencia_media': 60,
                'potencia_std': 2,
                'fp_medio': 1.0,
                'reativa_media': 0,
                'tipo': 'resistiva',
                'transiente': 'instantaneo'
            },
            'geladeira': {
                'potencia_media': 150,
                'potencia_std': 30,
                'fp_medio': 0.85,
                'reativa_media': 45,
                'tipo': 'indutiva',
                'transiente': 'compressor_ciclico'
            },
            'tv_led': {
                'potencia_media': 80,
                'potencia_std': 10,
                'fp_medio': 0.98,
                'reativa_media': 8,
                'tipo': 'eletronica',
                'transiente': 'fonte_chaveada'
            },
            'computador': {
                'potencia_media': 120,
                'potencia_std': 25,
                'fp_medio': 0.95,
                'reativa_media': 15,
                'tipo': 'eletronica',
                'transiente': 'fonte_chaveada'
            },
            'microondas': {
                'potencia_media': 1200,
                'potencia_std': 150,
                'fp_medio': 0.92,
                'reativa_media': 180,
                'tipo': 'indutiva',
                'transiente': 'magnetron'
            },
            'ar_condicionado': {
                'potencia_media': 1500,
                'potencia_std': 200,
                'fp_medio': 0.88,
                'reativa_media': 300,
                'tipo': 'indutiva',
                'transiente': 'compressor_lento'
            },
            'ferro_eletrico': {
                'potencia_media': 1200,
                'potencia_std': 50,
                'fp_medio': 1.0,
                'reativa_media': 5,
                'tipo': 'resistiva',
                'transiente': 'termico'
            },
            'secador_cabelo': {
                'potencia_media': 1500,
                'potencia_std': 100,
                'fp_medio': 0.98,
                'reativa_media': 20,
                'tipo': 'resistiva',
                'transiente': 'ventilador+resistencia'
            }
        }
    
    def extrair_features(self, amostra):
        """
        Extrai características relevantes de uma amostra
        """
        features = {
            'potencia': amostra.get('potencia_ativa', 0),
            'corrente': amostra.get('corrente', 0),
            'fp': amostra.get('fator_potencia', 1.0),
            'reativa': amostra.get('potencia_reativa', 0),
            'tensao': amostra.get('tensao', 127),
            'relacao_pq': amostra.get('potencia_reativa', 0) / (amostra.get('potencia_ativa', 1) + 0.01),
            'potencia_aparente': amostra.get('potencia_aparente', 0)
        }
        return features
    
    def detectar_mudanca_estado(self, nova_amostra, amostra_anterior):
        """
        Detecta se houve mudança significativa (equipamento ligou/desligou)
        """
        if amostra_anterior is None:
            return False, 0
        
        delta_potencia = nova_amostra['potencia_ativa'] - amostra_anterior['potencia_ativa']
        
        # Considerar mudança significativa se > 20W (limiar ajustável)
        if abs(delta_potencia) > 20:
            return True, delta_potencia
        
        return False, 0
    
    def identificar_por_assinatura(self, features):
        """
        Identifica equipamento comparando com assinaturas conhecidas
        """
        potencia = features['potencia']
        fp = features['fp']
        reativa = features['reativa']
        
        candidatos = []
        
        for nome, assinatura in self.assinaturas_conhecidas.items():
            # Calcular similaridade baseada em múltiplos parâmetros
            dist_potencia = abs(potencia - assinatura['potencia_media']) / (assinatura['potencia_media'] + 1)
            dist_fp = abs(fp - assinatura['fp_medio'])
            dist_reativa = abs(reativa - assinatura['reativa_media']) / (assinatura['reativa_media'] + 1)
            
            # Pontuação de similaridade (0 = perfeito, quanto menor melhor)
            similaridade = (dist_potencia * 0.5 + dist_fp * 0.3 + dist_reativa * 0.2)
            
            if similaridade < 0.3:  # Limiar de similaridade
                confianca = max(0, 100 - (similaridade * 100))
                candidatos.append((nome, confianca, similaridade))
        
        # Ordenar por melhor similaridade
        candidatos.sort(key=lambda x: x[1], reverse=True)
        
        return candidatos
    
    def iniciar_treinamento(self, nome_equipamento):
        """
        Inicia o modo de treinamento para um equipamento específico
        """
        self.modo_treinamento = True
        self.equipamento_atual = nome_equipamento
        self.buffer_treinamento = []
        print(f"🎯 Iniciando treinamento para: {nome_equipamento}")
        return True
    
    def adicionar_amostra_treinamento(self, amostra):
        """Adiciona uma amostra durante o treinamento Versão CORRIGIDA com validação"""
        if not self.modo_treinamento:
            return False, 0
        
        # VALIDAR SE OS DADOS SÃO CONSISTENTES
        if amostra['potencia_ativa'] < 10:  # Ignorar ruído
            print(f"⚠️ Amostra ignorada - potência muito baixa: {amostra['potencia_ativa']:.1f}W")
            return True, len(self.buffer_treinamento) / self.tamanho_buffer * 100
        
        features = self.extrair_features(amostra)
        self.buffer_treinamento.append(features)
        
        progresso = len(self.buffer_treinamento) / self.tamanho_buffer * 100
        
        # DEBUG - mostrar a cada 10 amostras
        if len(self.buffer_treinamento) % 10 == 0:
            print(f"📊 Amostra {len(self.buffer_treinamento)}: {amostra['potencia_ativa']:.1f}W, FP: {amostra['fator_potencia']:.3f}")
        
        if len(self.buffer_treinamento) >= self.tamanho_buffer:
            self.finalizar_treinamento()
            return True, 100
        
        return True, progresso
    
    def finalizar_treinamento(self):
        """
        Finaliza o treinamento e adiciona ao dataset
        """
        if len(self.buffer_treinamento) < 10:
            print("❌ Poucas amostras para treinamento")
            self.modo_treinamento = False
            return False
        
        # Calcular features médias
        features_medias = {
            'potencia_media': np.mean([f['potencia'] for f in self.buffer_treinamento]),
            'potencia_std': np.std([f['potencia'] for f in self.buffer_treinamento]),
            'fp_medio': np.mean([f['fp'] for f in self.buffer_treinamento]),
            'reativa_media': np.mean([f['reativa'] for f in self.buffer_treinamento]),
            'corrente_media': np.mean([f['corrente'] for f in self.buffer_treinamento]),
            'relacao_pq_media': np.mean([f['relacao_pq'] for f in self.buffer_treinamento])
        }
        
        # Adicionar ao dataset de assinaturas conhecidas
        self.assinaturas_conhecidas[self.equipamento_atual] = features_medias
        
        print(f"✅ Treinamento concluído para: {self.equipamento_atual}")
        print(f"   Potência média: {features_medias['potencia_media']:.1f}W")
        print(f"   FP médio: {features_medias['fp_medio']:.3f}")
        
        self.modo_treinamento = False
        self.equipamento_atual = None
        self.buffer_treinamento = []
        
        # Salvar dataset
        self.salvar_dataset()
        
        return True
    
    def analisar_amostra(self, amostra, amostra_anterior=None):
        """
        Analisa uma amostra e tenta identificar equipamentos
        Retorna lista de equipamentos detectados e mudanças
        """
        resultados = []
        
        # Extrair features
        features = self.extrair_features(amostra)
        
        # Verificar mudança de estado
        if amostra_anterior:
            mudou, delta = self.detectar_mudanca_estado(amostra, amostra_anterior)
            
            if mudou:
                # Se ligou (delta positivo)
                if delta > 20:
                    # Tentar identificar o que ligou
                    candidatos = self.identificar_por_assinatura({
                        'potencia': delta,
                        'fp': amostra['fator_potencia'],
                        'reativa': amostra['potencia_reativa'] - amostra_anterior.get('potencia_reativa', 0)
                    })
                    
                    if candidatos:
                        equipamento, confianca, _ = candidatos[0]
                        resultados.append({
                            'evento': 'ligou',
                            'equipamento': equipamento,
                            'potencia': delta,
                            'confianca': confianca,
                            'timestamp': datetime.now().strftime("%H:%M:%S")
                        })
                    else:
                        resultados.append({
                            'evento': 'ligou',
                            'equipamento': 'desconhecido',
                            'potencia': delta,
                            'confianca': 0,
                            'timestamp': datetime.now().strftime("%H:%M:%S")
                        })
                
                # Se desligou (delta negativo)
                elif delta < -20:
                    resultados.append({
                        'evento': 'desligou',
                        'equipamento': 'alguém',
                        'potencia': abs(delta),
                        'confianca': 0,
                        'timestamp': datetime.now().strftime("%H:%M:%S")
                    })
        
        # Identificar equipamento contínuo (se potencia estável > 0)
        if features['potencia'] > 30:
            candidatos = self.identificar_por_assinatura(features)
            if candidatos:
                equipamento, confianca, _ = candidatos[0]
                resultados.append({
                    'evento': 'funcionando',
                    'equipamento': equipamento,
                    'potencia': features['potencia'],
                    'confianca': confianca,
                    'timestamp': datetime.now().strftime("%H:%M:%S")
                })
        
        return resultados
    
    def salvar_dataset(self):
        """
        Salva o dataset de assinaturas em arquivo
        """
        try:
            os.makedirs('models', exist_ok=True)
            with open('models/assinaturas.json', 'w') as f:
                json.dump(self.assinaturas_conhecidas, f, indent=2)
            print("💾 Dataset salvo em models/assinaturas.json")
        except Exception as e:
            print(f"❌ Erro ao salvar dataset: {e}")
    
    def carregar_modelo(self):
        """
        Tenta carregar modelo treinado
        """
        try:
            if os.path.exists('models/assinaturas.json'):
                with open('models/assinaturas.json', 'r') as f:
                    self.assinaturas_conhecidas.update(json.load(f))
                print(f"📚 Dataset carregado com {len(self.assinaturas_conhecidas)} equipamentos")
        except Exception as e:
            print(f"⚠️ Não foi possível carregar dataset: {e}")