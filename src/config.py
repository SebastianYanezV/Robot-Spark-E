import serial

# Configuración del puerto serial
puerto_serial = 'COM6'
baud_rate = 9600

def conexion_bt(puerto_serial, baud_rate):
    try:
        # Inicializar el puerto serial con un tiempo de espera de 1 segundo
        ser = serial.Serial(puerto_serial, baud_rate, timeout=1)
        return ser
    except serial.SerialException as e:
        return None