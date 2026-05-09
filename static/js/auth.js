document.addEventListener('DOMContentLoaded', function() {
    // ===== Mobile Menu Toggle =====
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');
    
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('show');
            const icon = this.querySelector('i');
            if (mobileMenu.classList.contains('show')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-times');
            } else {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    }
    
    // Close mobile menu when clicking a link
    const mobileLinks = document.querySelectorAll('.mobile-link, .mobile-login');
    mobileLinks.forEach(link => {
        link.addEventListener('click', function() {
            mobileMenu.classList.remove('show');
            const icon = mobileMenuBtn.querySelector('i');
            if (icon) {
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    });
    
    // ===== Navbar Scroll Effect =====
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', function() {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // ===== Form Validation =====
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const username = this.querySelector('input[name="username"]').value;
            const password = this.querySelector('input[name="password"]').value;
            
            if (!username || !password) {
                e.preventDefault();
                showNotification('Please fill in all fields', 'error');
            } else {
                const submitBtn = this.querySelector('button[type="submit"]');
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Logging in...';
                submitBtn.disabled = true;
            }
        });
    }
    
    // ===== Show/Hide Password (optional) =====
    const passwordInput = document.querySelector('input[type="password"]');
    if (passwordInput) {
        const wrapper = passwordInput.parentElement;
        const toggleBtn = document.createElement('span');
        toggleBtn.innerHTML = '<i class="far fa-eye"></i>';
        toggleBtn.style.cssText = `
            position: absolute;
            right: 15px;
            top: 50%;
            transform: translateY(-50%);
            cursor: pointer;
            color: var(--primary-green);
            font-size: 1.2rem;
            z-index: 2;
        `;
        wrapper.appendChild(toggleBtn);
        
        toggleBtn.addEventListener('click', function() {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            this.innerHTML = type === 'password' ? '<i class="far fa-eye"></i>' : '<i class="far fa-eye-slash"></i>';
        });
    }
    
    // ===== Notification System =====
    window.showNotification = function(message, type = 'success') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <span>${message}</span>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: ${type === 'success' ? 'var(--primary-green)' : '#f44336'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 50px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 9999;
            animation: slideInRight 0.3s ease;
            font-weight: 500;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    };
    
    // Add CSS animations
    const style = document.createElement('style');
    style.innerHTML = `
        @keyframes slideInRight {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes slideOutRight {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
});


// ===== Register Form Validation with Guidance =====
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    const password = document.getElementById('password');
    const confirmPassword = document.getElementById('confirmPassword');
    const matchGuidance = document.getElementById('passwordMatchGuidance');
    const registerBtn = document.getElementById('registerBtn');
    
    function checkPasswordMatch() {
        if (password.value && confirmPassword.value) {
            if (password.value === confirmPassword.value) {
                matchGuidance.classList.add('match');
                matchGuidance.innerHTML = '<i class="fas fa-check-circle"></i> ✓ Passwords match';
                registerBtn.disabled = false;
            } else {
                matchGuidance.classList.remove('match');
                matchGuidance.innerHTML = '<i class="fas fa-exclamation-circle"></i> ✗ Passwords do not match';
                registerBtn.disabled = true;
            }
        } else {
            matchGuidance.classList.remove('match');
            matchGuidance.innerHTML = '<i class="fas fa-circle"></i> Passwords must match';
            registerBtn.disabled = true;
        }
    }
    
    password.addEventListener('keyup', checkPasswordMatch);
    confirmPassword.addEventListener('keyup', checkPasswordMatch);
    
    // Real-time validation for other fields (optional)
    const username = document.querySelector('input[name="username"]');
    if (username) {
        username.addEventListener('keyup', function() {
            const guidance = this.closest('.input-group').nextElementSibling;
            if (this.value.length < 3) {
                guidance.style.color = '#f44336';
                guidance.innerHTML = '<i class="fas fa-exclamation-circle"></i> Username must be at least 3 characters';
            } else if (!/^[a-zA-Z0-9_]+$/.test(this.value)) {
                guidance.style.color = '#f44336';
                guidance.innerHTML = '<i class="fas fa-exclamation-circle"></i> Only letters, numbers, and underscore allowed';
            } else {
                guidance.style.color = 'var(--text-light)';
                guidance.innerHTML = '<i class="fas fa-info-circle"></i> Choose a unique username (e.g., alishba_123)';
            }
        });
    }
    
    const email = document.querySelector('input[name="email"]');
    if (email) {
        email.addEventListener('keyup', function() {
            const guidance = this.closest('.input-group').nextElementSibling;
            if (this.value && !this.value.includes('@')) {
                guidance.style.color = '#f44336';
                guidance.innerHTML = '<i class="fas fa-exclamation-circle"></i> Please enter a valid email address';
            } else {
                guidance.style.color = 'var(--text-light)';
                guidance.innerHTML = '<i class="fas fa-info-circle"></i> Use your university email or personal email';
            }
        });
    }
    
    // Form submit validation
    registerForm.addEventListener('submit', function(e) {
        // Check all validations
        const username = document.querySelector('input[name="username"]').value;
        const email = document.querySelector('input[name="email"]').value;
        const passwordValue = password.value;
        const confirmValue = confirmPassword.value;
        
        if (username.length < 3) {
            e.preventDefault();
            showNotification('Username must be at least 3 characters', 'error');
            return;
        }
        
        if (!/^[a-zA-Z0-9_]+$/.test(username)) {
            e.preventDefault();
            showNotification('Username can only contain letters, numbers, and underscore', 'error');
            return;
        }
        
        if (!email.includes('@')) {
            e.preventDefault();
            showNotification('Please enter a valid email address', 'error');
            return;
        }
        
        if (passwordValue.length < 8) {
            e.preventDefault();
            showNotification('Password must be at least 8 characters', 'error');
            return;
        }
        
        if (passwordValue !== confirmValue) {
            e.preventDefault();
            showNotification('Passwords do not match!', 'error');
            return;
        }
        
        // If all validations pass
        registerBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating Account...';
        registerBtn.disabled = true;
    });
}