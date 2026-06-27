// ===== GRMS Homepage JavaScript =====

document.addEventListener('DOMContentLoaded', function() {
    
    console.log('GRMS Homepage JS loaded');
    
    // ===== 1. AOS INITIALIZATION (Animate on Scroll) =====
    if (typeof AOS !== 'undefined') {
        AOS.init({
            duration: 800,
            once: true,
            offset: 100,
            easing: 'ease-in-out'
        });
        console.log('AOS initialized');
    }
    
    // ===== 2. NAVBAR SCROLL EFFECT =====
    const navbar = document.getElementById('navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('scrolled');
            } else {
                navbar.classList.remove('scrolled');
            }
        });
    }
    
    // ===== 3. MOBILE MENU TOGGLE =====
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('show');
        });
        
        // Close mobile menu when clicking a link
        const mobileLinks = document.querySelectorAll('.mobile-link');
        mobileLinks.forEach(link => {
            link.addEventListener('click', function() {
                mobileMenu.classList.remove('show');
            });
        });
    }
    
    // ===== 4. COUNTER ANIMATION FOR STATS =====
    const counters = document.querySelectorAll('.stat-item h3, .counter-value');
    
    const animateCounter = (counter) => {
        const target = parseInt(counter.innerText);
        if (target > 0 && target < 10000) {
            let count = 0;
            const speed = Math.floor(1500 / target);
            const update = () => {
                if (count < target) {
                    count++;
                    counter.innerText = count;
                    setTimeout(update, speed);
                } else {
                    counter.innerText = target;
                }
            };
            update();
        }
    };
    
    // Intersection Observer for counters
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });
    
    counters.forEach(counter => {
        counterObserver.observe(counter);
    });
    
    // ===== 5. SMOOTH SCROLL FOR ANCHOR LINKS =====
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId !== '#' && targetId !== '#home') {
                const target = document.querySelector(targetId);
                if (target) {
                    e.preventDefault();
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
    
    // ===== 6. ADD ANIMATION CLASSES ON SCROLL =====
    const animatedElements = document.querySelectorAll('.feature-card, .help-card, .stat-item');
    
    const elementObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                elementObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.2 });
    
    animatedElements.forEach(el => {
        el.classList.add('animate-on-scroll');
        elementObserver.observe(el);
    });
    
    // ===== 7. LOGIN BUTTON CLICK EFFECT =====
    const loginBtn = document.querySelector('.login-btn');
    if (loginBtn) {
        loginBtn.addEventListener('click', function(e) {
            console.log('Login button clicked - redirecting to login page');
            // Animation effect
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    }
    
    // ===== 8. IMAGE LOADING ANIMATION =====
    const images = document.querySelectorAll('.about-image img, .logo');
    images.forEach(img => {
        img.addEventListener('load', function() {
            this.classList.add('loaded');
        });
        if (img.complete) {
            img.classList.add('loaded');
        }
    });
    
    // ===== 9. ADD HOVER EFFECT TO STAT ITEMS =====
    const statItems = document.querySelectorAll('.stat-item');
    statItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transition = 'all 0.3s ease';
        });
    });
    
    // ===== 10. SCROLL TO TOP BUTTON (Optional) =====
    // Create scroll to top button if not exists
    if (!document.querySelector('.scroll-top-btn')) {
        const scrollBtn = document.createElement('button');
        scrollBtn.innerHTML = '<i class="fas fa-arrow-up"></i>';
        scrollBtn.className = 'scroll-top-btn';
        scrollBtn.style.cssText = `
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 45px;
            height: 45px;
            background: #2e7d32;
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            opacity: 0;
            visibility: hidden;
            transition: all 0.3s ease;
            z-index: 999;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        `;
        document.body.appendChild(scrollBtn);
        
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                scrollBtn.style.opacity = '1';
                scrollBtn.style.visibility = 'visible';
            } else {
                scrollBtn.style.opacity = '0';
                scrollBtn.style.visibility = 'hidden';
            }
        });
        
        scrollBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // ===== 11. PRELOADER (Optional) =====
    // Add loading class to body
    window.addEventListener('load', function() {
        document.body.classList.add('loaded');
    });
    
    // ===== 12. LOG CONSOLE MESSAGE =====
    console.log('GRMS Homepage fully loaded and ready!');
});

// ===== ADDITIONAL HELPER FUNCTIONS =====

// Function to check if element is in viewport
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// Function to add animation class when element comes into view
function addAnimationOnScroll(element, animationClass) {
    if (isInViewport(element)) {
        element.classList.add(animationClass);
    } else {
        window.addEventListener('scroll', function onScroll() {
            if (isInViewport(element)) {
                element.classList.add(animationClass);
                window.removeEventListener('scroll', onScroll);
            }
        });
    }
}