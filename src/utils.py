from enum import Enum

# Declaración de las direcciones del robot
class Direcciones(Enum):
    U = ( 1, 0)
    R = ( 0,-1)
    D = (-1, 0)
    L = ( 0, 1)

# Declaración de las marcas en el mapa
class Marca(Enum):
    D = "D"#"Desconocido" 
    C = "C"#"Conocido"
    O = "O"#"Obstáculo"
    T_A = "T_A"#"Temperatura Alta"
    T_M = "T_M"#"Temperatura Media"
    G_A = "G_A"#"Gases noscivos Altos"
    G_M = "G_M"#"Gases noscivos Medios"

def procesar_cadena(cadena):
    # Asegúrate de que la cadena comienza con '<' y termina con '>'
    if cadena.startswith('<') and cadena.endswith('>'):
        # Eliminar los caracteres de inicio y fin
        cadena = cadena[1:-1]
        
        # Dividir la cadena por comas
        lista_data = cadena.split(',')
        
        # Inicializar variables
        data = {}
        ruta = []
        
        if 'R' in lista_data:
            if int(lista_data[1]) == 0:
                ruta.append(Direcciones.U.value)
            elif int(lista_data[1]) == 1:
                ruta.append(Direcciones.R.value)
            elif int(lista_data[1]) == 2:
                ruta.append(Direcciones.D.value)
            elif int(lista_data[1]) == 3:
                ruta.append(Direcciones.L.value)

            if lista_data[2] == 'C':
                ruta.append(Marca.C)
            elif lista_data[2] == 'O':
                ruta.append(Marca.O)
            elif lista_data[2] == 'T_A':
                ruta.append(Marca.T_A)
            elif lista_data[2] == 'T_M':
                ruta.append(Marca.T_M)
            elif lista_data[2] == 'G_A':
                ruta.append(Marca.G_A)
            elif lista_data[2] == 'G_M':
                ruta.append(Marca.G_M)

        else:
            # Iterar sobre los datos y extraer los valores
            for i in range(0, len(lista_data), 2):
                if lista_data[i] == 'T':
                    data["Temperatura"] = float(lista_data[i+1])
                elif lista_data[i] == 'H':
                    data["Humedad"] = float(lista_data[i+1])
                elif lista_data[i] == 'G':
                    data["Gas"] = int(lista_data[i+1])
                elif lista_data[i] == 'D':
                    data["Distancia"] = float(lista_data[i+1])
        
        return data, ruta
    else:
        return None, None