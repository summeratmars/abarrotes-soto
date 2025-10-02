# Documentación de Banners Publicitarios

## Descripción
Este sistema de banners publicitarios permite mostrar información promocional en la página principal de Abarrotes Soto, tanto en la versión móvil como en la de escritorio.

## Características
- **Carrusel automático**: Los banners cambian cada 5 segundos
- **Navegación manual**: Flechas izquierda/derecha y indicadores de puntos
- **Responsivo**: Se adapta a dispositivos móviles y escritorio
- **Touch/Swipe**: Soporte para gestos táctiles en móviles
- **Pausa automática**: Al pasar el mouse se pausa el carrusel
- **Enlaces funcionales**: Cada banner lleva a una sección específica

## Archivos involucrados

### 1. CSS - `/static/css/banner.css`
Contiene todos los estilos para el carrusel de banners:
- Estilos del contenedor y slider
- Animaciones y transiciones
- Controles de navegación
- Indicadores de posición
- Estilos responsivos

### 2. JavaScript - `/static/js/banner.js`
Funcionalidad del carrusel:
- Clase `BannerCarousel` para manejar la lógica
- Autoplay y navegación manual
- Soporte para touch/swipe
- Múltiples carruseles en la misma página

### 3. Plantilla principal - `/templates/index.html`
Implementación de los banners:
- Versión móvil: Se muestra solo en la página principal
- Versión escritorio: Se muestra solo en la página principal (6 banners)

### 4. Configuración - `/config_banners.py`
Archivo de configuración para gestionar los banners:
- Lista de banners disponibles
- Configuración del carrusel
- Funciones para obtener banners activos

### 5. Componente reutilizable - `/templates/banner_carousel.html`
Plantilla que puede reutilizarse en otras páginas.

## Cómo agregar un nuevo banner

### Método 1: Editar directamente en HTML
1. Abrir `/templates/index.html`
2. Localizar la sección de banners (móvil o escritorio)
3. Copiar un banner existente y modificar:
   - `href`: Enlace de destino
   - `h2`: Título del banner
   - `p`: Descripción
   - `banner-cta`: Texto del botón
   - `style`: Colores de fondo (gradiente)

### Método 2: Usar configuración (recomendado para futuras mejoras)
1. Editar `/config_banners.py`
2. Agregar un nuevo banner a `BANNERS_CONFIG`:
```python
{
    'id': 'nuevo_banner',
    'titulo': 'TÍTULO DEL BANNER',
    'descripcion': 'Descripción del banner',
    'cta': 'Texto del botón',
    'enlace': '/?departamento=DEPARTAMENTO',
    'gradiente': 'linear-gradient(135deg, #color1, #color2)',
    'activo': True
}
```

## Personalización de colores

Los banners usan gradientes CSS. Algunos ejemplos:
- Rojo: `linear-gradient(135deg, #ff6b6b, #ff8e8e)`
- Verde: `linear-gradient(135deg, #4ecdc4, #44a08d)`
- Amarillo: `linear-gradient(135deg, #f7971e, #ffd200)`
- Azul: `linear-gradient(135deg, #667eea, #764ba2)`
- Rosa: `linear-gradient(135deg, #ff9a9e, #fecfef)`

## Configuración del carrusel

En `/static/js/banner.js` puedes modificar:
- `autoPlayDelay`: Tiempo entre cambios (5000ms = 5 segundos)
- Velocidad de transición CSS en `/static/css/banner.css`

## Responsividad

Los banners se adaptan automáticamente:
- **Escritorio**: 200px de alto, texto grande
- **Tablet**: 150px de alto, texto mediano  
- **Móvil**: 120px de alto, texto pequeño

## Enlaces de los banners

Actualmente los banners enlazan a:
- Ofertas: `/?categoria=ofertas`
- Lácteos: `/?departamento=LACTEOS`
- Granos: `/?departamento=GRANOS Y CEREALES`
- Bebidas: `/?departamento=BEBIDAS`
- Dulcería: `/?departamento=DULCERIA`
- Limpieza: `/?departamento=LIMPIEZA`

## Mantenimiento

Para mantener los banners actualizados:
1. Cambiar las ofertas y promociones regularmente
2. Actualizar los enlaces según la disponibilidad de productos
3. Ajustar los colores según la temporada o eventos especiales
4. Monitorear el rendimiento y clics en cada banner

## Posibles mejoras futuras

1. **Panel de administración**: Para gestionar banners desde la web
2. **Imágenes reales**: Subir fotos de productos en lugar de gradientes
3. **Programación**: Banners que aparezcan en fechas específicas
4. **Analytics**: Seguimiento de clics en cada banner
5. **A/B Testing**: Probar diferentes versiones de banners