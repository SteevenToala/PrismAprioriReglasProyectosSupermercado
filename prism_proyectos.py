# Algoritmo PRISM - Dataset Proyectos de Software
# Induccion modular de reglas (J. Cendrowska, 1987)
# Hecho paso a paso para la clase de Inteligencia Artificial

import csv

# 1. CARGAR EL DATASET
archivo = open("dataset/dataset_prism_proyectos_software.csv", "r", encoding="utf-8")
lector = csv.reader(archivo)

encabezado = next(lector)
# Columnas: Proyecto_ID, Tamano_Equipo, Metodologia, Presupuesto, Experiencia_Lider, Exito_Proyecto
atributos = ["Tamano_Equipo", "Metodologia", "Presupuesto", "Experiencia_Lider"]

datos = []
for fila in lector:
    fila_dict = {
        "Tamano_Equipo": fila[1],
        "Metodologia": fila[2],
        "Presupuesto": fila[3],
        "Experiencia_Lider": fila[4],
        "Exito_Proyecto": fila[5]
    }
    datos.append(fila_dict)

archivo.close()

print("==================================================")
print("ALGORITMO PRISM - PROYECTOS DE SOFTWARE")
print("Total de registros:", len(datos))
print("Atributo objetivo: Exito_Proyecto (Valores: 'Si', 'No')")
print("==================================================")

# 2. FUNCION AUXILIAR PARA VER SI UNA FILA CUMPLE LA REGLA
def cumple_regla(fila, condiciones):
    for attr, val in condiciones:
        if fila[attr] != val:
            return False
    return True

# 3. EJECUTAR PRISM PARA CADA CLASE
clases = ["No", "Si"]

for clase in clases:
    print("\n--------------------------------------------------")
    print("REGLAS INDUCIDAS PARA: Exito_Proyecto =", clase)
    print("--------------------------------------------------")
    
    # Copiamos todos los datos para ir cubriendo instancias
    datos_restantes = list(datos)
    num_regla = 1
    
    # Mientras queden filas de esta clase sin cubrir
    quedan_filas = True
    while quedan_filas:
        # Verificamos si aun hay instancias de la clase
        contador_clase = 0
        for fila in datos_restantes:
            if fila["Exito_Proyecto"] == clase:
                contador_clase = contador_clase + 1
        if contador_clase == 0:
            break
            
        # S es el subconjunto de trabajo actual
        S = list(datos_restantes)
        regla_condiciones = []
        atributos_disponibles = list(atributos)
        
        # Bucle para ir agregando condiciones a la regla
        while len(atributos_disponibles) > 0:
            mejor_attr = None
            mejor_val = None
            mejor_prob = -1.0
            mejor_aciertos = -1
            
            # Evaluamos cada par (Atributo = Valor) disponible
            for attr in atributos_disponibles:
                # Sacamos los valores unicos de este atributo en S
                valores_unicos = []
                for fila in S:
                    if fila[attr] not in valores_unicos:
                        valores_unicos.append(fila[attr])
                        
                for val in valores_unicos:
                    total = 0
                    aciertos = 0
                    for fila in S:
                        if fila[attr] == val:
                            total = total + 1
                            if fila["Exito_Proyecto"] == clase:
                                aciertos = aciertos + 1
                                
                    if total > 0:
                        prob = aciertos / total
                        # Elegimos la mayor probabilidad p/t (desempate por aciertos)
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
                
            # Agregamos la mejor condicion a la regla
            regla_condiciones.append((mejor_attr, mejor_val))
            atributos_disponibles.remove(mejor_attr)
            
            # Filtramos S para quedarnos solo con las filas que cumplen la condicion
            nuevo_S = []
            for fila in S:
                if fila[mejor_attr] == mejor_val:
                    nuevo_S.append(fila)
            S = nuevo_S
            
            # Si todas las filas en S pertenecen a la clase, la regla es 100% pura
            todos_son_clase = True
            for fila in S:
                if fila["Exito_Proyecto"] != clase:
                    todos_son_clase = False
                    break
            if todos_son_clase:
                break
                
        # Calculamos la precision de la regla sobre los datos completos
        aciertos_totales = 0
        cubiertos_totales = 0
        for fila in datos:
            if cumple_regla(fila, regla_condiciones):
                cubiertos_totales = cubiertos_totales + 1
                if fila["Exito_Proyecto"] == clase:
                    aciertos_totales = aciertos_totales + 1
                    
        precision = aciertos_totales / cubiertos_totales if cubiertos_totales > 0 else 0
        
        # Mostramos las primeras reglas principales
        if num_regla <= 6:
            conds_texto = []
            for attr, val in regla_condiciones:
                conds_texto.append(attr + " = '" + val + "'")
            texto_regla = " Y ".join(conds_texto)
            print("Regla " + str(num_regla) + ": SI " + texto_regla + " ENTONCES Exito_Proyecto = " + clase)
            print("   Precision:", round(precision * 100, 2), "% (" + str(aciertos_totales) + "/" + str(cubiertos_totales) + " casos)")
            
        # Eliminamos de datos_restantes las filas cubiertas que pertenecen a esta clase
        nuevos_restantes = []
        for fila in datos_restantes:
            if cumple_regla(fila, regla_condiciones) and fila["Exito_Proyecto"] == clase:
                continue  # Se elimina
            nuevos_restantes.append(fila)
        datos_restantes = nuevos_restantes
        
        num_regla = num_regla + 1

    print("Total de reglas generadas para clase " + clase + ": " + str(num_regla - 1))
