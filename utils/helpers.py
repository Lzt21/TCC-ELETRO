# Funções utilitárias gerais
import math

def escurecer_cor(cor_hex, percentual=30):
    """Escurece uma cor hexadecimal"""
    cor = cor_hex.lstrip('#')
    r = int(cor[0:2], 16)
    g = int(cor[2:4], 16)
    b = int(cor[4:6], 16)
    
    r = max(0, r - percentual)
    g = max(0, g - percentual)
    b = max(0, b - percentual)
    
    return f'#{r:02x}{g:02x}{b:02x}'

def formatar_tempo(segundos):
    """Formata segundos em minutos:segundos"""
    minutos = segundos // 60
    segs = segundos % 60
    return f"{minutos:02d}:{segs:02d}"

def calcular_angulo_fase(fator_potencia):
    """Calcula ângulo de fase a partir do FP"""
    if fator_potencia > 0:
        return math.degrees(math.acos(min(1.0, max(-1.0, fator_potencia))))
    return 0

def obter_status_fp(fator_potencia):
    """Retorna status baseado no fator de potência"""
    if fator_potencia > 0.98:
        return "Excelente", "#00ff88"
    elif fator_potencia > 0.95:
        return "Bom", "#ffaa00"
    else:
        return "Baixo", "#ff4444"