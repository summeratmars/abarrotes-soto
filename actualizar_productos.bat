@echo off
cd /d C:\Users\Summe\OneDrive\Documents\catalogo_web_con_categorias

echo ----------------------------
echo 🔁 SUBIENDO CAMBIOS A GITHUB
echo ----------------------------

git add .
git commit -m "Actualización automática de productos e imágenes"
git push origin main

echo ----------------------------
echo ✅ ¡Listo! La tienda se actualizará en 1-2 minutos.
pause
