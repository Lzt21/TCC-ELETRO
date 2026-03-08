# Diálogo de chat com Gemini
import customtkinter as ctk
import threading
from datetime import datetime
from ai.gemini_client import GeminiClient
from ai.response_simulator import ResponseSimulator

class GeminiChatDialog(ctk.CTkToplevel):
    """Diálogo de chat com assistente IA"""
    
    def __init__(self, parent, dados_atuais, tensao_referencia):
        super().__init__(parent)
        self.title("🤖 POWERGRID AI - Assistente Gemini")
        self.geometry("900x700")
        self.configure(fg_color="#0f1b2d")
        
        self.dados = dados_atuais
        self.tensao_referencia = tensao_referencia
        
        # Inicializar clientes
        self.gemini_client = GeminiClient()
        self.simulator = ResponseSimulator(dados_atuais, tensao_referencia)
        
        self.criar_interface()
    
    def criar_interface(self):
        """Cria a interface do chat"""
        # Layout principal
        main_frame = ctk.CTkFrame(self, fg_color="#0f1b2d")
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Header
        self.criar_header(main_frame)
        
        # Informações atuais
        self.criar_info_frame(main_frame)
        
        # Área do chat
        self.criar_chat_area(main_frame)
        
        # Área de entrada
        self.criar_input_area(main_frame)
        
        # Botões de perguntas rápidas
        self.criar_quick_buttons(main_frame)
    
    def criar_header(self, parent):
        """Cria o cabeçalho"""
        header_frame = ctk.CTkFrame(parent, fg_color="#1a2b3e", corner_radius=10)
        header_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(header_frame, 
                    text="🤖 ASSISTENTE DE CONSUMO ELÉTRICO",
                    font=("Arial", 18, "bold"),
                    text_color="#00d4ff").pack(pady=15)
        
        status = "CONECTADO" if self.gemini_client.disponivel else "MODO SIMULAÇÃO"
        cor = "#00ff88" if self.gemini_client.disponivel else "#ffaa00"
        
        ctk.CTkLabel(header_frame,
                    text=f"Status: {status}",
                    font=("Arial", 12, "bold"),
                    text_color=cor).pack(pady=(0, 10))
    
    def criar_info_frame(self, parent):
        """Cria frame com informações atuais"""
        info_frame = ctk.CTkFrame(parent, fg_color="#1a2b3e", corner_radius=10)
        info_frame.pack(fill="x", pady=(0, 10))
        
        ctk.CTkLabel(info_frame,
                    text="📊 DADOS ATUAIS DO SISTEMA:",
                    font=("Arial", 14, "bold"),
                    text_color="#ffaa00").pack(pady=(10, 5))
        
        info_text = (f"⚡ Tensão: {self.dados['tensao']:.1f}V | "
                    f"🔌 Corrente: {self.dados['corrente']:.3f}A | "
                    f"🔋 Potência: {self.dados['potencia_ativa']:.1f}W | "
                    f"Φ FP: {self.dados['fator_potencia']:.3f}")
        
        ctk.CTkLabel(info_frame,
                    text=info_text,
                    font=("Arial", 12),
                    text_color="#ffffff").pack(pady=(0, 10))
    
    def criar_chat_area(self, parent):
        """Cria a área de mensagens do chat"""
        chat_frame = ctk.CTkFrame(parent, fg_color="transparent")
        chat_frame.pack(fill="both", expand=True)
        
        self.messages_frame = ctk.CTkScrollableFrame(
            chat_frame, fg_color="#1a2b3e", corner_radius=10,
            scrollbar_button_color="#2a3b4c", scrollbar_button_hover_color="#3a4b5c"
        )
        self.messages_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # Mensagem inicial
        if self.gemini_client.disponivel:
            self.adicionar_mensagem("assistente", 
                "Olá! Sou o assistente de energia do PowerGrid AI. Como posso ajudar?")
        else:
            self.adicionar_mensagem("assistente",
                "⚠️ **MODO SIMULAÇÃO**\n\nFaça sua pergunta sobre energia elétrica.")
    
    def criar_input_area(self, parent):
        """Cria a área de entrada de texto"""
        input_frame = ctk.CTkFrame(parent, fg_color="transparent")
        input_frame.pack(fill="x", pady=(10, 0))
        
        self.user_input = ctk.CTkTextbox(input_frame, height=60,
                                        font=("Arial", 12),
                                        fg_color="#2a3b4c",
                                        border_width=1,
                                        border_color="#00d4ff")
        self.user_input.pack(side="left", fill="both", expand=True, padx=(0, 10))
        self.user_input.bind("<Return>", self.enviar_mensagem_enter)
        self.user_input.insert("1.0", "Digite sua pergunta sobre energia...")
        self.user_input.bind("<FocusIn>", self.limpar_placeholder)
        
        btn_frame = ctk.CTkFrame(input_frame, fg_color="transparent", width=100)
        btn_frame.pack(side="right")
        
        ctk.CTkButton(btn_frame, text="Enviar", command=self.enviar_mensagem,
                     fg_color="#00d4ff", hover_color="#0099cc",
                     width=100, height=40).pack()
        
        ctk.CTkButton(btn_frame, text="Limpar", command=self.limpar_chat,
                     fg_color="#ff6b35", hover_color="#cc552a",
                     width=100, height=40).pack(pady=(5, 0))
    
    def criar_quick_buttons(self, parent):
        """Cria botões de perguntas rápidas"""
        quick_frame = ctk.CTkFrame(parent, fg_color="transparent")
        quick_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkLabel(quick_frame,
                    text="Perguntas rápidas:",
                    font=("Arial", 12, "bold"),
                    text_color="#8899aa").pack(anchor="w", pady=(0, 5))
        
        perguntas = [
            ("💡 Economia", "Como economizar energia elétrica?"),
            ("📊 Análise", "Analise meus dados atuais de consumo"),
            ("💰 Custo", "Quanto custa este consumo por mês?"),
            ("🔧 Dicas", "Dê dicas para melhorar eficiência")
        ]
        
        for text, question in perguntas:
            ctk.CTkButton(quick_frame, text=text,
                        command=lambda q=question: self.pergunta_rapida(q),
                        fg_color="#2a3b4c", hover_color="#3a4b5c",
                        font=("Arial", 11), height=35,
                        width=150).pack(side="left", padx=(0, 10))
    
    def adicionar_mensagem(self, sender, message):
        """Adiciona uma mensagem ao chat"""
        frame = ctk.CTkFrame(self.messages_frame, 
                            fg_color="#2a3b4c" if sender == "usuario" else "#1a2b3e",
                            corner_radius=10)
        frame.pack(fill="x", padx=5, pady=5)
        
        # Cabeçalho
        header_frame = ctk.CTkFrame(frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        if sender == "usuario":
            ctk.CTkLabel(header_frame, text="👤 VOCÊ", 
                        font=("Arial", 11, "bold"),
                        text_color="#00d4ff").pack(side="left")
        else:
            ctk.CTkLabel(header_frame, text="🤖 POWERGRID AI", 
                        font=("Arial", 11, "bold"),
                        text_color="#ffaa00").pack(side="left")
        
        ctk.CTkLabel(header_frame, 
                    text=datetime.now().strftime("%H:%M"),
                    font=("Arial", 10),
                    text_color="#8899aa").pack(side="right")
        
        # Mensagem
        text_frame = ctk.CTkFrame(frame, fg_color="transparent")
        text_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(text_frame, text=message,
                   font=("Arial", 12), text_color="#ffffff",
                   justify="left", anchor="w", wraplength=800).pack(anchor="w")
        
        self.messages_frame._parent_canvas.yview_moveto(1.0)
    
    def enviar_mensagem(self):
        """Envia mensagem do usuário"""
        user_text = self.user_input.get("1.0", "end-1c").strip()
        if not user_text or user_text == "Digite sua pergunta sobre energia...":
            return
        
        self.adicionar_mensagem("usuario", user_text)
        self.user_input.delete("1.0", "end")
        
        threading.Thread(target=self.processar_resposta, args=(user_text,), daemon=True).start()
    
    def enviar_mensagem_enter(self, event):
        """Envia mensagem quando Enter é pressionado"""
        if event.state & 0x4:  # Ctrl pressionado
            return
        self.enviar_mensagem()
        return "break"
    
    def processar_resposta(self, user_text):
        """Processa a resposta"""
        if self.gemini_client.disponivel:
            resposta = self.gemini_client.gerar_resposta(user_text, self.dados)
        else:
            resposta = self.simulator.simular_resposta(user_text)
        
        self.after(0, lambda: self.adicionar_mensagem("assistente", resposta))
    
    def limpar_placeholder(self, event):
        """Limpa o placeholder"""
        if self.user_input.get("1.0", "end-1c") == "Digite sua pergunta sobre energia...":
            self.user_input.delete("1.0", "end")
    
    def pergunta_rapida(self, question):
        """Insere pergunta rápida"""
        self.user_input.delete("1.0", "end")
        self.user_input.insert("1.0", question)
    
    def limpar_chat(self):
        """Limpa o chat"""
        for widget in self.messages_frame.winfo_children():
            widget.destroy()
        
        self.adicionar_mensagem("assistente", "Chat limpo. Como posso ajudar?")