// student.js (Cleaned Version - Safe for Forms)
document.addEventListener('DOMContentLoaded', function() {
    // AOS initialization
    if (typeof AOS !== 'undefined') {
        AOS.init({ duration: 600, once: true, offset: 5 });
    }

    // Mobile menu toggle (if needed)
    initMobileMenu();
    
    // Counter animation (safe)
    animateCounters();

    // Logout confirmation (safe)
    initLogoutConfirm();
});

function initMobileMenu() {
    const toggle = document.querySelector('.mobile-toggle');
    const sidebar = document.querySelector('.sidebar');
    if (toggle && sidebar) {
        toggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
}

function animateCounters() {
    const counters = document.querySelectorAll('.counter');
    counters.forEach(counter => {
        const target = parseInt(counter.innerText);
        if (target > 0) {
            let count = 0;
            const speed = Math.floor(1500 / target);
            const update = () => {
                if (count < target) {
                    count++;
                    counter.innerText = count;
                    setTimeout(update, speed);
                }
            };
            update();
        }
    });
}

function initLogoutConfirm() {
    const logoutForm = document.querySelector('.logout-container form');
    if (logoutForm) {
        logoutForm.addEventListener('submit', function(e) {
            if (!confirm('Are you sure you want to logout?')) {
                e.preventDefault();
            }
        });
    }
}