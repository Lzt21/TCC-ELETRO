# Ponto de entrada da aplicação
from ai.nilm_detector import NILMDetector
from ui.dialogs.training_dialog import TrainingDialog
import customtkinter as ctk
from ui.main_window import PowerGridAI

if __name__ == "__main__":
    print("=" * 80)
    print("⚡ POWERGRID AI - SISTEMA MONOFÁSICO")
    print("=" * 80)
    
    app = PowerGridAI()
    app.run()