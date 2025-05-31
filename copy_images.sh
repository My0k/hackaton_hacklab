#!/bin/bash

# Crear el directorio si no existe
mkdir -p static/fotos

# Lista de imágenes a copiar
IMAGES=("fardo.png" "madera.png" "bici.png" "computador.png" "ventana.png" "tv.png" "silla.png" "lavadora.png")

# Verificar si las imágenes existen en el directorio principal
for img in "${IMAGES[@]}"; do
  if [ -f "$img" ]; then
    cp "$img" static/fotos/
    echo "Copiado $img a static/fotos/"
  else
    echo "Advertencia: $img no encontrado"
    # Crear una imagen placeholder si no existe
    touch static/fotos/$img
    echo "Creado placeholder para $img"
  fi
done

echo "¡Proceso completado!" 