document.addEventListener('DOMContentLoaded', function() {
    const phrases = document.querySelectorAll('.carousel-phrase');
    let currentIndex = 0;
    
    function rotatePhrases() {
        // Masque toutes les phrases
        phrases.forEach(phrase => phrase.classList.remove('active'));
        
        // Affiche la phrase actuelle
        phrases[currentIndex].classList.add('active');
        
        // Passe à la phrase suivante
        currentIndex = (currentIndex + 1) % phrases.length;
    }
    
    // Rotation toutes les 3 secondes
    setInterval(rotatePhrases, 3000);
    
    // Initialisation
    rotatePhrases();
});