# Componente de card de análise de potência
import customtkinter as ctk
import math
from config.settings import CORES
from utils.helpers import calcular_angulo_fase

class AnalysisCardComponent:
    """Componente que exibe as fórmulas e análise de potência"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.cores = CORES
        
        self.criar_card()
    
    def criar_card(self):
        """Cria o card de análise"""
        self.frame = ctk.CTkFrame(self.parent, fg_color=self.cores["card"], corner_radius=12)
        
        # Header
        header = ctk.CTkFrame(self.frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)
        
        self.titulo = ctk.CTkLabel(header,
                                   text="📊 ANÁLISE DE POTÊNCIA",
                                   font=("Arial", 16, "bold"))
        self.titulo.pack(side="left")
        
        # Conteúdo
        self.content = ctk.CTkFrame(self.frame, fg_color="transparent")
        self.content.pack(fill="x", padx=20, pady=(0, 20))
    
    def atualizar(self, dados, modo_simulacao):
        """Atualiza o card com novos dados"""
        # Limpar conteúdo
        for widget in self.content.winfo_children():
            widget.destroy()
        
        # Atualizar título com modo
        modo_texto = "SIMULAÇÃO" if modo_simulacao else "REAL"
        cor_modo = self.cores["alerta"] if modo_simulacao else self.cores["sucesso"]
        self.titulo.configure(text=f"📊 ANÁLISE DE POTÊNCIA - MODO {modo_texto}", text_color=cor_modo)
        
        # Calcular ângulo de fase
        angulo_fase = calcular_angulo_fase(dados['fator_potencia'])
        
        # Fórmulas - Linha 1
        linha1 = ctk.CTkFrame(self.content, fg_color="transparent")
        linha1.pack(fill="x", pady=2)
        
        ctk.CTkLabel(linha1, text="P = ", font=("Arial", 12), text_color="#8899aa").pack(side="left")
        ctk.CTkLabel(linha1, text=f"V×I×cosφ", font=("Arial", 12, "bold"), 
                    text_color=self.cores["sucesso"]).pack(side="left")
        ctk.CTkLabel(linha1, text=" = ", font=("Arial", 12), text_color="#8899aa").pack(side="left")
        ctk.CTkLabel(linha1, text=f"{dados['potencia_ativa']:.2f}W", 
                    font=("Arial", 12, "bold"), text_color=self.cores["sucesso"]).pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(linha1, text="S = ", font=("Arial", 12), text_color="#8899aa").pack(side="left")
        ctk.CTkLabel(linha1, text=f"V×I", font=("Arial", 12, "bold"), 
                    text_color=self.cores["primaria"]).pack(side="left")
        ctk.CTkLabel(linha1, text=" = ", font=("Arial", 12), text_color="#8899aa").pack(side="left")
        ctk.CTkLabel(linha1, text=f"{dados['potencia_aparente']:.2f}VA", 
                    font=("Arial", 12, "bold"), text_color=self.cores["primaria"]).pack(side="left", padx=(0, 20))
        
        # Fórmulas - Linha 2
        linha2 = ctk.CTkFrame(self.content, fg_color="transparent")
        linha2.pack(fill="x", pady=5)
        
        ctk.CTkLabel(linha2, text="Q = ", font=("Arial", 12), text_color="#8899aa").pack(side="left")
        ctk.CTkLabel(linha2, text=f"V×I×sinφ", font=("Arial", 12, "bold"), 
                    text_color=self.cores["secundaria"]).pack(side="left")
        ctk.CTkLabel(linha2, text=" = ", font=("Arial", 12), text_color="#8899aa").pack(side="left")
        ctk.CTkLabel(linha2, text=f"{dados['potencia_reativa']:.2f}VAR", 
                    font=("Arial", 12, "bold"), text_color=self.cores["secundaria"]).pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(linha2, text="FP = cosφ = ", font=("Arial", 12), text_color="#8899aa").pack(side="left")
        cor_fp = self.cores["sucesso"] if dados['fator_potencia'] > 0.95 else self.cores["alerta"]
        ctk.CTkLabel(linha2, text=f"{dados['fator_potencia']:.3f}", 
                    font=("Arial", 12, "bold"), text_color=cor_fp).pack(side="left")
        ctk.CTkLabel(linha2, text=f" (φ = {angulo_fase:.1f}°)", 
                    font=("Arial", 10), text_color="#8899aa").pack(side="left")
        
        # Valores atuais - Linha 3
        linha3 = ctk.CTkFrame(self.content, fg_color="transparent")
        linha3.pack(fill="x", pady=10)
        
        ctk.CTkLabel(linha3, text="⚡ ", font=("Arial", 14), 
                    text_color=self.cores["primaria"]).pack(side="left")
        ctk.CTkLabel(linha3, text=f"V = {dados['tensao']:.1f}V", 
                    font=("Arial", 14, "bold"), text_color=self.cores["primaria"]).pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(linha3, text="🔌 ", font=("Arial", 14), 
                    text_color=self.cores["secundaria"]).pack(side="left")
        ctk.CTkLabel(linha3, text=f"I = {dados['corrente']:.3f}A", 
                    font=("Arial", 14, "bold"), text_color=self.cores["secundaria"]).pack(side="left", padx=(0, 20))
        
        ctk.CTkLabel(linha3, text="📊 ", font=("Arial", 14), 
                    text_color=self.cores["sucesso"]).pack(side="left")
        ctk.CTkLabel(linha3, text=f"P = {dados['potencia_ativa']:.1f}W", 
                    font=("Arial", 14, "bold"), text_color=self.cores["sucesso"]).pack(side="left")
    
    def pack(self, **kwargs):
        """Empacota o frame principal"""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Esconde o frame"""
        self.frame.pack_forget()