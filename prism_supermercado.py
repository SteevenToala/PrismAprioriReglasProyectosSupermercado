# Algoritmo PRISM - Dataset Supermercado
# Induccion modular de reglas (J. Cendrowska, 1987)
# Clasificar si un cliente compra 'Leche' (1 o 0)
# Hecho paso a paso para la clase de Inteligencia Artificial

import csv

# 1. CARGAR EL DATASET
archivo = open("dataset/dataset_apriori_supermercado.csv", "r", encoding="utf-8")
lector = csv.reader(archivo)

encabezado = next(lector)
# Columnas: Transaccion_ID, Leche, Pan, Huevos, Mantequilla, Queso, Cafe, Azucar, Galletas, Jugo, Cereal
columna_objetivo = "Leche"

# Los atributos son todos los demas productos
atributos = []
for col in encabezado:
    if col != "Transaccion_ID" and col != columna_objetivo:
        atributos.append(col)

datos = []
for fila in lector:
    fila_dict = {}
    for i in range(len(encabezado)):
        col = encabezado[i]
        fila_dict[col] = fila[i]
    datos.append(fila_dict)

archivo.close()

print("==================================================")
print("ALGORITMO PRISM - SUPERMERCADO")
print("Total de transacciones:", len(datos))
print("Objetivo a clasificar:", columna_objetivo, "(1 = Compra, 0 = No compra)")
print("==================================================")

# 2. FUNCION AUXILIAR PARA VER SI UNA FILA CUMPLE LA REGLA
def cumple_regla(fila, condiciones):
    for attr, val in condiciones:
        if fila[attr] != val:
            return False
    return True

# 3. EJECUTAR PRISM PARA CADA VALOR (0 y 1)
clases = ["0", "1"]

for clase in clases:
    etiqueta = "Compra Leche (1)" if clase == "1" else "NO Compra Leche (0)"
    print("\n--------------------------------------------------")
    print("REGLAS INDUCIDAS PARA:", etiqueta)
    print("--------------------------------------------------")
    
    datos_restantes = list(datos)
    num_regla = 1
    
    while True:
        # Contamos cuantas filas de esta clase quedan sin cubrir
        contador_clase = 0
        for fila in datos_restantes:
            if fila[columna_objetivo] == clase:
                contador_clase = contador_clase + 1
        if contador_clase == 0:
            break
            
        S = list(datos_restantes)
        regla_condiciones = []
        atributos_disponibles = list(atributos)
        
        while len(atributos_disponibles) > 0:
            mejor_attr = None
            mejor_val = None
            mejor_prob = -1.0
            mejor_aciertos = -1
            
            for attr in atributos_disponibles:
                # Cada producto solo puede tener valor '1' o '0'
                for val in ["1", "0"]:
                    total = 0
                    aciertos = 0
                    for fila in S:
                        if fila[attr] == val:
                            total = total + 1
                            if fila[columna_objetivo] == clase:
                                aciertos = aciertos + 1
                                
                    if total > 0:
                        prob = aciertos / total
                        if prob > mejor_prob:
                            mejor_prob = prob
                            mejor_aciertos = aciertos
                            mejor_attr = attr
                            mejor_val = val
                        elif prob == mejor_prob and aciertos > mejor_aciertos:
                            mejor_prob = prob
                            mejor_aciertos = aciertos
                            mejor_attr = attr
                            mejor_val = val
                            
            if mejor_attr is None or mejor_aciertos == 0:
                break
                
            regla_condiciones.append((mejor_attr, mejor_val))
            atributos_disponibles.remove(mejor_attr)
            
            # Filtramos S
            nuevo_S = []
            for fila in S:
                if fila[mejor_attr] == mejor_val:
                    nuevo_S.append(fila)
            S = nuevo_S
            
            # Si todas las filas en S pertenecen a la clase, terminamos
            todos_son_clase = True
            for fila in S:
                if fila[columna_objetivo] != clase:
                    todos_son_clase = False
                    break
            if todos_son_clase:
                break
                
        # Evaluamos sobre los datos totales
        aciertos_totales = 0
        cubiertos_totales = 0
        for fila in datos:
            if cumple_regla(fila, regla_condiciones):
                cubiertos_totales = cubiertos_totales + 1
                if fila[columna_objetivo] == clase:
                    aciertos_totales = aciertos_totales + 1
                    
        precision = aciertos_totales / cubiertos_totales if cubiertos_totales > 0 else 0
        
        # Mostramos las primeras 5 reglas principales
        if num_regla <= 5:
            conds_texto = []
            for attr, val in regla_condiciones:
                conds_texto.append(attr + " = " + val)
            texto_regla = " Y ".join(conds_texto)
            print("Regla " + str(num_regla) + ": SI " + texto_regla + " ENTONCES " + columna_objetivo + " = " + clase)
            print("   Precision:", round(precision * 100, 2), "% (" + str(aciertos_totales) + "/" + str(cubiertos_totales) + " casos)")
            
        # Eliminamos filas cubiertas de esta clase
        nuevos_restantes = []
        for fila in datos_restantes:
            if cumple_regla(fila, regla_condiciones) and fila[columna_objetivo] == clase:
                continue
            nuevos_restantes.append(fila)
        datos_restantes = nuevos_restantes
        
        num_regla = num_regla + 1

    print("Total de reglas generadas para clase " + clase + ": " + str(num_regla - 1))
