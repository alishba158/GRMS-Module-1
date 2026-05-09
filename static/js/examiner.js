// Examiner custom JavaScript
console.log("✅ Examiner JS loaded");

// Ensure AOS is initialized (safely)
document.addEventListener('DOMContentLoaded', function() {
    if (typeof AOS !== 'undefined') {
        AOS.init({ duration: 600, once: true, offset: 5 });
        console.log("AOS initialized");
    } else {
        console.log("AOS not loaded – check CDN");
    }
});