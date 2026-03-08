# Janela principal da aplicação
from ai.nilm_detector import NILMDetector
from ui.dialogs.training_dialog import TrainingDialog
import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
import threading
import time

from config.settings import CORES, TENSAO_PADRAO, INTERVALO_ATUALIZACAO
from config.gemini_config import configurar_gemini
from core.data_manager import DataManager
from core.serial_manager import SerialManager
from core.simulation import SimulationManager
from ui.dialogs.calibration_dialog import CalibrationDialog
from ui.dialogs.gemini_chat_dialog import GeminiChatDialog
from ui.components.sidebar import SidebarComponent
from ui.components.metric_cards import MetricCardsComponent
from ui.components.data_table import DataTableComponent
from ui.components.analysis_card import AnalysisCardComponent

class PowerGridAI:
    """Classe principal da aplicação PowerGrid AI"""
    
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("PowerGrid AI - Analisador Inteligente de Rede MONOFÁSICO")
        self.root.geometry("1400x900")
        
        # Inicializar gerenciadores
        self.data_manager = DataManager(TENSAO_PADRAO)
        self.serial_manager = SerialManager()
        self.simulation_manager = SimulationManager(TENSAO_PADRAO)
        self.nilm_detector = NILMDetector()
        
        # Variáveis de controle
        self.monitorando = False
        self.contador_tempo = 0
        self.aba_atual = "dashboard"
        self.modo_simulacao = True
        self.calibrando = False
        self.tensao_sensor_bruta = 0
        self.debug_counter = 0
        self.amostra_anterior = None
        
        # Testar conexão Gemini
        self.model, self.gemini_disponivel = configurar_gemini()
        self.exibir_status_inicial()
        
        # Referências para componentes
        self.sidebar = None
        self.metric_cards = None
        self.data_table = None
        self.analysis_card = None
        self.timestamp_label = None
        self.btn_monitoramento = None
        
        # Frames para cada aba
        self.frame_dashboard = None
        self.frame_analise = None
        self.frame_tendencias = None
        self.frame_configuracoes = None
        self.frame_ia = None
        
        # Referências para gráficos
        self.fig_tensao = None
        self.ax_tensao = None
        self.canvas_tensao = None
        self.fig_corrente = None
        self.ax_corrente = None
        self.canvas_corrente = None
        self.fig_potencia = None
        self.ax_potencia = None
        self.canvas_potencia = None
        self.label_faixa_tensao = None
        
        self.criar_interface()
    
    def exibir_status_inicial(self):
        """Exibe status inicial no console"""
        print("=" * 80)
        print("⚡ POWERGRID AI - SISTEMA MONOFÁSICO")
        print(f"🤖 Gemini: {'CONECTADO' if self.gemini_disponivel else 'SIMULAÇÃO'}")
        print("=" * 80)
    
    def criar_interface(self):
        """Cria a interface principal"""
        # Frame principal
        main_frame = ctk.CTkFrame(self.root, fg_color=CORES["fundo"])
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Criar sidebar com callbacks
        callbacks = {
            'mostrar_dashboard': self.mostrar_dashboard,
            'mostrar_analise': self.mostrar_analise,
            'mostrar_tendencias': self.mostrar_tendencias,
            'mostrar_configuracoes': self.mostrar_configuracoes,
            'mostrar_assistente_ia': self.mostrar_assistente_ia,
            'toggle_conexao_serial': self.toggle_conexao_serial,
            'toggle_modo_simulacao': self.toggle_modo_simulacao,
            'abrir_chat_gemini': self.abrir_chat_gemini,
            'abrir_treinamento_nilm': self.abrir_treinamento_nilm,
            'listar_portas': self.serial_manager.listar_portas
        }
        
        self.sidebar = SidebarComponent(main_frame, callbacks)
        
        # Área de conteúdo
        self.area_conteudo = ctk.CTkFrame(main_frame, fg_color="transparent")
        self.area_conteudo.pack(side="right", fill="both", expand=True, padx=(20, 0))
        
        # Criar todas as abas
        self.criar_todas_abas()
        
        # Mostrar dashboard inicial
        self.mostrar_dashboard()
    
    def toggle_conexao_serial(self):
        """Alterna conexão serial (conecta/desconecta)"""
        if not self.serial_manager.conectada:
            # Tenta conectar
            porta_selecionada = self.sidebar.get_porta_selecionada()
            if porta_selecionada and porta_selecionada != "Selecionar Porta":
                sucesso, mensagem = self.serial_manager.conectar(porta_selecionada)
                
                if sucesso:
                    print(f"✅ {mensagem}")
                    # Iniciar calibração em thread separada
                    self.calibrando = True
                    threading.Thread(target=self.processar_calibracao, daemon=True).start()
                    
                    # Mudar para modo real se estiver em simulação
                    if self.modo_simulacao:
                        self.toggle_modo_simulacao()
                else:
                    print(f"❌ {mensagem}")
                    messagebox.showerror("Erro de Conexão", mensagem)
            else:
                messagebox.showwarning("Aviso", "Selecione uma porta serial primeiro!")
        else:
            # Desconecta
            self.serial_manager.desconectar()
            self.calibrando = False
            print("🔌 Desconectado da porta serial")
        
        # Atualizar status na sidebar
        if hasattr(self, 'sidebar') and self.sidebar:
            self.sidebar.atualizar_status(
                self.modo_simulacao,
                self.serial_manager.conectada,
                self.gemini_disponivel,
                self.monitorando,
                self.contador_tempo
            )
    
    def toggle_modo_simulacao(self):
        """Alterna entre modo simulação e modo real"""
        self.modo_simulacao = not self.modo_simulacao
        
        # Atualizar status na sidebar
        if hasattr(self, 'sidebar') and self.sidebar:
            self.sidebar.atualizar_status(
                self.modo_simulacao,
                self.serial_manager.conectada,
                self.gemini_disponivel,
                self.monitorando,
                self.contador_tempo
            )
        
        # Mostrar no console
        modo = "SIMULAÇÃO" if self.modo_simulacao else "REAL"
        print(f"🎮 Modo alterado para: {modo}")
        
        # Se mudou para modo real mas não há conexão serial, avisar
        if not self.modo_simulacao and not self.serial_manager.conectada:
            print("⚠️ Modo REAL ativado mas sem conexão serial. Conecte o Arduino!")
    
    def abrir_treinamento_nilm(self):
        """Abre diálogo de treinamento NILM"""
        dialog = TrainingDialog(self.root, self.nilm_detector)
        dialog.focus()
    
    def abrir_chat_gemini(self):
        """Abre a janela de chat com Gemini"""
        try:
            chat_window = GeminiChatDialog(
                self.root, 
                self.data_manager.dados, 
                self.data_manager.tensao_referencia
            )
            chat_window.focus()
        except Exception as e:
            print(f"❌ Erro ao abrir chat Gemini: {e}")
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erro", f"Não foi possível abrir o chat:\n{str(e)[:100]}")
    
    def criar_todas_abas(self):
        """Cria todas as abas da aplicação"""
        # Dashboard
        self.frame_dashboard = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        self.criar_conteudo_dashboard()
        
        # Análise
        self.frame_analise = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        self.criar_conteudo_analise()
        
        # Tendências
        self.frame_tendencias = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        self.criar_conteudo_tendencias()
        
        # Configurações
        self.frame_configuracoes = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        self.criar_conteudo_configuracoes()
        
        # IA (será criada sob demanda)
        self.frame_ia = None
    
    def criar_conteudo_dashboard(self):
        """Cria o conteúdo da aba Dashboard"""
        # Header
        header = ctk.CTkFrame(self.frame_dashboard, fg_color="transparent", height=80)
        header.pack(fill="x", pady=(0, 20))
        
        titulo = ctk.CTkLabel(header,
                             text="Dashboard em Tempo Real - SISTEMA MONOFÁSICO",
                             font=("Arial", 24, "bold"),
                             text_color=CORES["texto"])
        titulo.pack(side="left")
        
        # Timestamp
        self.timestamp_label = ctk.CTkLabel(header,
                                          text=datetime.now().strftime("%H:%M:%S"),
                                          font=("Arial", 14),
                                          text_color=CORES["primaria"])
        self.timestamp_label.pack(side="right")
        
        # Controles
        controles_header = ctk.CTkFrame(header, fg_color="transparent")
        controles_header.pack(side="right", padx=(0, 20))
        
        self.btn_monitoramento = ctk.CTkButton(controles_header,
                                             text="▶ INICIAR MONITORAMENTO",
                                             command=self.toggle_monitoramento,
                                             fg_color=CORES["sucesso"],
                                             hover_color="#00cc77",
                                             font=("Arial", 12, "bold"),
                                             width=200,
                                             height=40)
        self.btn_monitoramento.pack(side="left", padx=(0, 10))
        
        # Cards de métricas
        self.metric_cards = MetricCardsComponent(self.frame_dashboard)
        self.metric_cards.pack(fill="x", pady=(0, 20))
        
        # Tabela de dados
        self.data_table = DataTableComponent(self.frame_dashboard)
        self.data_table.pack(fill="both", expand=True, pady=(0, 20))
        
        # Card de análise
        self.analysis_card = AnalysisCardComponent(self.frame_dashboard)
        self.analysis_card.pack(fill="x", pady=(0, 10))
    
    def criar_conteudo_analise(self):
        """Cria o conteúdo da aba Análise com gráficos"""
        from matplotlib.figure import Figure
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
        
        titulo = ctk.CTkLabel(self.frame_analise,
                             text="Análise Detalhada - Gráficos em Tempo Real (MONOFÁSICO)",
                             font=("Arial", 24, "bold"),
                             text_color=CORES["texto"])
        titulo.pack(pady=(0, 20))
        
        # Frame para gráficos
        frame_graficos = ctk.CTkFrame(self.frame_analise, fg_color="transparent")
        frame_graficos.pack(fill="both", expand=True)
        
        # Gráfico de Tensão
        frame_tensao = ctk.CTkFrame(frame_graficos, fg_color=CORES["card"], corner_radius=12)
        frame_tensao.pack(fill="both", expand=True, pady=(0, 10))
        
        header_tensao = ctk.CTkFrame(frame_tensao, fg_color="transparent")
        header_tensao.pack(fill="x", padx=20, pady=15)
        
        titulo_tensao = ctk.CTkLabel(header_tensao,
                                    text="TENSÃO - TEMPO REAL",
                                    font=("Arial", 16, "bold"),
                                    text_color=CORES["primaria"])
        titulo_tensao.pack(side="left")
        
        # Label da faixa
        self.label_faixa_tensao = ctk.CTkLabel(header_tensao,
                                             text=f"Faixa: {self.data_manager.faixa_tensao_min:.0f}-{self.data_manager.faixa_tensao_max:.0f}V",
                                             font=("Arial", 10),
                                             text_color="#ffaa00")
        self.label_faixa_tensao.pack(side="right")
        
        # Criar gráfico de tensão
        self.fig_tensao = Figure(figsize=(10, 3), facecolor=CORES["card"])
        self.ax_tensao = self.fig_tensao.add_subplot(111)
        self.ax_tensao.set_facecolor(CORES["card"])
        self.configurar_estilo_grafico(self.ax_tensao, "Tensão (V)", 
                                      self.data_manager.faixa_tensao_min, 
                                      self.data_manager.faixa_tensao_max)
        
        self.canvas_tensao = FigureCanvasTkAgg(self.fig_tensao, frame_tensao)
        self.canvas_tensao.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Gráfico de Corrente
        frame_corrente = ctk.CTkFrame(frame_graficos, fg_color=CORES["card"], corner_radius=12)
        frame_corrente.pack(fill="both", expand=True, pady=10)
        
        header_corrente = ctk.CTkFrame(frame_corrente, fg_color="transparent")
        header_corrente.pack(fill="x", padx=20, pady=15)
        
        titulo_corrente = ctk.CTkLabel(header_corrente,
                                      text="CORRENTE - TEMPO REAL",
                                      font=("Arial", 16, "bold"),
                                      text_color=CORES["secundaria"])
        titulo_corrente.pack(side="left")
        
        # Criar gráfico de corrente
        self.fig_corrente = Figure(figsize=(10, 3), facecolor=CORES["card"])
        self.ax_corrente = self.fig_corrente.add_subplot(111)
        self.ax_corrente.set_facecolor(CORES["card"])
        self.configurar_estilo_grafico(self.ax_corrente, "Corrente (A)", 0, 2.0)
        
        self.canvas_corrente = FigureCanvasTkAgg(self.fig_corrente, frame_corrente)
        self.canvas_corrente.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Gráfico de Potência
        frame_potencia = ctk.CTkFrame(frame_graficos, fg_color=CORES["card"], corner_radius=12)
        frame_potencia.pack(fill="both", expand=True, pady=10)
        
        header_potencia = ctk.CTkFrame(frame_potencia, fg_color="transparent")
        header_potencia.pack(fill="x", padx=20, pady=15)
        
        titulo_potencia = ctk.CTkLabel(header_potencia,
                                      text="POTÊNCIA - TEMPO REAL",
                                      font=("Arial", 16, "bold"),
                                      text_color=CORES["sucesso"])
        titulo_potencia.pack(side="left")
        
        # Criar gráfico de potência
        self.fig_potencia = Figure(figsize=(10, 3), facecolor=CORES["card"])
        self.ax_potencia = self.fig_potencia.add_subplot(111)
        self.ax_potencia.set_facecolor(CORES["card"])
        self.configurar_estilo_grafico(self.ax_potencia, "Potência (W)", 0, 300)
        
        self.canvas_potencia = FigureCanvasTkAgg(self.fig_potencia, frame_potencia)
        self.canvas_potencia.get_tk_widget().pack(fill="both", expand=True, padx=20, pady=(0, 20))
    
    def criar_conteudo_tendencias(self):
        """Cria o conteúdo da aba Tendências"""
        titulo = ctk.CTkLabel(self.frame_tendencias,
                             text="Análise de Tendências - Sistema Monofásico",
                             font=("Arial", 24, "bold"),
                             text_color=CORES["texto"])
        titulo.pack(pady=100)
        
        label = ctk.CTkLabel(self.frame_tendencias,
                           text="🔧 Em Desenvolvimento",
                           font=("Arial", 16),
                           text_color=CORES["alerta"])
        label.pack()
    
    def criar_conteudo_configuracoes(self):
        """Cria o conteúdo da aba Configurações"""
        titulo = ctk.CTkLabel(self.frame_configuracoes,
                             text="Configurações do Sistema Monofásico",
                             font=("Arial", 24, "bold"),
                             text_color=CORES["texto"])
        titulo.pack(pady=100)
        
        label = ctk.CTkLabel(self.frame_configuracoes,
                           text="🔧 Em Desenvolvimento",
                           font=("Arial", 16),
                           text_color=CORES["alerta"])
        label.pack()
    
    def criar_conteudo_ia(self):
        """Cria o conteúdo da aba Assistente IA"""
        self.frame_ia = ctk.CTkFrame(self.area_conteudo, fg_color="transparent")
        
        # Header
        header = ctk.CTkFrame(self.frame_ia, fg_color="transparent")
        header.pack(fill="x", pady=(0, 20))
        
        titulo = ctk.CTkLabel(header,
                             text="🤖 ASSISTENTE IA - GEMINI POWERGRID",
                             font=("Arial", 24, "bold"),
                             text_color="#9d4edd")
        titulo.pack(side="left")
        
        # Conteúdo principal
        main_content = ctk.CTkFrame(self.frame_ia, fg_color="transparent")
        main_content.pack(fill="both", expand=True)
        
        # Cards de funcionalidades
        self.criar_cards_ia(main_content)
        
        # Frame para dados atuais
        self.criar_dados_ia(main_content)
    
    def criar_cards_ia(self, parent):
        """Cria cards de funcionalidades da IA"""
        cards_frame = ctk.CTkFrame(parent, fg_color="transparent")
        cards_frame.pack(fill="x", pady=(0, 20))
        
        funcionalidades = [
            {
                "titulo": "💬 Chat Inteligente",
                "descricao": "Converse com o Gemini sobre consumo elétrico",
                "cor": "#00d4ff",
                "comando": self.abrir_chat_gemini
            },
            {
                "titulo": "📊 Análise de Dados",
                "descricao": "Análise automática dos dados coletados",
                "cor": "#ff6b35",
                "comando": self.analisar_dados_ia
            },
            {
                "titulo": "💡 Sugestões de Economia",
                "descricao": "Receba dicas personalizadas",
                "cor": "#00ff88",
                "comando": self.sugestoes_economia
            },
            {
                "titulo": "⚡ Cálculos Elétricos",
                "descricao": "Realize cálculos avançados",
                "cor": "#ffaa00",
                "comando": self.calculos_eletricos
            }
        ]
        
        for i, func in enumerate(funcionalidades):
            card = ctk.CTkFrame(cards_frame, 
                               fg_color=CORES["card"],
                               corner_radius=12,
                               height=150)
            card.grid(row=0, column=i, padx=10, sticky="nsew")
            cards_frame.columnconfigure(i, weight=1)
            
            inner_frame = ctk.CTkFrame(card, fg_color="transparent")
            inner_frame.pack(fill="both", expand=True, padx=20, pady=20)
            
            # Título
            ctk.CTkLabel(inner_frame,
                        text=func["titulo"],
                        font=("Arial", 16, "bold"),
                        text_color=func["cor"]).pack(anchor="w", pady=(0, 10))
            
            # Descrição
            ctk.CTkLabel(inner_frame,
                        text=func["descricao"],
                        font=("Arial", 12),
                        text_color="#8899aa",
                        wraplength=200).pack(anchor="w", pady=(0, 15))
            
            # Botão
            ctk.CTkButton(inner_frame,
                         text="Acessar →",
                         command=func["comando"],
                         fg_color=func["cor"],
                         hover_color=self.escurecer_cor(func["cor"]),
                         width=100).pack(anchor="w")
    
    def criar_dados_ia(self, parent):
        """Cria frame com dados atuais para IA"""
        dados_frame = ctk.CTkFrame(parent, fg_color=CORES["card"], corner_radius=12)
        dados_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(dados_frame,
                    text="📊 DADOS ATUAIS PARA ANÁLISE",
                    font=("Arial", 16, "bold"),
                    text_color="#ffaa00").pack(pady=15)
        
        # Grid de dados
        dados_grid = ctk.CTkFrame(dados_frame, fg_color="transparent")
        dados_grid.pack(padx=20, pady=(0, 20))
        
        parametros = [
            ("Tensão", f"{self.data_manager.dados['tensao']:.1f} V", "#00d4ff"),
            ("Corrente", f"{self.data_manager.dados['corrente']:.3f} A", "#ff6b35"),
            ("Potência Ativa", f"{self.data_manager.dados['potencia_ativa']:.1f} W", "#00ff88"),
            ("Fator Potência", f"{self.data_manager.dados['fator_potencia']:.3f}", "#ffaa00"),
            ("Potência Aparente", f"{self.data_manager.dados['potencia_aparente']:.1f} VA", "#9d4edd"),
            ("Potência Reativa", f"{self.data_manager.dados['potencia_reativa']:.1f} VAR", "#ff5555")
        ]
        
        for i in range(0, len(parametros), 3):
            row_frame = ctk.CTkFrame(dados_grid, fg_color="transparent")
            row_frame.pack(fill="x", pady=5)
            
            for j in range(3):
                if i + j < len(parametros):
                    nome, valor, cor = parametros[i + j]
                    
                    param_frame = ctk.CTkFrame(row_frame, fg_color="transparent")
                    param_frame.pack(side="left", fill="x", expand=True, padx=10)
                    
                    ctk.CTkLabel(param_frame,
                               text=nome,
                               font=("Arial", 12),
                               text_color="#8899aa").pack(anchor="w")
                    
                    ctk.CTkLabel(param_frame,
                               text=valor,
                               font=("Arial", 14, "bold"),
                               text_color=cor).pack(anchor="w", pady=(2, 0))
    
    def configurar_estilo_grafico(self, ax, titulo_y, ymin, ymax):
        """Configura o estilo dos gráficos"""
        ax.set_xlabel('Tempo (s)', color='white', fontsize=12)
        ax.set_ylabel(titulo_y, color='white', fontsize=12)
        ax.set_ylim(ymin, ymax)
        ax.grid(True, alpha=0.3, color='gray')
        ax.tick_params(colors='white')
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white') 
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
    
    def escurecer_cor(self, cor_hex):
        """Escurece uma cor hexadecimal"""
        cor = cor_hex.lstrip('#')
        r = int(cor[0:2], 16)
        g = int(cor[2:4], 16)
        b = int(cor[4:6], 16)
        
        r = max(0, r - 30)
        g = max(0, g - 30)
        b = max(0, b - 30)
        
        return f'#{r:02x}{g:02x}{b:02x}'
    
    # Métodos de navegação
    def mostrar_dashboard(self):
        """Mostra a aba Dashboard"""
        self.aba_atual = "dashboard"
        self.esconder_todas_abas()
        self.frame_dashboard.pack(fill="both", expand=True)
        self.atualizar_dashboard()
    
    def mostrar_analise(self):
        """Mostra a aba Análise"""
        self.aba_atual = "analise"
        self.esconder_todas_abas()
        self.frame_analise.pack(fill="both", expand=True)
        self.atualizar_graficos()
    
    def mostrar_tendencias(self):
        """Mostra a aba Tendências"""
        self.aba_atual = "tendencias"
        self.esconder_todas_abas()
        self.frame_tendencias.pack(fill="both", expand=True)
    
    def mostrar_configuracoes(self):
        """Mostra a aba Configurações"""
        self.aba_atual = "configuracoes"
        self.esconder_todas_abas()
        self.frame_configuracoes.pack(fill="both", expand=True)
    
    def mostrar_assistente_ia(self):
        """Mostra a aba Assistente IA"""
        self.aba_atual = "ia"
        self.esconder_todas_abas()
        
        if not self.frame_ia:
            self.criar_conteudo_ia()
        
        self.frame_ia.pack(fill="both", expand=True)
    
    def esconder_todas_abas(self):
        """Esconde todas as abas"""
        for frame in [self.frame_dashboard, self.frame_analise, 
                     self.frame_tendencias, self.frame_configuracoes]:
            if frame is not None:
                frame.pack_forget()
        
        if self.frame_ia is not None:
            self.frame_ia.pack_forget()
    
    # Métodos de atualização
    def atualizar_dashboard(self):
        """Atualiza os componentes do dashboard"""
        if hasattr(self, 'data_table') and self.data_table:
            self.data_table.atualizar(
                self.data_manager.dados,
                self.modo_simulacao,
                self.serial_manager.conectada,
                self.data_manager.tensao_referencia
            )
        
        if hasattr(self, 'metric_cards') and self.metric_cards:
            self.metric_cards.atualizar_cards(
                self.data_manager.dados,
                self.data_manager.tensao_referencia
            )
        
        if hasattr(self, 'analysis_card') and self.analysis_card:
            self.analysis_card.atualizar(
                self.data_manager.dados,
                self.modo_simulacao
            )
        
        if hasattr(self, 'timestamp_label'):
            self.timestamp_label.configure(text=datetime.now().strftime("%H:%M:%S"))
        
        # Atualizar sidebar
        if hasattr(self, 'sidebar') and self.sidebar:
            self.sidebar.atualizar_status(
                self.modo_simulacao,
                self.serial_manager.conectada,
                self.gemini_disponivel,
                self.monitorando,
                self.contador_tempo
            )
    
    def atualizar_graficos(self):
        """Atualiza os gráficos na aba análise"""
        if self.aba_atual != "analise":
            return
        
        max_pontos = 50
        
        # Limitar histórico
        if len(self.data_manager.timestamps) > max_pontos:
            self.data_manager.timestamps = self.data_manager.timestamps[-max_pontos:]
            self.data_manager.historico_tensao = self.data_manager.historico_tensao[-max_pontos:]
            self.data_manager.historico_corrente = self.data_manager.historico_corrente[-max_pontos:]
            self.data_manager.historico_potencia = self.data_manager.historico_potencia[-max_pontos:]
        
        # Atualizar gráfico de tensão
        if self.ax_tensao and self.canvas_tensao:
            self.ax_tensao.clear()
            self.configurar_estilo_grafico(self.ax_tensao, "Tensão (V)", 
                                          self.data_manager.faixa_tensao_min, 
                                          self.data_manager.faixa_tensao_max)
            
            if len(self.data_manager.historico_tensao) > 0:
                self.ax_tensao.plot(self.data_manager.timestamps, 
                                   self.data_manager.historico_tensao, 
                                   color=CORES["primaria"], 
                                   linewidth=2, 
                                   label='Tensão')
                
                # Linha de referência
                self.ax_tensao.axhline(y=self.data_manager.tensao_referencia, 
                                      color='#ffaa00', 
                                      linestyle='--', alpha=0.7, linewidth=1,
                                      label=f'Ref: {self.data_manager.tensao_referencia:.1f}V')
            
            modo_texto = "Simulação" if self.modo_simulacao else "Real"
            self.ax_tensao.set_title(f'Tensão em Tempo Real - Modo {modo_texto}', 
                                    color='white', fontsize=14)
            self.ax_tensao.legend(facecolor=CORES["card"], edgecolor='white', labelcolor='white')
            self.canvas_tensao.draw()
        
        # Atualizar gráfico de corrente
        if self.ax_corrente and self.canvas_corrente:
            self.ax_corrente.clear()
            self.configurar_estilo_grafico(self.ax_corrente, "Corrente (A)", 0, 2.0)
            
            if len(self.data_manager.historico_corrente) > 0:
                self.ax_corrente.plot(self.data_manager.timestamps, 
                                     self.data_manager.historico_corrente, 
                                     color=CORES["secundaria"], 
                                     linewidth=2, 
                                     label='Corrente')
            
            self.ax_corrente.set_title(f'Corrente em Tempo Real - Modo {modo_texto}', 
                                      color='white', fontsize=14)
            self.ax_corrente.legend(facecolor=CORES["card"], edgecolor='white', labelcolor='white')
            self.canvas_corrente.draw()
        
        # Atualizar gráfico de potência
        if self.ax_potencia and self.canvas_potencia:
            self.ax_potencia.clear()
            self.configurar_estilo_grafico(self.ax_potencia, "Potência (W)", 0, 300)
            
            if len(self.data_manager.historico_potencia) > 0:
                self.ax_potencia.plot(self.data_manager.timestamps, 
                                     self.data_manager.historico_potencia, 
                                     color=CORES["sucesso"], 
                                     linewidth=2, 
                                     label='Potência Ativa')
            
            self.ax_potencia.set_title(f'Potência Ativa em Tempo Real - Modo {modo_texto}', 
                                      color='white', fontsize=14)
            self.ax_potencia.legend(facecolor=CORES["card"], edgecolor='white', labelcolor='white')
            self.canvas_potencia.draw()
        
        # Atualizar label da faixa
        if hasattr(self, 'label_faixa_tensao') and self.label_faixa_tensao:
            self.label_faixa_tensao.configure(
                text=f"Faixa: {self.data_manager.faixa_tensao_min:.0f}-{self.data_manager.faixa_tensao_max:.0f}V"
            )
    
    # Métodos de controle
    def toggle_monitoramento(self):
        """Alterna o estado de monitoramento"""
        self.monitorando = not self.monitorando
        
        if self.monitorando:
            if self.btn_monitoramento:
                self.btn_monitoramento.configure(text="⏸️ PARAR MONITORAMENTO", 
                                               fg_color=CORES["perigo"])
            self.iniciar_simulacao()
        else:
            if self.btn_monitoramento:
                self.btn_monitoramento.configure(text="▶ INICIAR MONITORAMENTO", 
                                               fg_color=CORES["sucesso"])
    
    def iniciar_simulacao(self):
        """Inicia o loop de simulação/monitoramento"""
        if self.monitorando:
            self.simular_dados()
    
    def simular_dados(self):
        """Loop principal de aquisição de dados OTIMIZADO"""
        if not self.monitorando:
            return
        
        try:
            dados_recebidos = False

            # 1. Aquisição de dados (rápido)
            if not self.modo_simulacao and self.serial_manager.conectada:
                dados = self.serial_manager.ler_dados_medicao()
                if dados:
                    self.data_manager.atualizar_dados(dados['tensao'], dados['corrente'])
                    dados_recebidos = True

            if not dados_recebidos and self.modo_simulacao:
                dados_simulados = self.simulation_manager.gerar_dados()
                self.data_manager.atualizar_dados(dados_simulados['tensao'], dados_simulados['corrente'])
                dados_recebidos = True

            if dados_recebidos:
                self.data_manager.adicionar_ao_historico()

                # 2. Análise NILM (pesada - executar a cada 5 ciclos)
                if self.contador_tempo % 5 == 0:
                    self.processar_nilm()

            # 3. Atualizar INTERFACE apenas quando necessário
            if self.contador_tempo % 2 == 0:
                self.atualizar_interface_otimizado()

            # 4. Atualizar contador
            self.contador_tempo += 1

        except Exception as e:
            print(f"❌ Erro no loop principal: {e}")
            import traceback
            traceback.print_exc()
        
        # 5. Próxima iteração
        if self.monitorando:
            self.root.after(INTERVALO_ATUALIZACAO, self.simular_dados)
    
    def processar_nilm(self):
        """Processa NILM em separado para não travar"""
        try:
            if not self.nilm_detector.modo_treinamento:
                resultados = self.nilm_detector.analisar_amostra(
                    self.data_manager.dados, 
                    self.amostra_anterior
                )
                
                if resultados:
                    for r in resultados:
                        if r['evento'] == 'ligou' and r['equipamento'] != 'desconhecido':
                            print(f"🔌 {r['equipamento']} ligou - {r['potencia']:.0f}W")
                        
                self.amostra_anterior = self.data_manager.dados.copy()
        except Exception as e:
            print(f"⚠️ Erro no NILM: {e}")
    
    def atualizar_interface_otimizado(self):
        """Atualiza interface de forma otimizada"""
        try:
            if self.aba_atual == "dashboard":
                self.atualizar_dashboard_rapido()
            elif self.aba_atual == "analise":
                if self.contador_tempo % 10 == 0:
                    self.atualizar_graficos()
        except Exception as e:
            print(f"⚠️ Erro na interface: {e}")
    
    def atualizar_dashboard_rapido(self):
        """Versão leve de atualização do dashboard"""
        try:
            # Atualizar apenas labels de timestamp
            if hasattr(self, 'timestamp_label'):
                self.timestamp_label.configure(text=datetime.now().strftime("%H:%M:%S"))
            
            # Atualizar tabela (pode ser pesado - fazer a cada 3 ciclos)
            if self.contador_tempo % 3 == 0 and hasattr(self, 'data_table'):
                self.data_table.atualizar(
                    self.data_manager.dados,
                    self.modo_simulacao,
                    self.serial_manager.conectada,
                    self.data_manager.tensao_referencia
                )
            
            # Atualizar cards (leve)
            if hasattr(self, 'metric_cards'):
                self.metric_cards.atualizar_cards(
                    self.data_manager.dados,
                    self.data_manager.tensao_referencia
                )
            
            # Atualizar sidebar (leve)
            if hasattr(self, 'sidebar'):
                self.sidebar.atualizar_status(
                    self.modo_simulacao,
                    self.serial_manager.conectada,
                    self.gemini_disponivel,
                    self.monitorando,
                    self.contador_tempo
                )
        except Exception as e:
            print(f"⚠️ Erro no dashboard rápido: {e}")
    
    def processar_calibracao(self):
        """Processa a calibração do Arduino"""
        if not self.serial_manager.conectada:
            return
        
        print("⚡ Iniciando processo de calibração...")
        
        try:
            # Ler mensagens do Arduino durante 15 segundos
            inicio = time.time()
            while time.time() - inicio < 15 and self.calibrando and self.serial_manager.conectada:
                linha = self.serial_manager.ler_linha()
                
                if linha:
                    print(f"📥 ARDUINO: {linha}")
                    
                    # Processar mensagens específicas
                    if linha.startswith("TENSAO_SENSOR_BRUTA:"):
                        try:
                            self.tensao_sensor_bruta = float(linha.split(":")[1])
                        except:
                            pass
                    
                    elif linha == "SOLICITAR_CALIBRACAO":
                        print("🎯 Arduino solicitando calibração")
                        self.root.after(0, self.mostrar_dialogo_calibracao)
                        return
                    
                    elif "CALIBRACAO_CONCLUIDA" in linha:
                        print("✅ Calibração concluída")
                        self.calibrando = False
                        return
                
                time.sleep(0.1)
            
            print("⏰ Timeout na calibração")
            self.calibrando = False
                
        except Exception as e:
            print(f"❌ Erro na calibração: {e}")
            self.calibrando = False
    
    def mostrar_dialogo_calibracao(self):
        """Mostra diálogo de calibração"""
        dialog = CalibrationDialog(self.root, self.tensao_sensor_bruta)
        self.root.wait_window(dialog)
        
        if dialog.resultado:
            print(f"📏 Tensão de referência: {dialog.resultado}V")
            
            # Atualizar referência
            self.data_manager.definir_referencia(dialog.resultado)
            
            # Enviar para Arduino
            if self.serial_manager.escrever(f"{dialog.resultado}\n"):
                print("📤 Valor enviado para Arduino")
                
                # Aguardar confirmação
                for _ in range(10):
                    linha = self.serial_manager.ler_linha()
                    if linha and "CALIBRACAO_CONCLUIDA" in linha:
                        break
                    time.sleep(0.5)
                
                messagebox.showinfo("Calibração", 
                                  f"Calibração realizada com sucesso!\n\n"
                                  f"Referência: {self.data_manager.tensao_referencia:.1f}V\n"
                                  f"Faixa do gráfico: {self.data_manager.faixa_tensao_min:.0f}V a {self.data_manager.faixa_tensao_max:.0f}V")
            else:
                messagebox.showerror("Erro", "Não foi possível enviar calibração")
        else:
            print("❌ Calibração cancelada")
            messagebox.showwarning("Calibração Cancelada", 
                                 "A calibração foi cancelada.\nOs dados podem não ser precisos.")
        
        self.calibrando = False
    
    # Métodos da IA
    def analisar_dados_ia(self):
        """Abre chat com análise automática"""
        try:
            chat_window = GeminiChatDialog(
                self.root, 
                self.data_manager.dados, 
                self.data_manager.tensao_referencia
            )
            chat_window.focus()
            chat_window.after(500, lambda: chat_window.pergunta_rapida(
                "Analise os dados atuais do meu sistema elétrico e me dê recomendações."
            ))
        except Exception as e:
            print(f"❌ Erro ao analisar dados: {e}")
    
    def sugestoes_economia(self):
        """Abre chat com sugestões de economia"""
        try:
            chat_window = GeminiChatDialog(
                self.root, 
                self.data_manager.dados, 
                self.data_manager.tensao_referencia
            )
            chat_window.focus()
            chat_window.after(500, lambda: chat_window.pergunta_rapida(
                "Com base nos dados atuais, dê sugestões para economizar energia elétrica."
            ))
        except Exception as e:
            print(f"❌ Erro ao solicitar sugestões: {e}")
    
    def calculos_eletricos(self):
        """Abre chat para cálculos elétricos"""
        try:
            chat_window = GeminiChatDialog(
                self.root, 
                self.data_manager.dados, 
                self.data_manager.tensao_referencia
            )
            chat_window.focus()
            chat_window.after(500, lambda: chat_window.pergunta_rapida(
                "Ajude-me com cálculos elétricos e explique as fórmulas."
            ))
        except Exception as e:
            print(f"❌ Erro ao abrir cálculos: {e}")
    
    def run(self):
        """Inicia a aplicação"""
        print("\n" + "="*80)
        print("⚡ POWERGRID AI - SISTEMA MONOFÁSICO")
        print("="*80)
        print("\n🔧 DICAS PARA DETECÇÃO DE PORTAS SERIAIS:")
        print("1. Feche o IDE Arduino")
        print("2. Conecte o Arduino via USB")
        print("3. Aguarde o driver instalar (se necessário)")
        print("4. Execute o VS Code como Administrador (Windows)")
        print("5. Verifique as portas no gerenciador de dispositivos")
        print("="*80)
        
        # Atualizar portas na sidebar
        if hasattr(self, 'sidebar') and self.sidebar:
            self.sidebar.atualizar_portas()
        
        # Iniciar o loop principal da interface
        self.root.mainloop()
        
        # Limpeza ao fechar
        if hasattr(self, 'serial_manager'):
            self.serial_manager.desconectar()
        print("\n🎉 APLICAÇÃO FINALIZADA!")