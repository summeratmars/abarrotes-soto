// ✅ Inicializar carrito al cargar
// ✅ Declarar carrito como variable global
var carrito = [];

(function inicializarCarrito() {
    const flag = localStorage.getItem('pedido_enviado');
    if (flag === '1') {
        localStorage.removeItem('carrito');
        localStorage.removeItem('pedido_enviado');
        carrito = [];
    } else {
        carrito = JSON.parse(localStorage.getItem('carrito')) || [];
    }
})();


// ✅ Actualiza el ícono y burbuja del carrito
function actualizarBotonCarrito() {
    let total = 0, cantidad = 0;
    carrito.forEach(p => {
        total += p.precio * p.cantidad;
        cantidad += p.cantidad;
    });

    const contador = document.getElementById('carrito-contador');
    const totalSpan = document.getElementById('carrito-total');
    const burbuja = document.getElementById('contador-burbuja');

    if (contador) contador.textContent = cantidad;
    if (totalSpan) totalSpan.textContent = total.toFixed(2);

    if (burbuja) {
        if (cantidad > 0) {
            burbuja.textContent = cantidad;
            burbuja.style.display = "inline-block";
            burbuja.classList.add("rebote");
            setTimeout(() => burbuja.classList.remove("rebote"), 300);
        } else {
            burbuja.style.display = "none";
        }
    }
}

// ✅ Agrega 1 unidad de un producto
function incrementarCantidad(cbarras, nombre, precio, precioOriginal, puntosLealtad = 0) {
    let existente = carrito.find(p => p.cbarras === cbarras);
    if (existente) {
        existente.cantidad += 1;
    } else {
        carrito.push({ cbarras, nombre, precio, precio_original: precioOriginal, cantidad: 1, puntos: puntosLealtad });
    }
    localStorage.setItem('carrito', JSON.stringify(carrito));
    renderControlCantidad(cbarras, existente ? existente.cantidad : 1);
    actualizarBotonCarrito();

    // 🔔 Asegúrate de tener esto:
    if (typeof mostrarToast === "function") {
        mostrarToast("✅ Producto agregado al pedido");
    }
}


// ✅ Suma o resta cantidad
function modificarCantidad(cbarras, cambio) {
    let index = carrito.findIndex(p => p.cbarras === cbarras);
    if (index >= 0) {
        carrito[index].cantidad += cambio;
        if (carrito[index].cantidad <= 0) {
            carrito.splice(index, 1);
            restaurarAgregar(cbarras);
        } else {
            renderControlCantidad(cbarras, carrito[index].cantidad);
        }
        localStorage.setItem('carrito', JSON.stringify(carrito));
        actualizarBotonCarrito();
    }
}

// ✅ Restaura botón "Agregar" si cantidad llega a cero
function restaurarAgregar(cbarras) {
    const div = document.getElementById("control-" + cbarras);
    const nombre = div.dataset.nombre;
    const precio = parseFloat(div.dataset.precio);
    const precioOriginal = parseFloat(div.dataset.precioOriginal);
    const puntos = parseInt(div.dataset.puntos) || 0;

    div.innerHTML = `
        <button class="boton-agregar"
            onclick="incrementarCantidad('${cbarras}', '${nombre}', ${precio}, ${precioOriginal}, ${puntos})">
            🛒 Agregar
        </button>
    `;
}


// ✅ Muestra los botones + y – con cantidad actual
function renderControlCantidad(cbarras, cantidad) {
    const div = document.getElementById("control-" + cbarras);
    div.innerHTML = `
        <div style="
            display: flex;
            justify-content: center;
            align-items: center;
            border: 2px solid #b30000;
            border-radius: 30px;
            padding: 4px 10px;
            background-color: white;
            gap: 15px;
            box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
        ">
            <button onclick="modificarCantidad('${cbarras}', -1)" style="
                border: none;
                background: none;
                color: #b30000;
                font-size: 20px;
                font-weight: bold;
                cursor: pointer;
            ">–</button>

            <span id="cantidad-${cbarras}" style="
                min-width: 20px;
                text-align: center;
                font-weight: bold;
                color: #222;
                font-size: 16px;
            ">${cantidad}</span>

            <button onclick="modificarCantidad('${cbarras}', 1)" style="
                border: none;
                background: none;
                color: #b30000;
                font-size: 20px;
                font-weight: bold;
                cursor: pointer;
            ">+</button>
        </div>
    `;
}


// ✅ Ejecutar al cargar
window.onload = actualizarBotonCarrito;
