# Algoritmo Apriori - Dataset Proyectos de Software
# Hecho paso a paso para la clase de Inteligencia Artificial

import csv

# 1. CARGAR LOS DATOS
archivo = open("dataset/dataset_prism_proyectos_software.csv", "r", encoding="utf-8")
lector = csv.reader(archivo)

encabezado = next(lector)
atributos = encabezado[1:]  # Quitamos Proyecto_ID

transacciones = []
for fila in lector:
    proyecto = []
    for i in range(1, len(fila)):
        # Guardamos en formato Atributo=Valor
        proyecto.append(encabezado[i] + "=" + fila[i])
    transacciones.append(proyecto)

archivo.close()

total_proyectos = len(transacciones)
min_soporte = 0.15     # 15% de soporte minimo
min_confianza = 0.60   # 60% de confianza minima

print("==================================================")
print("ALGORITMO APRIORI - PROYECTOS DE SOFTWARE")
print("Total de proyectos:", total_proyectos)
print("Soporte minimo:", min_soporte * 100, "%")
print("Confianza minima:", min_confianza * 100, "%")
print("==================================================")

# 2. PASO 1: CONTAR ITEMS INDIVIDUALES (L1)
conteo_individual = {}
for t in transacciones:
    for item in t:
        if item not in conteo_individual:
            conteo_individual[item] = 0
        conteo_individual[item] = conteo_individual[item] + 1

soporte_individual = {}
l1 = []

print("\n--- PASO 1: Items Frecuentes (L1) ---")
for item in conteo_individual:
    sop = conteo_individual[item] / total_proyectos
    soporte_individual[item] = sop
    if sop >= min_soporte:
        l1.append(item)
        print(item, ":", conteo_individual[item], "veces - Soporte:", round(sop * 100, 2), "%")

# 3. PASO 2: COMBINAR EN PARES (L2)
l2 = []
soporte_pares = {}

print("\n--- PASO 2: Pares Frecuentes (L2) ---")
for i in range(len(l1)):
    for j in range(i + 1, len(l1)):
        item1 = l1[i]
        item2 = l1[j]
        
        # Dos valores del mismo atributo no pueden ir juntos en un proyecto
        # Ej: no puede ser Tamano_Equipo=Grande y Tamano_Equipo=Pequeno a la vez
        attr1 = item1.split("=")[0]
        attr2 = item2.split("=")[0]
        if attr1 == attr2:
            continue
            
        conteo = 0
        for t in transacciones:
            if (item1 in t) and (item2 in t):
                conteo = conteo + 1
                
        sop = conteo / total_proyectos
        if sop >= min_soporte:
            l2.append((item1, item2))
            soporte_pares[(item1, item2)] = sop
            soporte_pares[(item2, item1)] = sop
            print("{" + item1 + ", " + item2 + "} :", conteo, "veces - Soporte:", round(sop * 100, 2), "%")

# 4. GENERAR REGLAS DE ASOCIACION HACIA Exito_Proyecto
print("\n==================================================")
print("REGLAS PARA PREDECIR Exito_Proyecto (Confianza >= 60%)")
print("==================================================")

numero = 1
for par in l2:
    item1 = par[0]
    item2 = par[1]
    sop_union = soporte_pares[par]
    
    # Caso 1: item1 -> item2 (donde item2 sea el Exito_Proyecto)
    if "Exito_Proyecto" in item2:
        conf = sop_union / soporte_individual[item1]
        lift = conf / soporte_individual[item2]
        if conf >= min_confianza:
            print(str(numero) + ". SI {" + item1 + "} -> {" + item2 + "}")
            print("   Soporte:", round(sop_union * 100, 2), "% | Confianza:", round(conf * 100, 2), "% | Lift:", round(lift, 2))
            numero = numero + 1

    # Caso 2: item2 -> item1 (donde item1 sea el Exito_Proyecto)
    if "Exito_Proyecto" in item1:
        conf = sop_union / soporte_individual[item2]
        lift = conf / soporte_individual[item1]
        if conf >= min_confianza:
            print(str(numero) + ". SI {" + item2 + "} -> {" + item1 + "}")
            print("   Soporte:", round(sop_union * 100, 2), "% | Confianza:", round(conf * 100, 2), "% | Lift:", round(lift, 2))
            numero = numero + 1
