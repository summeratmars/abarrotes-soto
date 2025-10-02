# 📸 Cómo Agregar Fotos a los Banners

## Paso 1: Preparar las Imágenes

### Tamaños Recomendados:
- **Escritorio**: 1200x200 px (ratio 6:1)
- **Móvil**: 375x120 px (ratio 3.125:1)
- **Formato**: JPG, PNG, WEBP

### Nombres Sugeridos:
- `ofertas.jpg` - Banner de ofertas especiales
- `lacteos.jpg` - Productos frescos/lácteos  
- `granos.jpg` - Despensa básica/granos
- `bebidas.jpg` - Bebidas refrescantes
- `dulces.jpg` - Dulcería
- `limpieza.jpg` - Productos de limpieza

## Paso 2: Subir las Imágenes

Coloca las imágenes en la carpeta:
```
/static/images/banners/
```

Ejemplo de estructura:
```
static/
  images/
    banners/
      ofertas.jpg
      lacteos.jpg
      granos.jpg
      bebidas.jpg
      dulces.jpg
      limpieza.jpg
```

## Paso 3: Modificar los Banners

### Opción A: Reemplazar gradientes con imágenes

Cambia esto:
```html
<div class="banner-ejemplo banner-ofertas">
    <h2>¡OFERTAS ESPECIALES!</h2>
    <p>Hasta 50% de descuento</p>
    <span class="banner-cta">Ver ofertas</span>
</div>
```

Por esto:
```html
<div class="banner-imagen" style="background-image: url('{{ url_for('static', filename='images/banners/ofertas.jpg') }}');">
    <div class="banner-content">
        <h2>¡OFERTAS ESPECIALES!</h2>
        <p>Hasta 50% de descuento</p>
        <span class="banner-cta">Ver ofertas</span>
    </div>
</div>
```

### Opción B: Usar tag IMG tradicional

```html
<div class="banner-slide">
    <img src="{{ url_for('static', filename='images/banners/ofertas.jpg') }}" alt="Ofertas Especiales">
    <div class="banner-overlay">
        <div class="banner-title">¡OFERTAS ESPECIALES!</div>
        <div class="banner-description">Encuentra los mejores precios</div>
    </div>
</div>
```

## Paso 4: Implementación Completa

Te voy a mostrar exactamente cómo modificar tu archivo actual...

### 1. Para Versión Móvil:

Busca esta sección en `/templates/index.html` (línea ~195):
```html
<!-- Banner 1: Ofertas especiales -->
<a href="/productos?categoria=ofertas" class="banner-slide">
    <div class="banner-ejemplo banner-ofertas">
```

Y reemplázala con:
```html
<!-- Banner 1: Ofertas especiales -->
<a href="/productos?categoria=ofertas" class="banner-slide">
    <div class="banner-imagen" style="background-image: url('{{ url_for('static', filename='images/banners/ofertas.jpg') }}');">
        <div class="banner-content">
            <h2>¡OFERTAS ESPECIALES!</h2>
            <p>Hasta 50% de descuento en productos seleccionados</p>
            <span class="banner-cta">Ver ofertas</span>
        </div>
    </div>
```

### 2. Para Versión Escritorio:

Busca la sección similar en la versión de escritorio (línea ~590) y haz el mismo cambio.

## Paso 5: Imágenes de Respaldo

Para que funcione sin imágenes, puedes agregar un fallback:

```css
.banner-imagen {
    background-image: url('ruta/imagen.jpg'), linear-gradient(135deg, #ff6b6b, #ff8e8e);
}
```

## Paso 6: Optimización

### Compresión de Imágenes:
- Usa herramientas como TinyPNG o Squoosh
- Mantén el tamaño de archivo bajo 500KB por imagen

### Carga Lazy:
```html
<img loading="lazy" src="...">
```

### Formatos Modernos:
```html
<picture>
    <source srcset="imagen.webp" type="image/webp">
    <img src="imagen.jpg" alt="Banner">
</picture>
```

## Ejemplo Completo de Banner con Imagen

```html
<a href="/productos?departamento=BEBIDAS" class="banner-slide">
    <div class="banner-imagen" style="background-image: url('{{ url_for('static', filename='images/banners/bebidas.jpg') }}');">
        <div class="banner-content">
            <h2>BEBIDAS REFRESCANTES</h2>
            <p>Gran variedad de refrescos, aguas y jugos</p>
            <span class="banner-cta">Ver catálogo</span>
        </div>
    </div>
    <div class="banner-overlay">
        <div class="banner-title">BEBIDAS REFRESCANTES</div>
        <div class="banner-description">Para todos los gustos y todas las ocasiones</div>
    </div>
</a>
```

## Consideraciones de Diseño

### Contraste:
- Asegúrate de que el texto sea legible sobre la imagen
- Usa overlay oscuro si es necesario
- Coloca el texto en áreas menos ocupadas de la imagen

### Llamada a la Acción:
- El botón CTA debe ser visible y contrastante
- Usa colores que destaquen sobre la imagen

### Responsividad:
- Las imágenes deben verse bien en móviles y escritorio
- Considera usar diferentes imágenes para diferentes tamaños

## Tips para Buenas Imágenes de Banner

1. **Composición**: Deja espacio para el texto
2. **Calidad**: Usa imágenes de alta resolución
3. **Relevancia**: Que la imagen relate con el contenido
4. **Branding**: Mantén coherencia con los colores de la marca
5. **Optimización**: Balancea calidad vs. tiempo de carga

¿Te ayudo a implementar alguna de estas opciones específicamente?