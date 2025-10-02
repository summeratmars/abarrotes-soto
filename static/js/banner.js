// JavaScript para el carrusel de banners publicitarios

class BannerCarousel {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        if (!this.container) return;
        
        this.slider = this.container.querySelector('.banner-slider');
        this.slides = this.container.querySelectorAll('.banner-slide');
        this.indicators = this.container.querySelectorAll('.indicator');
        this.prevBtn = this.container.querySelector('.banner-prev');
        this.nextBtn = this.container.querySelector('.banner-next');
        
        this.currentSlide = 0;
        this.totalSlides = this.slides.length;
        this.autoPlayInterval = null;
        this.autoPlayDelay = 5000; // 5 segundos
        
        this.init();
    }
    
    init() {
        if (this.totalSlides <= 1) return;
        
        // Event listeners para navegación
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.prevSlide());
        }
        
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.nextSlide());
        }
        
        // Event listeners para indicadores
        this.indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => this.goToSlide(index));
        });
        
        // Pausar autoplay al hacer hover
        this.container.addEventListener('mouseenter', () => this.pauseAutoPlay());
        this.container.addEventListener('mouseleave', () => this.startAutoPlay());
        
        // Soporte para touch/swipe en móviles
        this.addTouchSupport();
        
        // Iniciar autoplay
        this.startAutoPlay();
        
        // Actualizar indicadores iniciales
        this.updateIndicators();
    }
    
    goToSlide(slideIndex) {
        this.currentSlide = slideIndex;
        const translateX = -slideIndex * 100;
        this.slider.style.transform = `translateX(${translateX}%)`;
        this.updateIndicators();
    }
    
    nextSlide() {
        this.currentSlide = (this.currentSlide + 1) % this.totalSlides;
        this.goToSlide(this.currentSlide);
    }
    
    prevSlide() {
        this.currentSlide = (this.currentSlide - 1 + this.totalSlides) % this.totalSlides;
        this.goToSlide(this.currentSlide);
    }
    
    updateIndicators() {
        this.indicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index === this.currentSlide);
        });
    }
    
    startAutoPlay() {
        if (this.totalSlides <= 1) return;
        
        this.autoPlayInterval = setInterval(() => {
            this.nextSlide();
        }, this.autoPlayDelay);
    }
    
    pauseAutoPlay() {
        if (this.autoPlayInterval) {
            clearInterval(this.autoPlayInterval);
            this.autoPlayInterval = null;
        }
    }
    
    addTouchSupport() {
        let startX = 0;
        let endX = 0;
        
        this.container.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
        });
        
        this.container.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            this.handleSwipe(startX, endX);
        });
        
        // Prevenir scroll vertical mientras se hace swipe horizontal
        this.container.addEventListener('touchmove', (e) => {
            e.preventDefault();
        }, { passive: false });
    }
    
    handleSwipe(startX, endX) {
        const threshold = 50; // Mínima distancia para considerar un swipe
        const diff = startX - endX;
        
        if (Math.abs(diff) > threshold) {
            if (diff > 0) {
                this.nextSlide(); // Swipe izquierda - siguiente slide
            } else {
                this.prevSlide(); // Swipe derecha - slide anterior
            }
        }
    }
}

// Inicializar el carrusel cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar carrusel principal (móvil)
    new BannerCarousel('bannerCarousel');
    
    // Inicializar carrusel de escritorio
    new BannerCarousel('bannerCarouselDesktop');
    
    // Inicializar contador regresivo
    initCountdownTimer();
    
    // Inicializar carruseles adicionales si existen
    const additionalCarousels = document.querySelectorAll('[id^="bannerCarousel"]');
    additionalCarousels.forEach((carousel, index) => {
        if (carousel.id !== 'bannerCarousel' && carousel.id !== 'bannerCarouselDesktop') {
            new BannerCarousel(carousel.id);
        }
    });
});

// Función para el contador regresivo
function initCountdownTimer() {
    // Fecha del sorteo: 16 de enero 2026, 21:00:00 (GMT-6 México)
    const targetDate = new Date('2026-01-16T21:00:00-06:00').getTime();
    
    function updateCountdown() {
        const now = new Date().getTime();
        const timeLeft = targetDate - now;
        
        if (timeLeft > 0) {
            const days = Math.floor(timeLeft / (1000 * 60 * 60 * 24));
            const hours = Math.floor((timeLeft % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
            const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
            
            const timeString = `${days}d ${hours}h ${minutes}m`;
            
            // Actualizar todos los contadores
            const counters = document.querySelectorAll('.timeLeft');
            counters.forEach(counter => {
                counter.textContent = timeString;
            });
        } else {
            // El sorteo ya pasó
            const counters = document.querySelectorAll('.timeLeft');
            counters.forEach(counter => {
                counter.textContent = '¡SORTEO REALIZADO!';
            });
            
            // Cambiar el texto del botón
            const buttons = document.querySelectorAll('.banner-cta');
            buttons.forEach(button => {
                if (button.textContent === 'CONSULTAR MIS BOLETOS') {
                    button.textContent = 'VER RESULTADOS';
                }
            });
        }
    }
    
    // Actualizar cada minuto
    updateCountdown();
    setInterval(updateCountdown, 60000);
}

// Función para agregar nuevos banners dinámicamente
function addBanner(imageSrc, title, description, link = '#') {
    const bannerSlider = document.querySelector('.banner-slider');
    if (!bannerSlider) return;
    
    const newSlide = document.createElement('a');
    newSlide.href = link;
    newSlide.className = 'banner-slide';
    
    newSlide.innerHTML = `
        <img src="${imageSrc}" alt="${title}">
        <div class="banner-overlay">
            <div class="banner-title">${title}</div>
            <div class="banner-description">${description}</div>
        </div>
    `;
    
    bannerSlider.appendChild(newSlide);
    
    // Actualizar indicadores
    const indicators = document.querySelector('.banner-indicators');
    if (indicators) {
        const newIndicator = document.createElement('div');
        newIndicator.className = 'indicator';
        indicators.appendChild(newIndicator);
    }
}