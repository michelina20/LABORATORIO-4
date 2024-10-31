#LABORATORIO 4

#Michel Ciabato Jiménez 5600595 y Eliana Domínguez Sabalza 5600587


import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, butter, filtfilt
from tkinter import Tk, filedialog
import pywt  # Asegúrate de tener instalada la librería pywt

# Función para seleccionar un archivo
def seleccionar_archivo():
    root = Tk()
    root.withdraw()
    root.call('wm', 'attributes', '.', '-topmost', True)
    archivo = filedialog.askopenfilename(
        title="Selecciona un archivo de señal",
        filetypes=[("Archivos de texto", "*.txt")]
    )
    return archivo

# Función para diseñar un filtro Butterworth pasabanda
def butter_bandpass(lowcut, highcut, fs, order=4):
    nyquist = 0.5 * fs  
    low = lowcut / nyquist
    high = highcut / nyquist
    b, a = butter(order, [low, high], btype='band')
    return b, a

# Función para aplicar el filtro
def aplicar_filtro(data, lowcut, highcut, fs, order=4):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = filtfilt(b, a, data)
    return y

# Función para aplicar la transformada wavelet continua 
def aplicar_transformada_wavelet(datos, fs):
    widths = np.arange(1, 100)  
    cwt_matrix, freqs = pywt.cwt(datos, widths, 'cmor', sampling_period=1/fs)
    freqs = freqs[::-1]
    cwt_matrix = cwt_matrix[::-1]
    
    # Grafica del espectrograma
    plt.figure(figsize=(12, 6))
    plt.imshow(np.abs(cwt_matrix), extent=[0, len(datos)/fs, freqs[0], freqs[-1]], aspect='auto', cmap='viridis')
    plt.colorbar(label='Potencia')
    plt.yscale('log')
    plt.ylabel('Frecuencia (Hz)')
    plt.xlabel('Tiempo (s)')
    plt.title('Espectrograma CWT - Wavelet Morlet')
    plt.show()
    
    return cwt_matrix, freqs

