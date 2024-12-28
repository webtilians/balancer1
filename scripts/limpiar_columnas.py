import csv

# Archivo de entrada
ruta_csv_original = "datos_entrenamiento.csv"
# Archivo de salida limpio
ruta_csv_limpio = "datos_simulacion_limpio2.csv"

with open(ruta_csv_original, 'r', newline='', encoding='utf-8') as infile, \
     open(ruta_csv_limpio, 'w', newline='', encoding='utf-8') as outfile:
    
    reader = csv.reader(infile)
    writer = csv.writer(outfile)
    
    # Leer las cabeceras
    cabeceras = next(reader)
    writer.writerow(cabeceras)  # Escribir las cabeceras en el archivo limpio
    
    # Determinar la cantidad correcta de columnas
    columnas_correctas = len(cabeceras)
    
    for fila in reader:
        # Solo escribir las filas que coincidan con el número correcto de columnas
        fila_limpia = fila[:columnas_correctas]  # Recorta columnas adicionales
        writer.writerow(fila_limpia)

print(f"Archivo limpio guardado correctamente en: {ruta_csv_limpio}")
