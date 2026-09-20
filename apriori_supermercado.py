# Algoritmo Apriori - Dataset Supermercado
# Hecho paso a paso para la clase de Inteligencia Artificial

import csv

# 1. CARGAR LAS TRANSACCIONES
archivo = open("dataset/dataset_apriori_supermercado.csv", "r", encoding="utf-8")
lector = csv.reader(archivo)

# La primera fila son los nombres de las columnas
encabezado = next(lector)
productos = encabezado[1:]  # Quitamos Transaccion_ID

transacciones = []
for fila in lector:
    compra = []
    # Revisamos cada columna de producto
    for i in range(1, len(fila)):
        if fila[i] == "1":
            compra.append(encabezado[i])
    if len(compra) > 0:
        transacciones.append(compra)

archivo.close()

total_transacciones = len(transacciones)
min_soporte = 0.15     # 15% de soporte minimo
min_confianza = 0.60   # 60% de confianza minima

print("==================================================")
print("ALGORITMO APRIORI - SUPERMERCADO")
print("Total de transacciones:", total_transacciones)
print("Soporte minimo:", min_soporte * 100, "%")
print("Confianza minima:", min_confianza * 100, "%")
print("==================================================")

# 2. PASO 1: CALCULAR C1 Y FILTRAR L1 (Items individuales)
conteo_individual = {}
for p in productos:
    conteo_individual[p] = 0

for t in transacciones:
    for item in t:
        conteo_individual[item] = conteo_individual[item] + 1

soporte_individual = {}
l1 = []

print("\n--- PASO 1: Items Frecuentes (L1) ---")
for item in productos:
    sop = conteo_individual[item] / total_transacciones
    soporte_individual[item] = sop
    if sop >= min_soporte:
        l1.append(item)
        print(item, ":", conteo_individual[item], "veces - Soporte:", round(sop * 100, 2), "%")

# 3. PASO 2: GENERAR PARES (C2) Y FILTRAR L2
pares_candidatos = []
for i in range(len(l1)):
    for j in range(i + 1, len(l1)):
        pares_candidatos.append((l1[i], l1[j]))

l2 = []
soporte_pares = {}

print("\n--- PASO 2: Pares Frecuentes (L2) ---")
for par in pares_candidatos:
    item1 = par[0]
    item2 = par[1]
    
    # Contamos cuantas transacciones tienen ambos productos
    conteo = 0
    for t in transacciones:
        if (item1 in t) and (item2 in t):
            conteo = conteo + 1
            
    sop = conteo / total_transacciones
    if sop >= min_soporte:
        l2.append(par)
        soporte_pares[par] = sop
        # Tambien guardamos en orden inverso para buscar facil
        soporte_pares[(item2, item1)] = sop
        print("{" + item1 + ", " + item2 + "} :", conteo, "veces - Soporte:", round(sop * 100, 2), "%")

# 4. PASO 3: GENERAR TRIOS (C3) Y FILTRAR L3 (con poda Apriori)
trios_candidatos = []
for i in range(len(l1)):
    for j in range(i + 1, len(l1)):
        for k in range(j + 1, len(l1)):
            trio = (l1[i], l1[j], l1[k])
            
            # Poda Apriori: los 3 pares deben estar en L2
            par1 = (trio[0], trio[1])
            par2 = (trio[0], trio[2])
            par3 = (trio[1], trio[2])
            
            if (par1 in l2 or (par1[1], par1[0]) in l2) and \
               (par2 in l2 or (par2[1], par2[0]) in l2) and \
               (par3 in l2 or (par3[1], par3[0]) in l2):
                trios_candidatos.append(trio)

l3 = []
soporte_trios = {}

print("\n--- PASO 3: Trios Frecuentes (L3) ---")
for trio in trios_candidatos:
    conteo = 0
    for t in transacciones:
        if (trio[0] in t) and (trio[1] in t) and (trio[2] in t):
            conteo = conteo + 1
            
    sop = conteo / total_transacciones
    if sop >= min_soporte:
        l3.append(trio)
        soporte_trios[trio] = sop
        print("{" + trio[0] + ", " + trio[1] + ", " + trio[2] + "} :", conteo, "veces - Soporte:", round(sop * 100, 2), "%")

# 5. GENERAR REGLAS DE ASOCIACION
print("\n==================================================")
print("REGLAS DE ASOCIACION (Confianza >= 60%)")
print("==================================================")

reglas_encontradas = []

# Reglas a partir de pares (A -> B y B -> A)
for par in l2:
    a = par[0]
    b = par[1]
    sop_union = soporte_pares[par]
    
    # Regla: SI a ENTONCES b
    conf_a_b = sop_union / soporte_individual[a]
    lift_a_b = conf_a_b / soporte_individual[b]
    if conf_a_b >= min_confianza:
        reglas_encontradas.append(( "{" + a + "} -> {" + b + "}", sop_union, conf_a_b, lift_a_b ))
        
    # Regla: SI b ENTONCES a
    conf_b_a = sop_union / soporte_individual[b]
    lift_b_a = conf_b_a / soporte_individual[a]
    if conf_b_a >= min_confianza:
        reglas_encontradas.append(( "{" + b + "} -> {" + a + "}", sop_union, conf_b_a, lift_b_a ))

# Reglas a partir de trios ({A, B} -> C)
for trio in l3:
    sop_trio = soporte_trios[trio]
    
    # Combinaciones posibles de 2 items hacia 1 item
    combos = [
        ((trio[0], trio[1]), trio[2]),
        ((trio[0], trio[2]), trio[1]),
        ((trio[1], trio[2]), trio[0])
    ]
    
    for antecedente, consecuente in combos:
        sop_ant = soporte_pares[antecedente]
        conf = sop_trio / sop_ant
        lift = conf / soporte_individual[consecuente]
        if conf >= min_confianza:
            ant_str = "{" + antecedente[0] + ", " + antecedente[1] + "}"
            cons_str = "{" + consecuente + "}"
            reglas_encontradas.append(( ant_str + " -> " + cons_str, sop_trio, conf, lift ))

# Mostramos las reglas ordenadas de forma sencilla
numero = 1
for regla, sop, conf, lift in reglas_encontradas:
    print(str(numero) + ". SI " + regla)
    print("   Soporte:", round(sop * 100, 2), "% | Confianza:", round(conf * 100, 2), "% | Lift:", round(lift, 2))
    numero = numero + 1
