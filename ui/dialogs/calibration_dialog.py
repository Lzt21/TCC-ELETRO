# Diálogo de calibração
import customtkinter as ctk
from tkinter import messagebox

class CalibrationDialog(ctk.CTkToplevel):
    """Diálogo para calibração do sensor"""
    
    def __init__(self, parent, tensao_sensor):
        super().__init__(parent)
        self.title("🔧 CALIBRAÇÃO DO SENSOR")
        self.geometry("500x350")
        self.resizable(False, False)
        
        self.grab_set()
        self.transient(parent)
        self.resultado = None
        self.tensao_sensor = tensao_sensor
        
        self.criar_interface()
    
    def criar_interface(self):
        """Cria os elementos da interface"""
        frame = ctk.CTkFrame(self, fg_color="#1a2b3e")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(frame, text="⚡ CALIBRAÇÃO DO SENSOR DE TENSÃO", 
                    font=("Arial", 18, "bold"), text_color="#00d4ff").pack(pady=20)
        
        # Tensão medida
        ctk.CTkLabel(frame, text=f"Tensão medida pelo sensor: {self.tensao_sensor:.1f} V", 
                    font=("Arial", 14)).pack(pady=10)
        
        # Instruções
        ctk.CTkLabel(frame, text="1. Meça a tensão REAL com um multímetro", 
                    font=("Arial", 12)).pack(pady=5)
        ctk.CTkLabel(frame, text="2. Digite o valor medido abaixo:", 
                    font=("Arial", 12)).pack(pady=5)
        
        # Entrada
        self.entry_tensao = ctk.CTkEntry(frame, placeholder_text="Ex: 127.5 ou 231.0", 
                                        font=("Arial", 16, "bold"), 
                                        width=200, height=40, justify="center")
        self.entry_tensao.pack(pady=20)
        self.entry_tensao.focus_set()
        self.entry_tensao.bind('<Return>', lambda event: self.calibrar())
        
        # Botões
        self.criar_botoes(frame)
        
        # Instrução extra
        ctk.CTkLabel(frame, text="Pressione ENTER para confirmar", 
                    font=("Arial", 10), text_color="#ffaa00").pack(pady=10)
    
    def criar_botoes(self, parent):
        """Cria os botões do diálogo"""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="✅ CALIBRAR", command=self.calibrar,
                     fg_color="#00ff88", hover_color="#00cc77",
                     font=("Arial", 14, "bold"), width=150).pack(side="left", padx=10)
        
        ctk.CTkButton(btn_frame, text="❌ CANCELAR", command=self.cancelar,
                     fg_color="#ff4444", hover_color="#cc3333",
                     font=("Arial", 14), width=150).pack(side="left", padx=10)
    
    def calibrar(self, event=None):
        """Processa a calibração"""
        try:
            valor = float(self.entry_tensao.get().replace(",", "."))
            if 50 <= valor <= 250:
                self.resultado = valor
                self.destroy()
            else:
                messagebox.showerror("Valor inválido", "Digite um valor entre 50V e 250V")
        except:
            messagebox.showerror("Valor inválido", "Digite um número válido (ex: 127.5)")
    
    def cancelar(self):
        """Cancela a calibração"""
        self.resultado = None
        self.destroy()