import time
import os
from ruta import *
from config import *
from utils import *
import json

if __name__ == "__main__":
    ser = conexion_bt(puerto_serial, baud_rate)
    if(ser == None):
        print(f"No se pudo abrir el puerto serial")
        exit()
    else:
        ruta = Ruta()
        print(f"Conectado al puerto {puerto_serial} a {baud_rate} baudios.")
        try:
            while True:
                # Leer una línea del puerto serial
                linea = ser.readline().decode('utf-8').strip()
                
                # Procesar la cadena recibida si no está vacía
                print(f"Linea: {linea}")
                if linea:
                    data, linea_ruta = procesar_cadena(linea)
                    print(data)
                    print(linea_ruta)
                    if(data != None and linea_ruta != None):
                        if len(data) > 0:
                            #print(f"Temperatura: {data["Temperatura"]}°C")
                            print("Temperatura:" +  str(data["Temperatura"]) + "°C")
                            print("Humedad:" + str(data["Humedad"]) +"%")
                            print(f"Gas:" + str(data["Gas"]) +"ppm")
                            print(f"Distancia:" + str(data["Distancia"]) +"cm")
                            if(data["Gas"] >= 2000 and data["Gas"] <= 5000):
                                ruta.marcar(Marca.G_M)
                            if(data["Gas"] > 5000):
                                ruta.marcar(Marca.G_A)
                            if(data["Temperatura"] >= 30 and data["Temperatura"] <= 35):
                                ruta.marcar(Marca.T_M)
                            if(data["Temperatura"] > 35):
                                ruta.marcar(Marca.T_A)
                            with open('data/sensores.json', 'w') as file:
                                json.dump(data, file, indent=4)
                            #os.system("cls")
                        else:
                            print("La cadena no contiene datos de los sensores")

                        if len(linea_ruta) > 0:
                            ruta.print_mapa()
                            ruta.marcar(linea_ruta[1], ruta.posX + linea_ruta[0][0], ruta.posY + linea_ruta[0][1])
                            if (linea_ruta[1] == Marca.C):
                                ruta.mover(linea_ruta[0])
                            else:
                                ruta_destino = ruta.ruta_casilla_cercana()

                                # Si no encuentra la próxima ruta más cercana
                                if ruta_destino == None:
                                    centro = (ruta.dimension // 2, ruta.dimension // 2)
                                    ruta_destino = ruta.A_star(centro[0], centro[1], objetivo="volver")
                                
                                #Si existe ruta para volver o explorar
                                if ruta_destino != None:
                                    direcciones = []
                                    for i in range(len(ruta_destino)-1):
                                        vector_dir_x = ruta_destino[i][0] - ruta_destino[i+1][0]
                                        vector_dir_y = ruta_destino[i][1] - ruta_destino[i+1][1]
                                        if (vector_dir_x,vector_dir_y) == Direcciones.U.value:
                                            if ruta.dir == Direcciones.D:
                                                direcciones.append("I")
                                                direcciones.append("I")
                                            elif ruta.dir == Direcciones.R:
                                                direcciones.append("I")
                                            else:
                                                direcciones.append("D")

                                        elif (vector_dir_x,vector_dir_y) == Direcciones.R.value:
                                            if ruta.dir == Direcciones.L:
                                                direcciones.append("I")
                                                direcciones.append("I")
                                            elif ruta.dir == Direcciones.U:
                                                direcciones.append("D")
                                            else:
                                                direcciones.append("I")
                                        elif (vector_dir_x,vector_dir_y) == Direcciones.D.value:
                                            if ruta.dir == Direcciones.U:
                                                direcciones.append("I")
                                                direcciones.append("I")
                                            elif ruta.dir == Direcciones.R:
                                                direcciones.append("I")
                                            else:
                                                direcciones.append("D")
                                        elif (vector_dir_x,vector_dir_y) == Direcciones.L.value:
                                            if ruta.dir == Direcciones.R:
                                                direcciones.append("I")
                                                direcciones.append("I")
                                            elif ruta.dir == Direcciones.D:
                                                direcciones.append("D")
                                            else:
                                                direcciones.append("I")

                                        if (i != len(ruta_destino)-2):
                                            direcciones.append("A")

                                    cadena_ruta = "<"
                                    for i in range(len(direcciones)):
                                        cadena_ruta += direcciones[i]
                                        if (i != len(direcciones)-1):
                                            cadena_ruta += ","
                                        else:
                                            cadena_ruta += ">\n"
                                    ser.write(cadena_ruta.encode('utf-8'))
                            mapa = ruta.cargar_mapa()
                            with open('data/mapa.json', 'w') as file:
                                json.dump(mapa, file, indent=4)
                        else:
                            print("La cadena no contiene datos sobre la ruta")
                        
                    else:
                        print("Cadena de datos no válida")
                else:
                    print("No se recibieron datos.")

                time.sleep(0.1 *10)  # Esperar 1 segundo antes de la siguiente lectura

        except KeyboardInterrupt:
            print("Interrupción del usuario.")

        finally:
            # Cerrar el puerto serial al interrumpir el programa
            ser.close()
            print("Puerto serial cerrado")
