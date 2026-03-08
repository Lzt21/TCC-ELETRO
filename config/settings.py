import customtkinter as ctk

# Aparência
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Cores
CORES = {
    "primaria": "#00d4ff",
    "secundaria": "#ff6b35",
    "sucesso": "#00ff88",
    "alerta": "#ffaa00",
    "perigo": "#ff4444",
    "fundo": "#0f1b2d",
    "card": "#1a2b3e",
    "texto": "#ffffff"
}

# ⚡ Configurações gerais
TENSAO_PADRAO = 127.0
BAUDRATE = 9600
TIMEOUT_SERIAL = 1
MAX_PONTOS_GRAFICO = 50
INTERVALO_ATUALIZACAO = 1000  # ← ESSA É A QUE FALTAVA

# 🔧 Calibração
TENSAO_MIN_VALIDA = 50
TENSAO_MAX_VALIDA = 250

# 📊 Gráficos
FAIXA_TENSAO_PADRAO = 300
FAIXA_CORRENTE_PADRAO = 2.0
FAIXA_POTENCIA_PADRAO = 300