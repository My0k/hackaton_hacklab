import os
import sys

def check_environment():
    """Verifica variables de entorno y directorios críticos"""
    print("=== Verificación del entorno ===")
    
    # Verificar Python
    print(f"Python version: {sys.version}")
    
    # Verificar variables de entorno
    print("\n--- Variables de entorno ---")
    for var in ['FLASK_APP', 'PORT', 'PYTHONPATH']:
        print(f"{var}: {os.environ.get(var, 'No establecida')}")
    
    # Verificar directorios
    print("\n--- Directorios ---")
    for directory in ['static', 'static/fotos', 'temp']:
        exists = os.path.exists(directory)
        is_dir = os.path.isdir(directory) if exists else False
        writable = os.access(directory, os.W_OK) if exists else False
        print(f"{directory}: Existe: {exists}, Es directorio: {is_dir}, Escritura: {writable}")
    
    # Verificar archivos importantes
    print("\n--- Archivos importantes ---")
    for file in ['app.py', 'products.csv', 'materiales.csv', 'requirements.txt']:
        exists = os.path.exists(file)
        is_file = os.path.isfile(file) if exists else False
        readable = os.access(file, os.R_OK) if exists else False
        writable = os.access(file, os.W_OK) if exists else False
        if exists:
            size = os.path.getsize(file)
            print(f"{file}: Existe: {exists}, Es archivo: {is_file}, Tamaño: {size} bytes, Lectura: {readable}, Escritura: {writable}")
        else:
            print(f"{file}: Existe: {exists}, Es archivo: {is_file}, Lectura: {readable}, Escritura: {writable}")
    
    # Verificar la aplicación Flask
    print("\n--- Verificación de la aplicación Flask ---")
    try:
        from app import app as flask_app
        print(f"Rutas registradas:")
        for rule in flask_app.url_map.iter_rules():
            print(f"  {rule}")
    except Exception as e:
        print(f"Error al importar la aplicación Flask: {e}")

if __name__ == "__main__":
    check_environment()
    print("\nSi todo está correcto, ejecuta: gunicorn --bind 0.0.0.0:5000 app:app") 