import serial
import tkinter as tk
import math
import time

class SeguidorLineaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Seguidor de Línea - Monitor de Calibración")
        self.root.geometry("1000x700")
        
        # Inicializar contadores
        self.contador_dibujo = 0
        self.error_count = 0
        
        self.ser = self.conectar_serial()
        self.setup_ui()
        self.datos_calibracion = {"min": [], "max": []}
        
    def conectar_serial(self):
        puertos = ['COM3', 'COM4', 'COM5', '/dev/ttyACM0', '/dev/ttyUSB0']
        
        for puerto in puertos:
            try:
                ser = serial.Serial(puerto, 115200, timeout=1)
                print(f"✅ Conectado a {puerto}")
                return ser
            except serial.SerialException:
                print(f"❌ No se pudo conectar a {puerto}")
                continue
        
        print("⚠️  Ejecutando en modo simulación")
        return None
    
    def setup_ui(self):
        # Frame principal
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Canvas para gráfico de barras
        self.canvas = tk.Canvas(main_frame, width=950, height=400, bg="white")
        self.canvas.pack(pady=10)
        
        # Mejorar rendimiento del canvas
        self.canvas.config(highlightthickness=0, borderwidth=0)
        
        # Frame de información
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        self.label_pos = tk.Label(info_frame, text="Posición: 0.00", font=("Arial", 14))
        self.label_pos.pack(side=tk.LEFT, padx=10)
        
        self.label_mode = tk.Label(info_frame, text="Modo: Esperando datos...", font=("Arial", 12))
        self.label_mode.pack(side=tk.LEFT, padx=10)
        
        self.label_rango = tk.Label(info_frame, text="Rango: 0-4095", font=("Arial", 10), fg="blue")
        self.label_rango.pack(side=tk.LEFT, padx=10)
        
        # Frame de estado de calibración
        cal_frame = tk.Frame(main_frame)
        cal_frame.pack(fill=tk.X, pady=5)
        
        self.label_calib = tk.Label(cal_frame, text="Calibración: No iniciada", font=("Arial", 11), fg="red")
        self.label_calib.pack(side=tk.LEFT, padx=10)
        
        self.label_diferencia = tk.Label(cal_frame, text="Dif. Min-Max: --", font=("Arial", 10))
        self.label_diferencia.pack(side=tk.LEFT, padx=10)
        
        # Área de log para mensajes de depuración
        log_frame = tk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        tk.Label(log_frame, text="Mensajes del Sistema:", font=("Arial", 10, "bold")).pack(anchor=tk.W)
        
        self.text_log = tk.Text(log_frame, height=8, width=100, font=("Consolas", 8))
        scrollbar = tk.Scrollbar(log_frame, command=self.text_log.yview)
        self.text_log.config(yscrollcommand=scrollbar.set)
        
        self.text_log.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Configuración de visualización
        self.num_sensores = 16
        self.ancho_barra = 45
        self.espaciado = 8
        self.posiciones_x = [70 + i * (self.ancho_barra + self.espaciado) for i in range(self.num_sensores)]
        
        # Dibujar elementos estáticos una sola vez
        self.dibujar_elementos_estaticos()
        
        # Datos actuales
        self.datos_actuales = {
            'valores': [0] * 16,
            'posicion': 0.0,
            'modo': 'RAW',
            'min_vals': [0] * 16,
            'max_vals': [0] * 16
        }
        
        # Referencias para elementos dinámicos
        self.barras = [None] * 16
        self.textos_valores = [None] * 16
        self.linea_posicion = None
        self.texto_linea = None
        
        self.actualizar_datos()
    
    def dibujar_elementos_estaticos(self):
        """Dibuja los elementos que no cambian (S1-S16 y referencias)"""
        # Dibujar números de sensores (S1 a S16) - SOLO UNA VEZ
        for i in range(self.num_sensores):
            x0 = self.posiciones_x[i]
            self.canvas.create_text(x0 + self.ancho_barra/2, 365, 
                                  text=f"S{i+1}", font=("Arial", 9, "bold"), tags="estatico")
        
        # Dibujar referencias estáticas
        self.dibujar_referencias_simplificadas()
    
    def dibujar_referencias_simplificadas(self):
        """Versión optimizada de referencias"""
        # Solo línea de 50%
        y_mitad = 200  # 350 - 150
        self.canvas.create_line(70, y_mitad, self.posiciones_x[15] + self.ancho_barra, y_mitad, 
                              fill="gray", dash=(4,2), width=1, tags="estatico")
        
        # Referencias mínimas
        self.canvas.create_text(50, 20, text="REF:", font=("Arial", 8, "bold"), tags="estatico")
        self.canvas.create_text(50, 35, text="0=Blanco", font=("Arial", 7), fill="green", tags="estatico")
        self.canvas.create_text(50, 50, text="4095=Negro", font=("Arial", 7), fill="red", tags="estatico")
    
    def log_mensaje(self, mensaje):
        """Agregar mensaje al área de log"""
        self.text_log.insert(tk.END, f"{time.strftime('%H:%M:%S')} - {mensaje}\n")
        self.text_log.see(tk.END)
    
    def leer_datos_seriales(self):
        """Función separada para lectura eficiente de datos"""
        if self.ser and self.ser.in_waiting:
            try:
                # Leer múltiples líneas si están disponibles
                lineas = []
                while self.ser.in_waiting:
                    linea = self.ser.readline().decode('utf-8').strip()
                    if linea:
                        lineas.append(linea)
                
                # Procesar solo la última línea para evitar acumulación
                if lineas:
                    self.procesar_linea(lineas[-1])
                    
            except Exception as e:
                self.error_count += 1
                if self.error_count % 50 == 0:  # Log cada 50 errores
                    self.log_mensaje(f"Errores seriales: {self.error_count}")
        
        elif self.ser is None:
            self.simular_datos()
    
    def actualizar_datos(self):
        # Leer datos seriales sin bloquear
        self.leer_datos_seriales()
        
        # Dibujar interfaz
        self.dibujar_interfaz()
        
        # Programar próxima actualización
        self.root.after(30, self.actualizar_datos)
    
    def procesar_linea(self, linea):
        # Mostrar mensajes informativos en el log
        if not linea.startswith(('RAW', 'MIN', 'MAX', 'CAL', 'POS', 'CRU')):
            self.log_mensaje(linea)
            return
            
        partes = linea.split(',')
        
        if partes[0] == "RAW":
            self.datos_actuales['valores'] = list(map(int, partes[1:17]))
            self.datos_actuales['modo'] = 'RAW'
            self.label_mode.config(text="Modo: Valores Crudos")
            self.label_rango.config(text="Rango: 0-4095 (Crudos)")
            
        elif partes[0] == "MIN":
            self.datos_actuales['valores'] = list(map(int, partes[1:17]))
            self.datos_actuales['modo'] = 'MIN'
            self.datos_actuales['min_vals'] = list(map(int, partes[1:17]))
            self.label_mode.config(text="Modo: Valores Mínimos")
            self.label_calib.config(text="Calibración: Capturando Mínimos", fg="orange")
            
        elif partes[0] == "MAX":
            self.datos_actuales['valores'] = list(map(int, partes[1:17]))
            self.datos_actuales['modo'] = 'MAX'
            self.datos_actuales['max_vals'] = list(map(int, partes[1:17]))
            self.label_mode.config(text="Modo: Valores Máximos")
            self.label_calib.config(text="Calibración: Capturando Máximos", fg="orange")
            
        elif partes[0] == "CAL":
            self.datos_actuales['valores'] = list(map(int, partes[1:17]))
            self.datos_actuales['modo'] = 'CAL'
            self.label_mode.config(text="Modo: Valores Calibrados")
            self.label_calib.config(text="Calibración: Activa", fg="green")
            
        elif partes[0] == "POS":
            self.datos_actuales['posicion'] = float(partes[1])
            self.actualizar_texto_posicion()
    
    def actualizar_texto_posicion(self):
        """Actualizar solo el texto de posición"""
        self.label_pos.config(text=f"Posición: {self.datos_actuales['posicion']:.2f}")
    
    def simular_datos(self):
        # Simulación mejorada para pruebas
        import random
        
        if self.datos_actuales['modo'] == 'MIN':
            # Simular valores bajos (blanco)
            self.datos_actuales['valores'] = [random.randint(50, 200) for _ in range(16)]
        elif self.datos_actuales['modo'] == 'MAX':
            # Simular valores altos (negro)
            self.datos_actuales['valores'] = [random.randint(3500, 4095) for _ in range(16)]
        else:
            # Simular seguimiento normal
            pos = (math.sin(time.time() * 0.3) + 1) / 2
            sensor_activo = int(pos * 15)
            
            self.datos_actuales['valores'] = [0] * 16
            for i in range(16):
                distancia = abs(i - sensor_activo)
                if distancia <= 2:
                    self.datos_actuales['valores'][i] = int(3500 * (1 - distancia/3) + 500)
                else:
                    self.datos_actuales['valores'][i] = random.randint(50, 200)
        
        self.datos_actuales['posicion'] = (sensor_activo - 7.5) * 6
        self.actualizar_texto_posicion()
        self.label_mode.config(text="Modo: SIMULACIÓN")
    
    def dibujar_interfaz(self):
        """Dibuja solo los elementos dinámicos (barras y línea)"""
        max_val = 4095
        
        # Actualizar o crear barras y textos
        for i in range(self.num_sensores):
            x0 = self.posiciones_x[i]
            y_base = 350
            
            # Calcular altura de la barra
            valor = self.datos_actuales['valores'][i]
            altura_barra = (valor / max_val) * 300 if max_val > 0 else 0
            y_superior = y_base - altura_barra
            
            # Color según el modo
            if self.datos_actuales['modo'] == 'RAW':
                color = 'blue'
            elif self.datos_actuales['modo'] == 'MIN':
                color = 'lightgreen'
            elif self.datos_actuales['modo'] == 'MAX':
                color = 'salmon'
            else:  # CAL
                color = 'lightblue' if valor < 1000 else 'darkblue' if valor > 3500 else 'blue'
            
            # Actualizar o crear barra
            if self.barras[i] is None:
                self.barras[i] = self.canvas.create_rectangle(
                    x0, y_base, x0 + self.ancho_barra, y_superior, 
                    fill=color, outline='black', width=1, tags="dinamico"
                )
            else:
                self.canvas.coords(self.barras[i], x0, y_base, x0 + self.ancho_barra, y_superior)
                self.canvas.itemconfig(self.barras[i], fill=color)
            
            # Actualizar texto del valor (cada 3 frames para mejor rendimiento)
            self.contador_dibujo += 1
            if self.contador_dibujo % 3 == 0:
                texto_valor = str(valor)
                if self.textos_valores[i] is None:
                    self.textos_valores[i] = self.canvas.create_text(
                        x0 + self.ancho_barra/2, y_superior - 12, 
                        text=texto_valor, font=("Arial", 7), tags="dinamico"
                    )
                else:
                    self.canvas.coords(self.textos_valores[i], x0 + self.ancho_barra/2, y_superior - 12)
                    self.canvas.itemconfig(self.textos_valores[i], text=texto_valor)
        
        # Actualizar línea de posición
        pos_x = 70 + ((self.datos_actuales['posicion'] + 45) / 90) * (self.posiciones_x[15] + self.ancho_barra - 70)
        
        if self.linea_posicion is None:
            self.linea_posicion = self.canvas.create_line(
                pos_x, 40, pos_x, 340, fill="red", width=3, arrow=tk.BOTH, tags="dinamico"
            )
            self.texto_linea = self.canvas.create_text(
                pos_x, 25, text="LÍNEA", fill="red", font=("Arial", 10, "bold"), tags="dinamico"
            )
        else:
            self.canvas.coords(self.linea_posicion, pos_x, 40, pos_x, 340)
            self.canvas.coords(self.texto_linea, pos_x, 25)

if __name__ == "__main__":
    root = tk.Tk()
    app = SeguidorLineaApp(root)
    root.mainloop()