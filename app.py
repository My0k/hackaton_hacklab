from flask import Flask, render_template, send_from_directory, request, url_for, jsonify
import os
import csv
import uuid
from werkzeug.utils import secure_filename
import base64
import io
from PIL import Image
from functions.genera_categorias import generar_categorias, generar_descripcion_larga, generar_titulo

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
                # Manejar las imágenes de manera más segura
                if 'imagen_url' in row:
                    image_name = row['imagen_url']
                    
                    # Evitar rutas duplicadas o erróneas
                    if image_name.startswith(('/', 'static', 'http')):
                        # Si ya es una URL completa o ruta absoluta, mantenerla
                        row['imagen_url'] = image_name
                    else:
                        # Si es solo un nombre de archivo, construir la URL
                        # Verificar primero si el archivo existe
                        img_path = os.path.join('static', 'fotos', image_name)
                        if os.path.exists(img_path):
                            row['imagen_url'] = url_for('static', filename=f'fotos/{image_name}')
                        else:
                            # Si no existe, usar una imagen de placeholder
                            row['imagen_url'] = url_for('static', filename='img/placeholder.png')
                            print(f"Advertencia: Imagen no encontrada: {image_name}")
                
                # Convertir categorías de string a lista
                if 'categorias' in row and row['categorias']:
                    row['categorias_lista'] = row['categorias'].split('|')
                else:
                    row['categorias_lista'] = []
                    
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
@app.route('/marketplace/<categoria>')
def marketplace(categoria=None):
    # Cargar todos los productos
    all_products = load_products()
    
    # Obtener todas las categorías disponibles
    categories = get_all_categories(all_products)
    
    # Filtrar por categoría si se especificó
    if categoria:
        filtered_products = [p for p in all_products 
                          if 'categorias_lista' in p and categoria in p['categorias_lista']]
    else:
        filtered_products = all_products
    
    return render_template('marketplace.html', 
                          products=filtered_products, 
                          categories=categories,
                          selected_category=categoria)

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

@app.route('/vista_receptor/<receptor>')
def vista_receptor(receptor):
    # Ruta para ver los productos por receptor
    all_products = load_products()
    
    # Filtrar productos del receptor específico
    receptor_products = [p for p in all_products if p['descartador'] == receptor]
    
    return render_template('receptor.html', 
                          receptor=receptor,
                          products=receptor_products)

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
        try:
            # Obtener datos del formulario
            titulo = request.form.get('title', 'Material Reciclable')
            descripcion = request.form.get('details', '')
            descripcion_larga = request.form.get('descripcion_larga', '')
            categorias = request.form.get('categorias', '')
            costo_envio = request.form.get('shipping_cost', '1000')  # Por defecto 1000
            
            # Manejar la imagen
            imagen_url = ''
            if 'photo' in request.files and request.files['photo'].filename:
                # Si se subió un archivo
                imagen = request.files['photo']
                # Generar nombre único para la imagen
                nombre_archivo = f"{uuid.uuid4()}_{secure_filename(imagen.filename)}"
                
                # Guardar en la carpeta /static/fotos (donde están las otras imágenes)
                ruta_guardado = os.path.join('static', 'fotos', nombre_archivo)
                os.makedirs(os.path.join('static', 'fotos'), exist_ok=True)
                imagen.save(ruta_guardado)
                
                # Guardar la URL en el formato que usa el resto de productos
                imagen_url = f"/static/fotos/{nombre_archivo}"
                
            elif 'camera_image' in request.form and request.form['camera_image']:
                # Si se capturó una imagen con la cámara (base64)
                b64_imagen = request.form['camera_image'].split(',')[1] if ',' in request.form['camera_image'] else request.form['camera_image']
                imagen_bytes = base64.b64decode(b64_imagen)
                
                # Guardar la imagen en la carpeta correcta
                nombre_archivo = f"{uuid.uuid4()}.jpg"
                ruta_guardado = os.path.join('static', 'fotos', nombre_archivo)
                os.makedirs(os.path.join('static', 'fotos'), exist_ok=True)
                
                with open(ruta_guardado, 'wb') as f:
                    f.write(imagen_bytes)
                
                # Guardar la URL en el formato que usa el resto de productos
                imagen_url = f"/static/fotos/{nombre_archivo}"
            
            # Generar un SKU único
            sku = str(uuid.uuid4())[:8]
            
            # Determinar si es descartable (ahora siempre es False por el diseño simplificado)
            descartable = "No"
            
            # Configurar el usuario que publica (podría ser dinámico en un futuro)
            usuario = "Revamper"
            
            # Asegurarse de que el archivo CSV existe y tiene encabezados
            if not os.path.exists('products.csv') or os.path.getsize('products.csv') == 0:
                with open('products.csv', 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(['sku', 'titulo', 'descripcion', 'descripcion_larga', 'costo_transporte', 'descartador', 'imagen_url', 'categorias'])
            
            # Agregar a la base de datos CSV
            with open('products.csv', 'a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow([
                    sku,
                    titulo,
                    descripcion,
                    descripcion_larga,
                    costo_envio,
                    usuario,
                    imagen_url,
                    categorias
                ])
            
            return render_template('crear_revamp.html', mensaje=f"¡Tu Revamp ha sido creado con éxito! Se ha asignado el SKU {sku}.")
        
        except Exception as e:
            app.logger.error(f"Error en crear_revamp: {str(e)}")
            return render_template('crear_revamp.html', error=f"Ocurrió un error: {str(e)}")
    
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

