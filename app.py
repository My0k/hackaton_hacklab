from flask import Flask, render_template, send_from_directory, request, url_for
import os
import csv
import uuid
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/fotos'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def load_products():
    products = []
    try:
        with open('products.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # Añadir la ruta completa a las imágenes
                row['imagen_url'] = url_for('static', filename=f'fotos/{row["imagen_url"]}')
                # Convertir categorías de string a lista
                row['categorias_lista'] = row['categorias'].split('|')
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

def load_materials():
    materials = []
    try:
        with open('materiales.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file, skipinitialspace=True)
            for row in csv_reader:
                # Convertir categorías de string a lista
                if 'categorias' in row:
                    row['categorias_lista'] = row['categorias'].split('|')
                materials.append(row)
        return materials
    except Exception as e:
        print(f"Error loading materials: {e}")
        return []

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
@app.route('/receptor/<receptor>/<categoria>')
def vista_receptor(receptor, categoria=None):
    # Cargar todos los productos
    all_products = load_products()
    
    # Cargar todos los materiales
    all_materials = load_materials()
    
    # Crear un diccionario para mapear materiales a sus categorías
    material_to_categories = {}
    material_names = []
    for mat in all_materials:
        if 'nombre_material' in mat and 'categorias_lista' in mat:
            material_to_categories[mat['nombre_material']] = mat['categorias_lista']
            material_names.append(mat['nombre_material'])
    
    # Filtrar productos por receptor (descartador)
    receptor_products = [p for p in all_products if p['descartador'].lower() == receptor.lower()]
    
    # Filtrar adicionalmente por categoría si se especifica
    selected_material = None
    if categoria:
        # Determinar a qué material pertenece esta categoría
        for material, categories in material_to_categories.items():
            if categoria in categories:
                selected_material = material
                break
        
        # Filtrar productos por la categoría seleccionada
        receptor_products = [p for p in receptor_products 
                           if 'categorias_lista' in p and categoria in p['categorias_lista']]
    
    return render_template('receptor.html', 
                          products=receptor_products,
                          materials=all_materials,
                          material_to_categories=material_to_categories,
                          material_names=material_names,
                          receptor_name=receptor,
                          selected_category=categoria,
                          selected_material=selected_material)

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

@app.route('/productos-por-material')
@app.route('/productos-por-material/<material>')
def productos_por_material(material=None):
    # Cargar todos los productos
    all_products = load_products()
    
    # Cargar todos los materiales
    all_materials = load_materials()
    
    # Crear una estructura de datos para el mapeo de materiales a categorías
    material_to_categories = {}
    for mat in all_materials:
        if 'nombre_material' in mat and 'categorias_lista' in mat:
            material_to_categories[mat['nombre_material']] = mat['categorias_lista']
    
    # Determinar las categorías a filtrar basado en el material seleccionado
    filter_categories = []
    selected_material_name = None
    if material:
        for mat in all_materials:
            if 'nombre_material' in mat and mat['nombre_material'].lower() == material.lower():
                if 'categorias_lista' in mat:
                    filter_categories = mat['categorias_lista']
                    selected_material_name = mat['nombre_material']
                break
    
    # Filtrar productos según las categorías del material seleccionado
    if filter_categories:
        filtered_products = []
        for product in all_products:
            if 'categorias_lista' in product:
                # Un producto coincide si cualquiera de sus categorías está en las categorías del material
                for category in product['categorias_lista']:
                    if category.lower() in [c.lower() for c in filter_categories]:
                        filtered_products.append(product)
                        break
    else:
        filtered_products = all_products
    
    # Obtener nombres de materiales para el menú de navegación
    material_names = [mat['nombre_material'] for mat in all_materials if 'nombre_material' in mat]
    
    return render_template('productos_por_material.html',
                          products=filtered_products,
                          materials=all_materials,
                          material_names=material_names,
                          selected_material=selected_material_name)

@app.route('/materiales-disponibles')
@app.route('/materiales-disponibles/<material>')
@app.route('/materiales-disponibles/<material>/<categoria>')
def materiales_disponibles(material=None, categoria=None):
    # Cargar todos los productos
    all_products = load_products()
    
    # Cargar todos los materiales
    all_materials = load_materials()
    
    # Crear un diccionario para mapear materiales a sus categorías
    material_to_categories = {}
    material_names = []
    for mat in all_materials:
        if 'nombre_material' in mat and 'categorias_lista' in mat:
            material_to_categories[mat['nombre_material']] = mat['categorias_lista']
            material_names.append(mat['nombre_material'])
    
    # Filtrar productos según el material seleccionado
    filtered_products = all_products
    
    if material:
        # Obtener las categorías del material seleccionado
        material_categories = []
        for mat in all_materials:
            if mat['nombre_material'] == material:
                material_categories = mat['categorias_lista']
                break
        
        # Si también se seleccionó una categoría específica
        if categoria and categoria in material_categories:
            filtered_products = [p for p in all_products 
                               if 'categorias_lista' in p and categoria in p['categorias_lista']]
        # Si solo se seleccionó el material, mostrar todos los productos que coincidan con cualquiera de sus categorías
        else:
            temp_products = []
            for product in all_products:
                if 'categorias_lista' in product:
                    for cat in product['categorias_lista']:
                        if cat in material_categories:
                            temp_products.append(product)
                            break
            filtered_products = temp_products
    
    # Agrupar productos por proveedor (descartador)
    proveedores = {}
    for product in filtered_products:
        proveedor = product['descartador']
        if proveedor not in proveedores:
            proveedores[proveedor] = []
        proveedores[proveedor].append(product)
    
    return render_template('materiales_disponibles.html',
                          all_products=filtered_products,
                          proveedores=proveedores,
                          materials=all_materials,
                          material_to_categories=material_to_categories,
                          material_names=material_names,
                          selected_material=material,
                          selected_category=categoria)

@app.route('/crear-revamp', methods=['GET', 'POST'])
def crear_revamp():
    if request.method == 'POST':
        details = request.form.get('details', '')
        camera_image = request.form.get('camera_image', '')
        
        # Verificar si se envió una imagen de cámara
        if camera_image and camera_image.startswith('data:image'):
            try:
                # Extraer los datos de la imagen en base64
                import base64
                import re
                # Extraer el tipo de imagen y los datos
                image_data = re.sub('^data:image/.+;base64,', '', camera_image)
                # Decodificar la imagen
                decoded_image = base64.b64decode(image_data)
                
                # Generar un nombre de archivo único
                unique_filename = f"{uuid.uuid4().hex}.jpg"
                
                # Asegurarse de que el directorio existe
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                # Guardar la imagen
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                with open(file_path, 'wb') as f:
                    f.write(decoded_image)
                
                # Obtener el siguiente SKU
                next_sku = get_next_sku()
                
                # Preparar nueva fila para el CSV
                new_product = {
                    'sku': next_sku,
                    'titulo': details[:30],  # Limitar título a 30 caracteres
                    'descripcion': details,
                    'descripcion_larga': '',
                    'costo_transporte': '2000',  # Valor por defecto
                    'descartador': 'Revamper',
                    'imagen_url': unique_filename,
                    'categorias': ''
                }
                
                # Añadir al CSV
                try:
                    # Verificar si el archivo existe y obtener los encabezados
                    file_exists = os.path.isfile('products.csv')
                    
                    with open('products.csv', 'a', newline='', encoding='utf-8') as file:
                        fieldnames = ['sku', 'titulo', 'descripcion', 'descripcion_larga', 
                                      'costo_transporte', 'descartador', 'imagen_url', 'categorias']
                        writer = csv.DictWriter(file, fieldnames=fieldnames)
                        
                        # Escribir encabezados solo si el archivo es nuevo
                        if not file_exists:
                            writer.writeheader()
                        
                        writer.writerow(new_product)
                    
                    return render_template('crear_revamp.html', 
                                          mensaje=f"¡Tu Revamp ha sido creado exitosamente! Producto #{next_sku}")
                
                except Exception as e:
                    print(f"Error saving to CSV: {e}")
                    return render_template('crear_revamp.html', 
                                          error=f"Error al guardar el producto: {str(e)}")
                
            except Exception as e:
                print(f"Error processing camera image: {e}")
                return render_template('crear_revamp.html', 
                                      error=f"Error al procesar la imagen: {str(e)}")
        
        # Si no hay imagen de cámara, procesar el archivo subido normalmente
        elif 'photo' in request.files:
            file = request.files['photo']
            
            # Si el usuario no selecciona un archivo
            if file.filename == '':
                return render_template('crear_revamp.html', error="No se seleccionó ninguna imagen")
            
            if file and allowed_file(file.filename):
                # Generar un nombre de archivo seguro y único
                filename = secure_filename(file.filename)
                # Añadir un identificador único para evitar sobreescrituras
                unique_filename = f"{uuid.uuid4().hex}_{filename}"
                
                # Asegurarse de que el directorio existe
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                
                # Guardar el archivo
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                
                # Obtener el siguiente SKU
                next_sku = get_next_sku()
                
                # Preparar nueva fila para el CSV
                new_product = {
                    'sku': next_sku,
                    'titulo': details[:30],  # Limitar título a 30 caracteres
                    'descripcion': details,
                    'descripcion_larga': '',
                    'costo_transporte': '2000',  # Valor por defecto
                    'descartador': 'Revamper',
                    'imagen_url': unique_filename,
                    'categorias': ''
                }
                
                # Añadir al CSV
                try:
                    # Verificar si el archivo existe y obtener los encabezados
                    file_exists = os.path.isfile('products.csv')
                    
                    with open('products.csv', 'a', newline='', encoding='utf-8') as file:
                        fieldnames = ['sku', 'titulo', 'descripcion', 'descripcion_larga', 
                                      'costo_transporte', 'descartador', 'imagen_url', 'categorias']
                        writer = csv.DictWriter(file, fieldnames=fieldnames)
                        
                        # Escribir encabezados solo si el archivo es nuevo
                        if not file_exists:
                            writer.writeheader()
                        
                        writer.writerow(new_product)
                    
                    return render_template('crear_revamp.html', 
                                          mensaje=f"¡Tu Revamp ha sido creado exitosamente! Producto #{next_sku}")
                
                except Exception as e:
                    print(f"Error saving to CSV: {e}")
                    return render_template('crear_revamp.html', 
                                          error=f"Error al guardar el producto: {str(e)}")
            else:
                return render_template('crear_revamp.html', 
                                      error="Formato de archivo no permitido. Use PNG, JPG, JPEG o GIF")
        else:
            return render_template('crear_revamp.html', error="No se proporcionó ninguna imagen")
    
    return render_template('crear_revamp.html')

# Función para verificar extensiones permitidas
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Función para obtener el próximo SKU
def get_next_sku():
    try:
        with open('products.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            max_sku = 0
            for row in csv_reader:
                try:
                    sku_num = int(row['sku'])
                    if sku_num > max_sku:
                        max_sku = sku_num
                except (ValueError, KeyError):
                    continue
            
            # Formatear el siguiente SKU como string de 3 dígitos
            next_sku = str(max_sku + 1).zfill(3)
            return next_sku
    except Exception as e:
        print(f"Error getting next SKU: {e}")
        return "001"  # Valor por defecto si hay error

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 