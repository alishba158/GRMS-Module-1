// Admin Dashboard JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Admin Dashboard JS Loaded');
    
    initMobileMenu();
    initLogoutConfirm();
    initScrollAnimations();
    initCounterAnimation();
    initQuickActions();
});

// ===== Mobile Menu Toggle =====
function initMobileMenu() {
    const sidebar = document.querySelector('.sidebar');
    if (!sidebar) return;
    
    // Create toggle button if not exists
    if (document.querySelector('.mobile-toggle')) return;
    
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
    
    toggleBtn.addEventListener('click', function() {
        sidebar.classList.toggle('active');
        this.innerHTML = sidebar.classList.contains('active') ? 
            '<i class="fas fa-times"></i>' : '<i class="fas fa-bars"></i>';
    });
    
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
    
    // Close sidebar when clicking a nav link on mobile
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

// ===== Logout Confirmation =====
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

// ===== Scroll Animations for List Items =====
function initScrollAnimations() {
    const items = document.querySelectorAll('.list-item, .extension-card');
    
    if (items.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });
    
    items.forEach(item => {
        item.style.opacity = '0';
        item.style.transform = 'translateY(20px)';
        item.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(item);
    });
}

// ===== Counter Animation for Stats =====
function initCounterAnimation() {
    const counters = document.querySelectorAll('.counter, .stat-value');
    
    counters.forEach(counter => {
        const target = parseInt(counter.innerText);
        if (isNaN(target) || target === 0) return;
        
        if (counter.classList.contains('animated')) return;
        counter.classList.add('animated');
        
        let count = 0;
        const speed = Math.floor(1500 / target);
        
        const updateCount = () => {
            if (count < target) {
                count++;
                counter.innerText = count;
                setTimeout(updateCount, speed);
            } else {
                counter.innerText = target;
            }
        };
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    updateCount();
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.5 });
        
        observer.observe(counter);
    });
}

// ===== Quick Actions Button Effects =====
function initQuickActions() {
    const actionBtns = document.querySelectorAll('.quick-action-btn, .btn-action, .view-all');
    
    actionBtns.forEach(btn => {
        btn.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
        });
        
        btn.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
        
        // Add click effect for buttons that might have forms
        if (btn.tagName === 'BUTTON' || btn.classList.contains('btn-action')) {
            btn.addEventListener('click', function(e) {
                if (this.querySelector('.fa-plus, .fa-user-plus, .fa-chalkboard-teacher')) {
                    // Just a visual effect, don't prevent default
                    this.style.transform = 'scale(0.95)';
                    setTimeout(() => {
                        this.style.transform = '';
                    }, 200);
                }
            });
        }
    });
}

// Mobile sidebar toggle
document.addEventListener('DOMContentLoaded', function() {
    const mobileToggle = document.getElementById('mobileToggle');
    const sidebar = document.getElementById('sidebar');
    if (mobileToggle && sidebar) {
        mobileToggle.addEventListener('click', function() {
            sidebar.classList.toggle('active');
        });
    }
});