# Componente da barra lateral
import customtkinter as ctk
import threading
from config.settings import CORES
from utils.helpers import formatar_tempo

class SidebarComponent:
    """Componente da barra lateral com menu e controles"""
    
    def __init__(self, parent, callbacks):
        """
        Args:
            parent: Frame pai
            callbacks: Dicionário com funções de callback
                {
                    'mostrar_dashboard': func,
                    'mostrar_analise': func,
                    'mostrar_tendencias': func,
                    'mostrar_configuracoes': func,
                    'mostrar_assistente_ia': func,
                    'toggle_conexao_serial': func,
                    'toggle_modo_simulacao': func,
                    'abrir_chat_gemini': func,
                    'listar_portas': func
                }
        """
        self.parent = parent
        self.callbacks = callbacks
        self.cor_card = CORES["card"]
        self.cor_primaria = CORES["primaria"]
        self.cor_sucesso = CORES["sucesso"]
        self.cor_alerta = CORES["alerta"]
        self.cor_perigo = CORES["perigo"]
        
        self.frame = None
        self.porta_var = None
        self.porta_combobox = None
        self.btn_conectar = None
        self.btn_simulacao = None
        self.btn_ia = None
        self.status_modo = None
        self.status_serial = None
        self.status_online = None
        self.status_ia = None
        self.tempo_operacao = None
        
        self.criar_sidebar()
    
    def criar_sidebar(self):
        """Cria a barra lateral completa"""
        self.frame = ctk.CTkFrame(self.parent, width=280, fg_color=self.cor_card, corner_radius=15)
        self.frame.pack(side="left", fill="y", padx=(0, 20))
        self.frame.pack_propagate(False)
        
        self.criar_logo()
        self.criar_menu()
        self.criar_configuracao_serial()
        self.criar_status()
    
    def criar_logo(self):
        """Cria o logo e título"""
        logo_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        logo_frame.pack(pady=40)
        
        logo = ctk.CTkLabel(logo_frame, 
                           text="⚡ POWERGRID AI",
                           font=("Arial", 20, "bold"),
                           text_color=self.cor_primaria)
        logo.pack()
        
        slogan = ctk.CTkLabel(logo_frame,
                             text="Sistema Monofásico",
                             font=("Arial", 12),
                             text_color="#8899aa")
        slogan.pack(pady=(5, 0))
    
    def criar_menu(self):
        """Cria o menu de navegação"""
        menu_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        menu_frame.pack(fill="x", padx=20, pady=40)
        
        botoes_menu = [
            ("📊 Dashboard", self.callbacks['mostrar_dashboard']),
            ("🔍 Análise Detalhada", self.callbacks['mostrar_analise']),
            ("📈 Tendências", self.callbacks['mostrar_tendencias']),
            ("🤖 Assistente IA", self.callbacks['mostrar_assistente_ia'])
        ]
        
        for texto, comando in botoes_menu:
            btn = ctk.CTkButton(menu_frame,
                              text=texto,
                              command=comando,
                              fg_color="transparent",
                              hover_color="#2a3b4c",
                              font=("Arial", 14),
                              anchor="w",
                              height=45)
            btn.pack(fill="x", pady=5)
    
    def criar_configuracao_serial(self):
        """Cria a seção de configuração serial"""
        serial_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        serial_frame.pack(fill="x", padx=20, pady=20)
        
        # Título
        serial_label = ctk.CTkLabel(serial_frame,
                                  text="CONFIGURAÇÃO SERIAL",
                                  font=("Arial", 12, "bold"),
                                  text_color=self.cor_primaria)
        serial_label.pack(anchor="w")
        
        # Combobox de portas
        self.porta_var = ctk.StringVar(value="Selecionar Porta")
        portas = self.callbacks['listar_portas']()
        
        self.porta_combobox = ctk.CTkComboBox(serial_frame,
                                            values=portas,
                                            variable=self.porta_var,
                                            width=200,
                                            command=self.atualizar_portas)
        self.porta_combobox.pack(pady=(10, 5))
        
        # Botão de conexão
        self.btn_conectar = ctk.CTkButton(serial_frame,
                                        text="🔌 CONECTAR",
                                        command=self.callbacks['toggle_conexao_serial'],
                                        fg_color=self.cor_sucesso,
                                        hover_color="#00cc77",
                                        width=200)
        self.btn_conectar.pack(pady=5)
        
        # Botão de modo simulação
        self.btn_simulacao = ctk.CTkButton(serial_frame,
                                         text="🎮 MODO SIMULAÇÃO",
                                         command=self.callbacks['toggle_modo_simulacao'],
                                         fg_color=self.cor_alerta,
                                         hover_color="#ff9900",
                                         width=200)
        self.btn_simulacao.pack(pady=5)
        
        # Botão IA
        self.btn_ia = ctk.CTkButton(serial_frame,
                                  text="🤖 CHAT COM GEMINI",
                                  command=self.callbacks['abrir_chat_gemini'],
                                  fg_color=self.cor_sucesso,
                                  hover_color="#00cc77",
                                  width=200)
        self.btn_ia.pack(pady=5)

        self.btn_treinamento = ctk.CTkButton(serial_frame,
                                      text="🎯 TREINAR IA",
                                      command=self.callbacks['abrir_treinamento_nilm'],
                                      fg_color="#9d4edd",  # Roxo
                                      hover_color="#7b2cbf",
                                      width=200)
        self.btn_treinamento.pack(pady=5)
        
    def criar_status(self):
        """Cria a seção de status"""
        status_frame = ctk.CTkFrame(self.frame, fg_color="transparent")
        status_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        
        # Status do modo
        self.status_modo = ctk.CTkLabel(status_frame,
                                      text="● MODO: SIMULAÇÃO",
                                      text_color=self.cor_alerta,
                                      font=("Arial", 10, "bold"))
        self.status_modo.pack()
        
        # Status serial
        self.status_serial = ctk.CTkLabel(status_frame,
                                        text="● SERIAL DESCONECTADO",
                                        text_color=self.cor_perigo,
                                        font=("Arial", 10, "bold"))
        self.status_serial.pack(pady=(2, 0))
        
        # Status online
        self.status_online = ctk.CTkLabel(status_frame,
                                        text="● SISTEMA PRONTO",
                                        text_color=self.cor_alerta,
                                        font=("Arial", 10, "bold"))
        self.status_online.pack(pady=(2, 0))
        
        # Status IA
        self.status_ia = ctk.CTkLabel(status_frame,
                                    text="● GEMINI: CONECTADO",
                                    text_color=self.cor_sucesso,
                                    font=("Arial", 10, "bold"))
        self.status_ia.pack(pady=(2, 0))
        
        # Tempo de operação
        self.tempo_operacao = ctk.CTkLabel(status_frame,
                                         text="Operando há 00:00",
                                         text_color="#8899aa",
                                         font=("Arial", 9))
        self.tempo_operacao.pack(pady=(5, 0))
    
    def atualizar_portas(self, choice=None):
        """Atualiza a lista de portas seriais"""
        portas = self.callbacks['listar_portas']()
        self.porta_combobox.configure(values=portas)
    
    def atualizar_status(self, modo_simulacao, serial_conectada, gemini_disponivel, monitorando, tempo):
        """Atualiza todos os status na sidebar"""
        # Status do modo
        if modo_simulacao:
            self.status_modo.configure(text="● MODO: SIMULAÇÃO", text_color=self.cor_alerta)
            self.btn_simulacao.configure(text="🎮 MODO SIMULAÇÃO", fg_color=self.cor_alerta)
        else:
            self.status_modo.configure(text="● MODO: REAL", text_color=self.cor_sucesso)
            self.btn_simulacao.configure(text="📡 MODO REAL", fg_color=self.cor_sucesso)
        
        # Status serial
        if serial_conectada:
            self.status_serial.configure(text="● SERIAL CONECTADO", text_color=self.cor_sucesso)
            self.btn_conectar.configure(text="🔌 DESCONECTAR", fg_color=self.cor_perigo)
        else:
            self.status_serial.configure(text="● SERIAL DESCONECTADO", text_color=self.cor_perigo)
            self.btn_conectar.configure(text="🔌 CONECTAR", fg_color=self.cor_sucesso)
        
        # Status online
        if monitorando:
            self.status_online.configure(text="● MONITORANDO", text_color=self.cor_primaria)
        else:
            self.status_online.configure(text="● PAUSADO", text_color=self.cor_alerta)
        
        # Status IA
        if gemini_disponivel:
            self.status_ia.configure(text="● GEMINI: CONECTADO", text_color=self.cor_sucesso)
            self.btn_ia.configure(text="🤖 CHAT COM GEMINI", fg_color=self.cor_sucesso)
        else:
            self.status_ia.configure(text="● GEMINI: SIMULAÇÃO", text_color=self.cor_alerta)
            self.btn_ia.configure(text="🤖 SIMULAÇÃO IA", fg_color=self.cor_alerta)
        
        # Tempo de operação
        self.tempo_operacao.configure(text=f"Operando há {formatar_tempo(tempo)}")
    
    def get_porta_selecionada(self):
        """Retorna a porta serial selecionada"""
        return self.porta_var.get()