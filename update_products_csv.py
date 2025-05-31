import csv
import os

def fix_products_csv():
    """
    Corrige el formato del archivo products.csv para asegurar que las imágenes se muestren correctamente.
    """
    # Verificar si existe el archivo
    if not os.path.exists('products.csv'):
        print("El archivo products.csv no existe.")
        return
    
    # Leer el archivo actual
    rows = []
    with open('products.csv', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames
        for row in reader:
            # Corregir la estructura del CSV
            if 'imagen_url' in row:
                # Limpiar la ruta de la imagen
                img_path = row['imagen_url']
                
                # Quitar rutas incorrectas
                if img_path.startswith('/static/fotos/'):
                    img_path = img_path.replace('/static/fotos/', '')
                elif img_path.startswith('static/fotos/'):
                    img_path = img_path.replace('static/fotos/', '')
                
                # Corrección especial para nombres erróneos
                if '|' in img_path:
                    # Este es un error grave - la categoría se mezcló con la imagen
                    # Vamos a intentar recuperar el nombre correcto
                    if row['sku'] == '001':
                        img_path = 'fardo.png'
                    elif row['sku'] == '003':
                        img_path = 'madera.png'
                    elif row['sku'] == '004':
                        img_path = 'bici.png'
                    elif row['sku'] == '005':
                        img_path = 'computador.png'
                    elif row['sku'] == '006':
                        img_path = 'ventana.png'
                    elif row['sku'] == '007':
                        img_path = 'tv.png'
                    elif row['sku'] == '008':
                        img_path = 'silla.png'
                    elif row['sku'] == '009':
                        img_path = 'lavadora.png'
                
                row['imagen_url'] = img_path
            
            rows.append(row)
    
    # Escribir el archivo corregido
    with open('products.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"Se corrigieron {len(rows)} registros en products.csv")

if __name__ == "__main__":
    fix_products_csv() 