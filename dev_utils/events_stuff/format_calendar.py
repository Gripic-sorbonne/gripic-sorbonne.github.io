import pandas as pd

# 1. Cargar el archivo actual y el original de referencia
df_curr = pd.read_csv('calendar.csv', sep=';')
df_orig = pd.read_csv('calendar_orig.csv', sep=';')

# 2. Crear un DataFrame nuevo con la estructura exacta de columnas original
df_mapped = pd.DataFrame(columns=df_orig.columns)

# 3. Asignar los valores disponibles que extrajimos
df_mapped['Séquentiel'] = range(1, len(df_curr) + 1)
df_mapped['Titre'] = df_curr['Titre']
df_mapped['Date'] = df_curr['Date']
df_mapped['Organisateur(s)'] = df_curr['Organisateur(s)']
df_mapped['Descriptif'] = df_curr['Descriptif']
df_mapped['Photo'] = df_curr['Photo']

# 4. Rellenar las columnas faltantes con valores vacíos para que no rompa el script de Gatsby
df_mapped['Lieu'] = ""
df_mapped['Catégorie'] = "Événement"
df_mapped['Contact'] = ""
df_mapped['Date de début de publication'] = ""
df_mapped["Date d'archivage"] = ""
df_mapped['Url associé.e'] = ""
df_mapped['Nom'] = ""

# 5. Sobrescribir calendar.csv con el formato completo original
df_mapped.to_csv('calendar.csv', sep=';', index=False)

print(f"¡Listo! Se han mapeado {len(df_mapped)} registros al formato de 13 columnas original sin riesgos de bucle.")