# 🎯 Configuración Final: 2 Banners para Abarrotes Soto

## ✅ **LO QUE YA ESTÁ CONFIGURADO:**

Tu página web ya está lista para mostrar **exactamente 2 banners**:

### 📱 **Versión Móvil y 💻 Escritorio:**
1. **🎯 RIFA 2026** - Busca la imagen: `RIFA2026.jpg`
2. **🎉 OFERTAS ESPECIALES** - Busca la imagen: `OFERTAS.jpg`

---

## 📁 **PASO 1: Sube las imágenes**

Coloca estas 2 imágenes en la carpeta:
```
/static/images/banners/
├── RIFA2026.jpg
└── OFERTAS.jpg
```

### 📐 **Especificaciones de las imágenes:**
- **Tamaño**: 1200x200 píxeles (recomendado)
- **Formato**: JPG preferiblemente 
- **Peso**: Menos de 500KB cada una
- **Nombres**: **EXACTAMENTE** como se muestra arriba (incluye mayúsculas)

---

## 🎨 **PASO 2: Personaliza el contenido (opcional)**

Si quieres cambiar los textos, edita en `/templates/index.html`:

### Banner RIFA 2026:
```html
<h2>🎯 RIFA 2026</h2>
<p>¡Participa y gana increíbles premios!</p>
<span class="banner-cta">Participar</span>
```

### Banner OFERTAS:
```html
<h2>🎉 OFERTAS ESPECIALES</h2>
<p>Hasta 50% de descuento en productos seleccionados</p>
<span class="banner-cta">Ver ofertas</span>
```

---

## 🔗 **PASO 3: Enlaces de los banners**

Los banners actuales enlazan a:
- **RIFA 2026**: `/productos` (página general de productos)
- **OFERTAS**: `/productos?categoria=ofertas` (productos en oferta)

Para cambiar los enlaces, busca en `/templates/index.html`:
```html
<a href="/productos" class="banner-slide">  <!-- RIFA 2026 -->
<a href="/productos?categoria=ofertas" class="banner-slide">  <!-- OFERTAS -->
```

---

## ⚙️ **FUNCIONAMIENTO AUTOMÁTICO:**

### 🔄 **Carrusel automático:**
- Cambia entre los 2 banners cada **5 segundos**
- Se pausa al pasar el mouse encima
- Funciona en móvil y escritorio

### 🎮 **Controles manuales:**
- **Flechas** ← → para cambiar manualmente
- **Puntos indicadores** abajo para ir a banner específico
- **Swipe/deslizar** en móviles

### 📱 **Responsivo:**
- **Móvil**: 120px de alto
- **Tablet**: 150px de alto  
- **Escritorio**: 200px de alto

---

## ✅ **CHECKLIST FINAL:**

- [ ] Sube `RIFA2026.jpg` a `/static/images/banners/`
- [ ] Sube `OFERTAS.jpg` a `/static/images/banners/`
- [ ] Verifica que los nombres sean **exactos** (mayúsculas incluidas)
- [ ] Prueba la página web para confirmar que se cargan
- [ ] Ajusta textos si es necesario
- [ ] Verifica que los enlaces funcionen correctamente

---

## 🎯 **RESULTADO FINAL:**

Tu página principal mostrará:
1. **Banner RIFA 2026** con tu imagen personalizada
2. **Banner OFERTAS** con tu imagen personalizada  
3. Cambio automático cada 5 segundos
4. Funciona perfectamente en móvil y escritorio
5. Solo aparece en la página principal (no en categorías/búsquedas)

---

## 🚨 **IMPORTANTE:**

- Los nombres de archivo deben ser **EXACTAMENTE**: `RIFA2026.jpg` y `OFERTAS.jpg`
- Si usas otros nombres, debes cambiarlos también en el código HTML
- Las imágenes deben estar en formato JPG para mejor compatibilidad

¡Ya tienes todo listo! Solo sube las 2 imágenes y disfruta de tus banners publicitarios! 🎉