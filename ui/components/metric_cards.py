# Componente de cards de métricas
import customtkinter as ctk
from config.settings import CORES
from utils.helpers import obter_status_fp

class MetricCardsComponent:
    """Componente que gerencia os cards de métricas do dashboard"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.cores = CORES
        self.cards = {}
        
        self.criar_container()
    
    def criar_container(self):
        """Cria o container para os cards"""
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
    
    def atualizar_cards(self, dados, tensao_referencia):
        """Atualiza todos os cards com novos dados"""
        # Limpar cards existentes
        for widget in self.frame.winfo_children():
            widget.destroy()
        
        # Obter status do FP
        status_fp, cor_fp = obter_status_fp(dados['fator_potencia'])
        
        # Definir métricas
        metricas = [
            {
                "titulo": "TENSÃO CALIBRADA",
                "valor": f"{dados['tensao']:.1f}V",
                "trend": f"Ref: {tensao_referencia:.1f}V" if tensao_referencia > 0 else "Calibre!",
                "cor": self.cores["primaria"],
                "icone": "⚡"
            },
            {
                "titulo": "FATOR DE POTÊNCIA",
                "valor": f"{dados['fator_potencia']:.3f}",
                "trend": status_fp,
                "cor": cor_fp,
                "icone": "Φ"
            },
            {
                "titulo": "POTÊNCIA ATIVA",
                "valor": f"{dados['potencia_ativa']:.1f}W",
                "trend": f"P = V×I×cosφ",
                "cor": self.cores["sucesso"],
                "icone": "🔋"
            },
            {
                "titulo": "POTÊNCIA REATIVA",
                "valor": f"{dados['potencia_reativa']:.1f}VAR",
                "trend": f"Q = V×I×sinφ",
                "cor": self.cores["secundaria"],
                "icone": "🌀"
            }
        ]
        
        # Criar cards
        for i, metrica in enumerate(metricas):
            card = self.criar_card(metrica)
            card.grid(row=0, column=i, padx=10, sticky="nsew")
            self.frame.columnconfigure(i, weight=1)
            
            # Guardar referência
            self.cards[metrica["titulo"]] = card
    
    def criar_card(self, metrica):
        """Cria um card individual"""
        card = ctk.CTkFrame(self.frame, 
                           fg_color=self.cores["card"],
                           corner_radius=12,
                           height=120)
        
        inner_frame = ctk.CTkFrame(card, fg_color="transparent")
        inner_frame.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Header do card
        header_card = ctk.CTkFrame(inner_frame, fg_color="transparent")
        header_card.pack(fill="x")
        
        # Ícone
        icone = ctk.CTkLabel(header_card,
                            text=metrica["icone"],
                            font=("Arial", 16))
        icone.pack(side="left")
        
        # Título
        titulo = ctk.CTkLabel(header_card,
                             text=metrica["titulo"],
                             font=("Arial", 12),
                             text_color="#8899aa")
        titulo.pack(side="left", padx=(10, 0))
        
        # Valor principal
        valor = ctk.CTkLabel(inner_frame,
                            text=metrica["valor"],
                            font=("Arial", 24, "bold"),
                            text_color=metrica["cor"])
        valor.pack(anchor="w", pady=(10, 5))
        
        # Tendência/info
        trend = ctk.CTkLabel(inner_frame,
                            text=metrica["trend"],
                            font=("Arial", 11),
                            text_color=metrica["cor"])
        trend.pack(anchor="w")
        
        return card
    
    def pack(self, **kwargs):
        """Empacota o frame principal"""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Esconde o frame"""
        self.frame.pack_forget()