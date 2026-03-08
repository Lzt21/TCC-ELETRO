# Gerenciamento de comunicação serial
import serial
import serial.tools.list_ports
import time
import os

class SerialManager:
    """Gerencia comunicação com Arduino via serial"""
    
    def __init__(self, baudrate=9600, timeout=1):
        self.baudrate = baudrate
        self.timeout = timeout
        self.porta_serial = None
        self.conectada = False
    
    def listar_portas(self):
        """Lista todas as portas seriais disponíveis"""
        portas = []
        try:
            portas_disponiveis = serial.tools.list_ports.comports()
            
            if not portas_disponiveis:
                if os.name == 'nt':  # Windows
                    portas_comuns = ['COM' + str(i) for i in range(1, 21)]
                    portas = [f"{p} - Porta Serial" for p in portas_comuns]
                else:  # Linux/Mac
                    portas_comuns = ['/dev/ttyUSB' + str(i) for i in range(0, 5)] + \
                                  ['/dev/ttyACM' + str(i) for i in range(0, 5)]
                    portas = [f"{p} - Porta Serial" for p in portas_comuns]
            else:
                for porta in portas_disponiveis:
                    descricao = porta.description if porta.description else "Porta Serial"
                    portas.append(f"{porta.device} - {descricao}")
                    
        except Exception as e:
            print(f"❌ Erro ao listar portas: {e}")
            portas = ["Nenhuma porta encontrada"]
        
        return portas
    
    def conectar(self, porta_nome):
        """Conecta a uma porta serial"""
        try:
            if " - " in porta_nome:
                porta_nome = porta_nome.split(" - ")[0]
            
            self.porta_serial = serial.Serial(
                port=porta_nome,
                baudrate=self.baudrate,
                timeout=self.timeout,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE
            )
            
            time.sleep(2)  # Aguardar Arduino inicializar
            self.porta_serial.reset_input_buffer()
            self.porta_serial.reset_output_buffer()
            
            self.conectada = True
            return True, f"Conectado em {porta_nome}"
            
        except serial.SerialException as e:
            if "PermissionError" in str(e):
                return False, "Permissão negada - Feche o IDE Arduino"
            return False, f"Erro de conexão: {str(e)}"
        except Exception as e:
            return False, f"Erro inesperado: {str(e)}"
    
    def desconectar(self):
        """Desconecta da porta serial"""
        if self.porta_serial:
            try:
                self.porta_serial.close()
            except:
                pass
        self.conectada = False
        self.porta_serial = None
    
    def ler_linha(self):
        """Lê uma linha da serial"""
        if not self.conectada or not self.porta_serial:
            return None
        
        try:
            if self.porta_serial.in_waiting > 0:
                linha_bytes = self.porta_serial.readline()
                
                # Tentar decodificar
                try:
                    return linha_bytes.decode('utf-8').strip()
                except:
                    try:
                        return linha_bytes.decode('ascii', errors='ignore').strip()
                    except:
                        return None
            return None
            
        except Exception as e:
            print(f"❌ Erro na leitura: {e}")
            return None
    
    def escrever(self, dados):
        """Escreve dados na serial"""
        if not self.conectada or not self.porta_serial:
            return False
        
        try:
            self.porta_serial.write(f"{dados}\n".encode('utf-8'))
            return True
        except:
            return False
    
    def ler_dados_medicao(self):
        """Tenta ler dados de medição (corrente,tensão)"""
        linha = self.ler_linha()
        if not linha:
            return None
        
        # Ignorar mensagens de calibração
        if any(x in linha for x in ["OFFSET", "TENSAO", "FATOR", "SENSIBILIDADE", 
                                   "CALIBRACAO", "SISTEMA", "INICIANDO"]):
            return None
        
        # Verificar formato esperado
        if ',' in linha:
            partes = linha.split(',')
            if len(partes) >= 2:
                try:
                    corrente = float(partes[0])
                    tensao = float(partes[1])
                    
                    # Validação básica
                    if 0 <= corrente < 20 and 0 <= tensao < 300:
                        return {
                            'corrente': corrente,
                            'tensao': tensao
                        }
                except:
                    pass
        
        return None