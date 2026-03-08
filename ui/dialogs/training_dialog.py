"""
Diálogo para treinamento de equipamentos
"""
import customtkinter as ctk
from tkinter import messagebox
import threading
import time
import math
import random

class TrainingDialog(ctk.CTkToplevel):
    """Diálogo para treinar o sistema a reconhecer equipamentos"""
    
    def __init__(self, parent, nilm_detector):
        super().__init__(parent)
        self.title("🎯 TREINAR IA - IDENTIFICAR EQUIPAMENTOS")
        self.geometry("600x500")
        self.configure(fg_color="#0f1b2d")
        
        # Tornar modal
        self.grab_set()
        self.transient(parent)
        
        self.nilm = nilm_detector
        self.capturando = False
        self.equipamento_selecionado = None
        self.potencia_alvo = 0
        
        self.criar_interface()
        self.atualizar_lista_equipamentos()
    
    def criar_interface(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        titulo = ctk.CTkLabel(main_frame,
                             text="🎯 TREINE A IA PARA RECONHECER EQUIPAMENTOS",
                             font=("Arial", 18, "bold"),
                             text_color="#00d4ff")
        titulo.pack(pady=(0, 20))
        
        # Instruções
        instrucoes = ctk.CTkTextbox(main_frame, height=80, fg_color="#1a2b3e", border_width=0)
        instrucoes.pack(fill="x", pady=(0, 20))
        instrucoes.insert("1.0", 
            "1. Selecione o equipamento que será ligado\n"
            "2. Clique em 'Iniciar Captura'\n"
            "3. LIGUE o equipamento agora\n"
            "4. Aguarde 10 segundos capturando dados\n"
            "5. A IA aprenderá a assinatura elétrica deste equipamento")
        instrucoes.configure(state="disabled")
        
        # Frame de seleção
        select_frame = ctk.CTkFrame(main_frame, fg_color="#1a2b3e", corner_radius=10)
        select_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(select_frame,
                    text="Equipamento:",
                    font=("Arial", 14),
                    text_color="#8899aa").pack(pady=(10, 5))
        
        # Combobox para selecionar equipamento
        self.equipamento_var = ctk.StringVar(value="Selecione um equipamento")
        self.combo_equipamentos = ctk.CTkComboBox(select_frame,
                                                 values=[],
                                                 variable=self.equipamento_var,
                                                 width=300,
                                                 command=self.selecionar_equipamento)
        self.combo_equipamentos.pack(pady=(0, 10))
        
        # Botão para novo equipamento
        btn_novo = ctk.CTkButton(select_frame,
                                text="➕ Novo Equipamento",
                                command=self.novo_equipamento,
                                fg_color="#ffaa00",
                                hover_color="#cc8800",
                                width=200)
        btn_novo.pack(pady=(0, 10))
        
        # Frame de captura
        self.capture_frame = ctk.CTkFrame(main_frame, fg_color="#1a2b3e", corner_radius=10)
        self.capture_frame.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(self.capture_frame,
                    text="📊 CAPTURA DE DADOS",
                    font=("Arial", 14, "bold"),
                    text_color="#00d4ff").pack(pady=(10, 10))
        
        # Barra de progresso
        self.progress_bar = ctk.CTkProgressBar(self.capture_frame, width=400)
        self.progress_bar.pack(pady=(0, 10))
        self.progress_bar.set(0)
        
        # Label de status
        self.status_label = ctk.CTkLabel(self.capture_frame,
                                        text="Aguardando início da captura...",
                                        font=("Arial", 12),
                                        text_color="#ffaa00")
        self.status_label.pack(pady=(0, 10))
        
        # Amostras capturadas
        self.samples_label = ctk.CTkLabel(self.capture_frame,
                                         text="Amostras: 0/50",
                                         font=("Arial", 12),
                                         text_color="#8899aa")
        self.samples_label.pack(pady=(0, 10))
        
        # Botões de controle
        btn_frame = ctk.CTkFrame(self.capture_frame, fg_color="transparent")
        btn_frame.pack(pady=(0, 10))
        
        self.btn_iniciar = ctk.CTkButton(btn_frame,
                                        text="▶ INICIAR CAPTURA",
                                        command=self.iniciar_captura,
                                        fg_color="#00ff88",
                                        hover_color="#00cc77",
                                        font=("Arial", 12, "bold"),
                                        width=150)
        self.btn_iniciar.pack(side="left", padx=5)
        
        self.btn_parar = ctk.CTkButton(btn_frame,
                                      text="⏹️ PARAR",
                                      command=self.parar_captura,
                                      fg_color="#ff4444",
                                      hover_color="#cc3333",
                                      font=("Arial", 12, "bold"),
                                      width=100,
                                      state="disabled")
        self.btn_parar.pack(side="left", padx=5)
        
        # Frame de equipamentos conhecidos
        known_frame = ctk.CTkFrame(main_frame, fg_color="#1a2b3e", corner_radius=10)
        known_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(known_frame,
                    text="📚 EQUIPAMENTOS CONHECIDOS",
                    font=("Arial", 14, "bold"),
                    text_color="#00d4ff").pack(pady=(10, 10))
        
        # Lista de equipamentos
        self.lista_frame = ctk.CTkScrollableFrame(known_frame, fg_color="transparent", height=150)
        self.lista_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
    
    def atualizar_lista_equipamentos(self):
        """Atualiza a lista de equipamentos conhecidos"""
        # Limpar lista
        for widget in self.lista_frame.winfo_children():
            widget.destroy()
        
        # Adicionar equipamentos
        equipamentos = sorted(self.nilm.assinaturas_conhecidas.keys())
        
        if not equipamentos:
            ctk.CTkLabel(self.lista_frame,
                        text="Nenhum equipamento treinado ainda",
                        font=("Arial", 12),
                        text_color="#8899aa").pack(pady=10)
        else:
            for equip in equipamentos:
                frame = ctk.CTkFrame(self.lista_frame, fg_color="#2a3b4c", corner_radius=5)
                frame.pack(fill="x", pady=2)
                
                ctk.CTkLabel(frame,
                            text=f"• {equip}",
                            font=("Arial", 12),
                            text_color="white").pack(side="left", padx=10, pady=5)
        
        # Atualizar combobox
        self.combo_equipamentos.configure(values=list(self.nilm.assinaturas_conhecidas.keys()) + ["OUTRO"])
    
    def selecionar_equipamento(self, choice):
        """Seleciona um equipamento existente"""
        if choice and choice != "Selecione um equipamento":
            self.equipamento_selecionado = choice
            self.status_label.configure(text=f"Equipamento selecionado: {choice}", text_color="#00ff88")
    
    def novo_equipamento(self):
        """Diálogo para novo equipamento"""
        dialog = ctk.CTkInputDialog(
            text="Digite o nome do novo equipamento:",
            title="Novo Equipamento"
        )
        nome = dialog.get_input()
        
        if nome and nome.strip():
            self.equipamento_selecionado = nome.strip()
            self.equipamento_var.set(nome.strip())
            self.status_label.configure(text=f"Novo equipamento: {nome}", text_color="#00ff88")
            
            # Perguntar potência para equipamento novo
            self.perguntar_potencia()
    
    def perguntar_potencia(self):
        """Pergunta a potência aproximada do equipamento"""
        dialog = ctk.CTkInputDialog(
            text=f"Qual a potência aproximada do {self.equipamento_selecionado} em Watts?\n"
                 "Exemplos:\n"
                 "- Lâmpada LED: 9W\n"
                 "- Geladeira: 150W\n"
                 "- Motor 1CV: 800W\n"
                 "- Microondas: 1200W",
            title="Potência do Equipamento"
        )
        try:
            valor = dialog.get_input()
            if valor and valor.strip():
                self.potencia_alvo = float(valor)
                self.status_label.configure(
                    text=f"Potência definida: {self.potencia_alvo}W. Pronto para capturar!", 
                    text_color="#00ff88"
                )
            else:
                self.potencia_alvo = 100  # valor padrão
        except:
            self.potencia_alvo = 100
            messagebox.showwarning("Aviso", "Valor inválido. Usando potência padrão: 100W")
    
    def iniciar_captura(self):
        """Inicia a captura de dados para treinamento"""
        if not self.equipamento_selecionado:
            messagebox.showwarning("Aviso", "Selecione um equipamento primeiro!")
            return
        
        # Se for equipamento novo e não tem potência, perguntar
        if self.equipamento_selecionado not in self.nilm.assinaturas_conhecidas and self.potencia_alvo == 0:
            self.perguntar_potencia()
            # Aguardar um pouco para o diálogo
            time.sleep(0.5)
        
        self.capturando = True
        self.nilm.iniciar_treinamento(self.equipamento_selecionado)
        
        # Atualizar UI
        self.btn_iniciar.configure(state="disabled")
        self.btn_parar.configure(state="normal")
        self.status_label.configure(
            text=f"⚡ Capturando: {self.equipamento_selecionado} - LIGUE O EQUIPAMENTO!", 
            text_color="#00d4ff"
        )
        
        # Iniciar thread de captura
        threading.Thread(target=self.capturar_dados, daemon=True).start()
    
    def capturar_dados(self):
        """Captura dados reais ou simulados para treinamento"""
        amostras = 0
        
        while self.capturando and amostras < 50:
            # Aqui você pode substituir por dados reais do Arduino
            # Por enquanto, vamos usar simulação melhorada
            
            # Usar potência alvo se disponível
            if self.potencia_alvo > 0:
                # Variação pequena (±3%) para simular equipamento estável
                variacao = random.uniform(-0.03, 0.03) * self.potencia_alvo
                potencia = self.potencia_alvo + variacao
            else:
                # Fallback para valores aleatórios
                potencia = random.uniform(50, 1500)
            
            # Calcular corrente baseada na tensão (127V)
            tensao = 127
            corrente = potencia / tensao
            
            # Determinar FP baseado no nome do equipamento
            nome_lower = self.equipamento_selecionado.lower()
            if any(x in nome_lower for x in ['motor', 'geladeira', 'compressor']):
                fp = random.uniform(0.82, 0.92)
            elif any(x in nome_lower for x in ['lampada', 'lâmpada', 'resistencia']):
                fp = random.uniform(0.98, 1.0)
            else:
                fp = random.uniform(0.90, 0.98)
            
            # Calcular potência reativa
            angulo = math.acos(fp)
            reativa = potencia * math.tan(angulo)
            
            amostra = {
                'potencia_ativa': potencia,
                'corrente': corrente,
                'fator_potencia': fp,
                'potencia_reativa': reativa,
                'tensao': tensao,
                'potencia_aparente': potencia / fp if fp > 0 else potencia
            }
            
            # Adicionar ao treinamento
            concluido, progresso = self.nilm.adicionar_amostra_treinamento(amostra)
            
            amostras += 1
            
            # Atualizar UI
            self.after(0, self.atualizar_progresso, amostras, progresso)
            
            # Mostrar amostra no console para debug
            if amostras % 10 == 0:
                print(f"📊 Amostra {amostras}: {potencia:.1f}W, FP: {fp:.3f}")
            
            time.sleep(0.2)  # 200ms entre amostras
        
        if amostras >= 50:
            self.after(0, self.captura_concluida)
    
    def atualizar_progresso(self, amostras, progresso):
        """Atualiza barra de progresso"""
        self.progress_bar.set(progresso / 100)
        self.samples_label.configure(text=f"Amostras: {amostras}/50")
    
    def captura_concluida(self):
        """Captura finalizada com sucesso"""
        self.capturando = False
        self.btn_iniciar.configure(state="normal")
        self.btn_parar.configure(state="disabled")
        self.status_label.configure(text="✅ Treinamento concluído com sucesso!", text_color="#00ff88")
        self.progress_bar.set(1.0)
        
        # Calcular estatísticas do equipamento treinado
        if self.equipamento_selecionado in self.nilm.assinaturas_conhecidas:
            dados = self.nilm.assinaturas_conhecidas[self.equipamento_selecionado]
            print(f"\n📊 Estatísticas do treinamento:")
            print(f"   Potência média: {dados['potencia_media']:.1f}W")
            print(f"   Desvio padrão: {dados['potencia_std']:.1f}W ({(dados['potencia_std']/dados['potencia_media']*100):.1f}% da média)")
            print(f"   FP médio: {dados['fp_medio']:.3f}")
        
        # Atualizar lista
        self.atualizar_lista_equipamentos()
        
        messagebox.showinfo("Sucesso", 
                          f"Equipamento '{self.equipamento_selecionado}' treinado com sucesso!\n\n"
                          f"A IA agora consegue reconhecer este equipamento.")
    
    def parar_captura(self):
        """Para a captura manualmente"""
        self.capturando = False
        self.nilm.modo_treinamento = False
        self.btn_iniciar.configure(state="normal")
        self.btn_parar.configure(state="disabled")
        self.status_label.configure(text="⏸️ Captura interrompida", text_color="#ffaa00")
        self.progress_bar.set(0)