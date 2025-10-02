# Configuración de banners publicitarios para Abarrotes Soto

# Esta configuración permite gestionar los banners que aparecen en la página principal
# Cada banner debe tener: título, descripción, enlace, imagen (opcional), y colores de fondo

BANNERS_CONFIG = [
    {
        'id': 'ofertas',
        'titulo': '¡OFERTAS ESPECIALES!',
        'descripcion': 'Hasta 50% de descuento en productos seleccionados',
        'cta': 'Ver ofertas',
        'enlace': '/?categoria=ofertas',
        'gradiente': 'linear-gradient(135deg, #ff6b6b, #ff8e8e)',
        'activo': True
    },
    {
        'id': 'frescos',
        'titulo': 'PRODUCTOS FRESCOS',
        'descripcion': 'La mejor calidad en lácteos y productos frescos',
        'cta': 'Comprar ahora',
        'enlace': '/?departamento=LACTEOS',
        'gradiente': 'linear-gradient(135deg, #4ecdc4, #44a08d)',
        'activo': True
    },
    {
        'id': 'despensa',
        'titulo': 'DESPENSA BÁSICA',
        'descripcion': 'Todo lo que necesitas para tu hogar',
        'cta': 'Explorar',
        'enlace': '/?departamento=GRANOS Y CEREALES',
        'gradiente': 'linear-gradient(135deg, #f7971e, #ffd200)',
        'activo': True
    },
    {
        'id': 'bebidas',
        'titulo': 'BEBIDAS REFRESCANTES',
        'descripcion': 'Gran variedad de refrescos, aguas y jugos',
        'cta': 'Ver catálogo',
        'enlace': '/?departamento=BEBIDAS',
        'gradiente': 'linear-gradient(135deg, #667eea, #764ba2)',
        'activo': True
    },
    {
        'id': 'dulceria',
        'titulo': 'DULCERÍA',
        'descripcion': 'Los mejores dulces y golosinas',
        'cta': 'Endulza tu día',
        'enlace': '/?departamento=DULCERIA',
        'gradiente': 'linear-gradient(135deg, #ff9a9e, #fecfef)',
        'activo': True
    },
    {
        'id': 'limpieza',
        'titulo': 'PRODUCTOS DE LIMPIEZA',
        'descripcion': 'Mantén tu hogar impecable',
        'cta': 'Ver productos',
        'enlace': '/?departamento=LIMPIEZA',
        'gradiente': 'linear-gradient(135deg, #a8edea, #fed6e3)',
        'activo': True
    }
]

# Configuración del carrusel
CARRUSEL_CONFIG = {
    'autoplay': True,
    'autoplay_delay': 5000,  # 5 segundos
    'show_indicators': True,
    'show_navigation': True,
    'enable_touch': True,
    'pause_on_hover': True
}

# Función para obtener banners activos
def get_banners_activos():
    return [banner for banner in BANNERS_CONFIG if banner['activo']]

# Función para obtener banners por categoría (si se quisiera implementar)
def get_banners_por_categoria(categoria=None):
    banners = get_banners_activos()
    if categoria:
        # Filtrar por categoría si se implementa esta funcionalidad
        pass
    return banners