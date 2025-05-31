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

@app.route('/materiales')
def materiales():
    return render_template('materiales.html')

@app.route('/receptor/<receptor>')
def vista_receptor(receptor):
    # Cargar todos los productos
    all_products = load_products()
    
    # Filtrar productos por receptor (descartador)
    receptor_products = [p for p in all_products if p['descartador'].lower() == receptor.lower()]
    
    # Obtener todas las categorías únicas para los filtros
    all_categories = get_all_categories(all_products)
    
    # Obtener lista de receptores únicos para la navegación
    all_receptors = sorted(list(set([p['descartador'] for p in all_products])))
    
    return render_template('receptor.html', 
                          products=receptor_products, 
                          categories=all_categories,
                          receptor_name=receptor,
                          all_receptors=all_receptors)

@app.route('/receptores')
@app.route('/receptores/<categoria>')
def receptores(categoria=None):
    # Simulamos datos de empresas receptoras
    receptores = [
        {
            'id': 1,
            'nombre': 'EcoMuebles',
            'logo': 'https://via.placeholder.com/150',
            'descripcion': 'Empresa dedicada a la transformación de madera y muebles viejos en piezas renovadas.',
            'categorias': ['Madera', 'Muebles', 'Textiles'],
            'ubicacion': 'Santiago Centro',
            'contacto': 'contacto@ecomuebles.cl'
        },
        {
            'id': 2,
            'nombre': 'MetalArte',
            'logo': 'https://via.placeholder.com/150',
            'descripcion': 'Especialistas en dar nueva vida a todo tipo de metales y chatarra convirtiéndolos en arte funcional.',
            'categorias': ['Chatarra', 'Metales', 'Electrónicos'],
            'ubicacion': 'Providencia',
            'contacto': 'info@metalarte.cl'
        },
        {
            'id': 3,
            'nombre': 'PlastiRenova',
            'logo': 'https://via.placeholder.com/150',
            'descripcion': 'Transformamos plásticos desechados en nuevos productos útiles para el hogar y la oficina.',
            'categorias': ['Plástico', 'PET', 'Envases'],
            'ubicacion': 'Ñuñoa',
            'contacto': 'hola@plastirenova.cl'
        },
        {
            'id': 4,
            'nombre': 'TextilCreativo',
            'logo': 'https://via.placeholder.com/150',
            'descripcion': 'Damos nueva vida a textiles usados creando prendas únicas y accesorios sostenibles.',
            'categorias': ['Textiles', 'Ropa', 'Telas'],
            'ubicacion': 'Las Condes',
            'contacto': 'contacto@textilcreativo.cl'
        },
        {
            'id': 5,
            'nombre': 'ElectroFix',
            'logo': 'https://via.placeholder.com/150',
            'descripcion': 'Reparamos y renovamos aparatos electrónicos dándoles una segunda oportunidad.',
            'categorias': ['Electrónicos', 'Reparables', 'Eléctricos'],
            'ubicacion': 'La Florida',
            'contacto': 'info@electrofix.cl'
        }
    ]
    
    # Obtener todas las categorías únicas
    todas_categorias = set()
    for receptor in receptores:
        for cat in receptor['categorias']:
            todas_categorias.add(cat)
    todas_categorias = sorted(list(todas_categorias))
    
    # Filtrar por categoría si se especifica
    if categoria:
        receptores_filtrados = [r for r in receptores if categoria in r['categorias']]
    else:
        receptores_filtrados = receptores
    
    return render_template('receptores.html', 
                          receptores=receptores_filtrados, 
                          categorias=todas_categorias,
                          categoria_seleccionada=categoria)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 