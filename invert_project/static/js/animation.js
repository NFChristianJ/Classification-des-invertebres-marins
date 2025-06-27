// static/js/animations.js
// static/js/slider.js
document.addEventListener('DOMContentLoaded', function() {
    // Précharge toutes les images
    const slides = document.querySelectorAll('.slide');
    slides.forEach(slide => {
        const img = new Image();
        img.src = slide.style.backgroundImage.replace(/url\(['"]?(.*?)['"]?\)/i, '$1');
    });

    // Garantit la transition sans blanc
    let current = 0;
    const totalSlides = slides.length;
    
    function activateNext() {
        slides[current].classList.remove('active');
        current = (current + 1) % totalSlides;
        slides[current].classList.add('active');
        
        // Prépare le prochain slide
        const next = (current + 1) % totalSlides;
        slides[next].classList.add('next-in-line');
    }

    // Démarrer
    slides[0].classList.add('active');
    slides[1].classList.add('next-in-line');
    setInterval(activateNext, 4000); // 4 secondes par slide
});