@app.route('/admin/fix-images')
def fix_images():
    """Endpoint administrativo para corregir problemas con las imágenes"""
    try:
        # Ejecutar la corrección de rutas
        from fix_image_paths import fix_image_paths
        fix_image_paths()
        
        # Verificar archivos de imagen
        img_dir = os.path.join('static', 'fotos')
        if not os.path.exists(img_dir):
            os.makedirs(img_dir)
        
        # Listar imágenes en el directorio
        images = os.listdir(img_dir)
        
        # Cargar productos para verificar
        products = []
        with open('products.csv', 'r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                products.append(row)
        
        # Verificar qué imágenes faltan
        missing_images = []
        for product in products:
            if 'imagen_url' in product:
                img_name = product['imagen_url']
                if img_name and img_name not in images:
                    missing_images.append(img_name)
        
        result = {
            "success": True,
            "message": "Correcciones aplicadas",
            "images_found": images,
            "missing_images": missing_images,
            "products": len(products)
        }
        
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/generar_ai_content', methods=['POST'])
def generar_ai_content():
    """Ruta para generar contenido con IA a partir de una imagen y descripción"""
    try:
        # Obtener la descripción del formulario
        descripcion = request.form.get('details', '')
        
        # Manejar la imagen
        imagen_temp = None
        if 'photo' in request.files and request.files['photo'].filename:
            # Si se subió un archivo
            imagen = request.files['photo']
            imagen_temp = os.path.join('temp', f"{uuid.uuid4()}.jpg")
            os.makedirs('temp', exist_ok=True)  # Asegurarse de que exista el directorio
            imagen.save(imagen_temp)
        elif 'camera_image' in request.form and request.form['camera_image']:
            # Si se capturó una imagen con la cámara (base64)
            b64_imagen = request.form['camera_image'].split(',')[1] if ',' in request.form['camera_image'] else request.form['camera_image']
            imagen_bytes = base64.b64decode(b64_imagen)
            
            # Guardar temporalmente la imagen
            imagen_temp = os.path.join('temp', f"{uuid.uuid4()}.jpg")
            os.makedirs('temp', exist_ok=True)
            
            # Convertir y guardar la imagen
            img = Image.open(io.BytesIO(imagen_bytes))
            img.save(imagen_temp)
        
        # Generar contenido con IA
        categorias = "No se pudo generar"
        descripcion_larga = "No se pudo generar una descripción detallada."
        titulo = "Material Reciclable"
        
        if imagen_temp:
            # Usar la IA para generar el contenido
            categorias = generar_categorias(descripcion, imagen_temp)
            descripcion_larga = generar_descripcion_larga(descripcion, imagen_temp)
            titulo = generar_titulo(descripcion, imagen_temp)
            
            # Eliminar la imagen temporal
            if os.path.exists(imagen_temp):
                os.remove(imagen_temp)
        else:
            # Si no hay imagen, intentar solo con la descripción
            categorias = generar_categorias(descripcion)
            descripcion_larga = generar_descripcion_larga(descripcion)
            titulo = generar_titulo(descripcion)
        
        # Devolver los resultados como JSON
        return jsonify({
            'titulo': titulo,
            'categorias': categorias,
            'descripcion_larga': descripcion_larga
        })
        
    except Exception as e:
        # Registrar el error y devolver un mensaje amigable
        app.logger.error(f"Error en generar_ai_content: {str(e)}")
        return jsonify({'error': f"Ocurrió un error: {str(e)}"}), 500

@app.route('/test-ai')
def test_ai():
    try:
        # Probar la generación de categorías con un texto estático
        categorias = generar_categorias("Madera de pino en buen estado")
        descripcion = generar_descripcion_larga("Madera de pino en buen estado")
        titulo = generar_titulo("Madera de pino en buen estado")
        
        return jsonify({
            'success': True,
            'titulo': titulo,
            'categorias': categorias,
            'descripcion': descripcion
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True) 