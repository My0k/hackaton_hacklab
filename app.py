from flask import Flask, render_template, send_from_directory, request
import os
import csv

app = Flask(__name__)

def load_products():
    products = []
    try:
        with open('products.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Convertir las categorías a una lista
                if 'categorias' in row:
                    row['categorias_lista'] = [cat.strip() for cat in row['categorias'].split('|')] if row['categorias'] else []
                products.append(row)
        return products
    except Exception as e:
        print(f"Error loading products: {e}")
        return []

def get_all_categories(products):
    # Extraer todas las categorías únicas de los productos
    categories = set()
    for product in products:
        if 'categorias_lista' in product:
            for category in product['categorias_lista']:
                categories.add(category)
    return sorted(list(categories))

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/marketplace')
def marketplace():
    # Obtener el filtro seleccionado de los parámetros de consulta
    selected_category = request.args.get('categoria', '')
    
    # Cargar todos los productos
    all_products = load_products()
    
    # Obtener todas las categorías únicas para los filtros
    all_categories = get_all_categories(all_products)
    
    # Filtrar productos si se seleccionó una categoría
    if selected_category:
        filtered_products = [p for p in all_products if 'categorias_lista' in p and selected_category in p['categorias_lista']]
    else:
        filtered_products = all_products
    
    return render_template('marketplace.html', 
                          products=filtered_products, 
                          categories=all_categories,
                          selected_category=selected_category)

@app.route('/debug')
def debug():
    # Información de depuración
    info = {
        "templates_folder": app.template_folder,
        "static_folder": app.static_folder,
        "root_path": app.root_path,
        "templates_exist": os.path.exists(os.path.join(app.root_path, 'templates')),
        "index_exists": os.path.exists(os.path.join(app.root_path, 'templates', 'index.html'))
    }
    return str(info)

@app.route('/health')
def health():
    return "OK", 200

# Ruta específica para la verificación de salud de CapRover
@app.route('/.well-known/captain-identifier')
def captain_health_check():
    return "OK", 200

# Permitir servir archivos directamente desde la carpeta .well-known
@app.route('/.well-known/<path:filename>')
def wellknown(filename):
    return send_from_directory(os.path.join(app.root_path, '.well-known'), filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 