# Componente de tabela de dados
import customtkinter as ctk
from tkinter import ttk
import math
from config.settings import CORES
from utils.helpers import obter_status_fp, calcular_angulo_fase

class DataTableComponent:
    """Componente que gerencia a tabela de dados em tempo real"""
    
    def __init__(self, parent):
        self.parent = parent
        self.frame = None
        self.tabela = None
        self.label_referencia = None
        self.cores = CORES
        
        self.criar_tabela()
    
    def criar_tabela(self):
        """Cria a tabela de dados"""
        self.frame = ctk.CTkFrame(self.parent, fg_color=self.cores["card"], corner_radius=12)
        
        # Header da tabela
        header_tabela = ctk.CTkFrame(self.frame, fg_color="transparent")
        header_tabela.pack(fill="x", padx=20, pady=15)
        
        titulo_tabela = ctk.CTkLabel(header_tabela,
                                    text="ANÁLISE MONOFÁSICA EM TEMPO REAL",
                                    font=("Arial", 16, "bold"))
        titulo_tabela.pack(side="left")
        
        # Label de referência
        self.label_referencia = ctk.CTkLabel(header_tabela,
                                           text="Ref: 127.0V",
                                           font=("Arial", 10),
                                           text_color="#ffaa00")
        self.label_referencia.pack(side="right", padx=(0, 10))
        
        # Frame para a tabela
        tabela_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        tabela_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Configurar estilo da tabela
        self.configurar_estilo()
        
        # Criar tabela
        colunas = ('Parâmetro', 'Valor', 'Unidade', 'Status')
        self.tabela = ttk.Treeview(tabela_frame, columns=colunas, show='headings', 
                                  style="Premium.Treeview", height=8)
        
        # Configurar colunas
        col_widths = [250, 150, 100, 150]
        for col, width in zip(colunas, col_widths):
            self.tabela.heading(col, text=col)
            self.tabela.column(col, width=width, anchor='center')
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tabela_frame, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scrollbar.set)
        
        # Posicionar
        self.tabela.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def configurar_estilo(self):
        """Configura o estilo da tabela"""
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Premium.Treeview",
                       background=self.cores["card"],
                       foreground=self.cores["texto"],
                       fieldbackground=self.cores["card"],
                       rowheight=35,
                       font=('Arial', 11))
        style.configure("Premium.Treeview.Heading",
                       background="#2a3b4c",
                       foreground=self.cores["texto"],
                       font=('Arial', 12, 'bold'))
    
    def atualizar(self, dados, modo_simulacao, serial_conectada, tensao_referencia):
        """Atualiza a tabela com novos dados"""
        # Limpar tabela
        for item in self.tabela.get_children():
            self.tabela.delete(item)
        
        # Atualizar label de referência
        self.label_referencia.configure(text=f"Ref: {tensao_referencia:.1f}V")
        
        # Determinar status geral
        if modo_simulacao:
            status_geral = "Simulação"
        elif serial_conectada and dados['tensao'] > 0:
            status_geral = "Real - Ativo"
        elif serial_conectada:
            status_geral = "Real - Aguardando"
        else:
            status_geral = "Real - Desconectado"
        
        # Obter status do FP
        status_fp, cor_fp = obter_status_fp(dados['fator_potencia'])
        angulo_fase = calcular_angulo_fase(dados['fator_potencia'])
        
        # Parâmetros para exibir
        parametros = [
            ('Modo Operação', 'Simulação' if modo_simulacao else 'Real', '', status_geral),
            ('Tensão (V)', f"{dados['tensao']:.1f}", 'V', f"Ref: {tensao_referencia:.1f}V"),
            ('Corrente (I)', f"{dados['corrente']:.3f}", 'A', f"I = P/V"),
            ('Potência Ativa (P)', f"{dados['potencia_ativa']:.1f}", 'W', f"P = V×I×cosφ"),
            ('Potência Aparente (S)', f"{dados['potencia_aparente']:.1f}", 'VA', f"S = V×I"),
            ('Potência Reativa (Q)', f"{dados['potencia_reativa']:.1f}", 'VAR', f"Q = V×I×sinφ"),
            ('Fator de Potência (FP)', f"{dados['fator_potencia']:.3f}", '', f"{status_fp} (φ={angulo_fase:.1f}°)"),
            ('Temperatura', f"{dados['temperatura']:.1f}", '°C', 'Normal' if dados['temperatura'] < 40 else 'Alta')
        ]
        
        # Inserir na tabela
        for param in parametros:
            item_id = self.tabela.insert('', 'end', values=param)
            
            # Colorir linha do FP
            if 'Fator de Potência' in param[0]:
                self.tabela.tag_configure('fp', foreground=cor_fp)
                self.tabela.item(item_id, tags=('fp',))
    
    def pack(self, **kwargs):
        """Empacota o frame principal"""
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        """Esconde o frame"""
        self.frame.pack_forget()