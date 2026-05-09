// Supervisor Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Supervisor Dashboard JS Loaded');
    
    initMobileMenu();
    initLogoutConfirm();
    initActionButtons();
});

// Mobile Menu Toggle
function initMobileMenu() {
    const sidebar = document.querySelector('.sidebar');
    if (!sidebar) return;
    
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'mobile-toggle';
    toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
    toggleBtn.style.cssText = `
        position: fixed;
        top: 1rem;
        left: 1rem;
        z-index: 1001;
        background: #2e7d32;
        color: white;
        border: none;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        cursor: pointer;
        display: none;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2);
        align-items: center;
        justify-content: center;
    `;
    
    document.body.appendChild(toggleBtn);
    
    function checkMobile() {
        if (window.innerWidth <= 768) {
            toggleBtn.style.display = 'flex';
        } else {
            toggleBtn.style.display = 'none';
            sidebar.classList.remove('active');
        }
    }
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    
    toggleBtn.addEventListener('click', function() {
        sidebar.classList.toggle('active');
        this.innerHTML = sidebar.classList.contains('active') ? 
            '<i class="fas fa-times"></i>' : '<i class="fas fa-bars"></i>';
    });
    
    const navLinks = document.querySelectorAll('.nav-menu a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 768) {
                sidebar.classList.remove('active');
                toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
            }
        });
    });
}

// Logout Confirmation
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

// Action Buttons Click Effect
function initActionButtons() {
    const actionBtns = document.querySelectorAll('.btn-action, .view-all');
    actionBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (this.classList.contains('btn-action') && this.querySelector('.fa-plus, .fa-calendar-plus')) {
                // No loading effect for now
            }
        });
    });
}