# Función para leer la señal, calcular estadísticas y graficarla
def graficar_senal(archivo, fs=100, n_subplots=5, num_bits=12):
    # Definir los límites de las bandas de frecuencia
    low_freq_limit = 0.04  # 0.04 Hz para la banda LF (Low Frequency)
    high_freq_limit = 0.15  # 0.15 Hz para la banda HF (High Frequency)

    # Calcular potencias de las bandas de frecuencia
    def calcular_potencias_bandap(cwt_matrix, freqs):
        potencia_LF = np.sum(np.abs(cwt_matrix[(freqs >= low_freq_limit) & (freqs <= high_freq_limit)])**2)
        potencia_HF = np.sum(np.abs(cwt_matrix[(freqs > high_freq_limit)])**2)
        return potencia_LF, potencia_HF

    try:
        # Leer los datos del archivo
        datos = np.loadtxt(archivo)
        
        # Calcular estadísticas
        media = np.mean(datos)
        varianza = np.var(datos)  # Varianza poblacional
        desviacion_estandar = np.std(datos)  # Desviación estándar poblacional
        mediana = np.median(datos)
        tipo_varianza = "Varianza Poblacional"
        
        # Calcular el tiempo total de muestreo
        tiempo_total = len(datos) / fs  # Tiempo en segundos
        
        # Encontrar picos para calcular frecuencia cardíaca
        picos, _ = find_peaks(datos, distance=fs//2)  
        rr_intervals = np.diff(picos) / fs 
        frecuencia_cardiaca = 60 / np.mean(rr_intervals) if rr_intervals.size > 0 else 0

        # Calcular parámetros de HRV
        sdnn = np.std(rr_intervals) if rr_intervals.size > 0 else 0  
        rmssd = np.sqrt(np.mean(np.square(np.diff(rr_intervals)))) if rr_intervals.size > 1 else 0  
        pnn50 = np.sum(np.abs(np.diff(rr_intervals)) > 0.05) / len(rr_intervals) * 100 if rr_intervals.size > 0 else 0  

        # Calcular rango y bits de resolución
        Vmax = np.max(datos)
        Vmin = np.min(datos)
        q = (Vmax - Vmin) / (2 ** num_bits)  # Tamaño de paso de cuantificación
        bits_resolucion = np.log2((Vmax - Vmin) / q) if (Vmax - Vmin) != 0 else 0

        # Imprimir estadísticas en la consola
        print(f"Frecuencia de muestreo: {fs} Hz")
        print(f"Tiempo total de muestreo: {tiempo_total:.2f} s")
        print(f"Media: {media:.2f} mV")
        print(f"{tipo_varianza}: {varianza:.2f} (mV)^2")
        print(f"Desviación Estándar: {desviacion_estandar:.2f} mV")
        print(f"Mediana: {mediana:.2f} mV")
        print(f"Frecuencia Cardíaca: {frecuencia_cardiaca:.2f} latidos/min")
        print(f"SDNN: {sdnn:.2f} s")
        print(f"RMSSD: {rmssd:.2f} s")
        print(f"pNN50: {pnn50:.2f}%")
        print(f"Bits de Resolución: {bits_resolucion:.2f} bits")

        # Convertir el eje x de muestras a tiempo (en minutos)
        tiempo = np.arange(len(datos)) / fs / 60  # Escala en minutos

        # Graficar la señal completa en una figura separada con estadísticas
        plt.figure(figsize=(12, 6))
        plt.plot(tiempo, datos, color='purple', linewidth=0.5, label="Señal ECG")
        plt.grid(True)
        plt.ylabel("Amplitud (mV)")
        plt.xlabel("Tiempo (minutos)")
        plt.title("Señal Completa")

        # Mostrar estadísticas en la parte inferior del gráfico
        plt.text(0.01, 0.02, f"Frecuencia de muestreo: {fs} Hz", transform=plt.gca().transAxes)
        plt.text(0.01, 0.07, f"Tiempo total de muestreo: {tiempo_total:.2f} s", transform=plt.gca().transAxes)
        plt.text(0.01, 0.12, f"Media: {media:.2f} mV", transform=plt.gca().transAxes)
        plt.legend()
        plt.show()

        # Graficar la señal en subgráficos
        plt.figure(figsize=(20, 10))
        segment_length = len(datos) // n_subplots
        for i in range(n_subplots):
            plt.subplot(n_subplots, 1, i + 1)
            plt.plot(tiempo[i * segment_length : (i + 1) * segment_length],
                     datos[i * segment_length : (i + 1) * segment_length],
                     color='blue', linewidth=0.5, label="Señal ECG")
            plt.grid(True)
            plt.ylabel("Amplitud (mV)")
            if i == n_subplots - 1:
                plt.xlabel("Tiempo (minutos)")
            if i == 0:
                plt.title("Señal ECG - 5 Minutos Completa (Dividida en Subgráficos)")
            plt.legend()
        plt.tight_layout()
        plt.show()

        # Aplicar filtro
        lowcut = 0.5
        highcut = 40.0
        valores_filtrados = aplicar_filtro(datos, lowcut, highcut, fs)

        # Aplicar transformada wavelet y graficar el espectrograma
        cwt_matrix, freqs = aplicar_transformada_wavelet(datos, fs)

        # Calcular potencias LF y HF
        potencia_LF, potencia_HF = calcular_potencias_bandap(cwt_matrix, freqs)

        # Imprimir resultados
        print(f"Potencia LF: {potencia_LF:.2f}")
        print(f"Potencia HF: {potencia_HF:.2f}")
        print(f"Relación LF/HF: {potencia_LF / potencia_HF:.2f}" if potencia_HF > 0 else "Relación LF/HF: Infinito")

    except Exception as e:
        print(f"Ocurrió un error: {e}")


archivo = seleccionar_archivo()
graficar_senal(archivo)

