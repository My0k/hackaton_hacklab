#!/bin/bash
# Verificar que exista el directorio
if [ ! -d "static/fotos" ]; then
    mkdir -p static/fotos
    echo "Directorio creado: static/fotos"
fi

# Verificar permisos
chmod -R 755 static/fotos
echo "Permisos actualizados para static/fotos"

# Listar contenido
echo "Contenido del directorio:"
ls -la static/fotos 