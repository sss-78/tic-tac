// Payroll App - Client-side JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Auto-hide flash messages after 5 seconds
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(function(message) {
        setTimeout(function() {
            message.style.opacity = '0';
            setTimeout(function() {
                message.style.display = 'none';
            }, 300);
        }, 5000);
    });

    // Form validation enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Processing...';
                
                // Re-enable button after 3 seconds to prevent permanent disable
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.textContent = submitBtn.getAttribute('data-original-text') || 'Submit';
                }, 3000);
            }
        });
        
        // Store original button text
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.setAttribute('data-original-text', submitBtn.textContent);
        }
    });

    // Hours input formatting for timesheet
    const hoursInputs = document.querySelectorAll('.hours-input');
    hoursInputs.forEach(function(input) {
        input.addEventListener('input', function(e) {
            let value = e.target.value;
            
            // Remove any non-numeric characters except decimal point
            value = value.replace(/[^0-9.]/g, '');
            
            // Ensure only one decimal point
            const parts = value.split('.');
            if (parts.length > 2) {
                value = parts[0] + '.' + parts.slice(1).join('');
            }
            
            // Limit to 2 decimal places
            if (parts[1] && parts[1].length > 2) {
                value = parts[0] + '.' + parts[1].substring(0, 2);
            }
            
            // Ensure value doesn't exceed 24
            const numValue = parseFloat(value);
            if (numValue > 24) {
                value = '24.00';
            }
            
            e.target.value = value;
        });

        // Round to nearest 0.25 on blur for better UX
        input.addEventListener('blur', function(e) {
            const value = parseFloat(e.target.value);
            if (!isNaN(value)) {
                const rounded = Math.round(value * 4) / 4;
                e.target.value = rounded > 0 ? rounded.toFixed(2) : '';
            }
        });
    });

    // Add keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + S to save timesheet (if on timesheet page)
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            const timesheetForm = document.querySelector('.timesheet-form');
            if (timesheetForm) {
                e.preventDefault();
                timesheetForm.submit();
            }
        }
        
        // Ctrl/Cmd + D to go to dashboard (if logged in)
        if ((e.ctrlKey || e.metaKey) && e.key === 'd') {
            const dashboardLink = document.querySelector('a[href*="dashboard"]');
            if (dashboardLink) {
                e.preventDefault();
                window.location.href = dashboardLink.href;
            }
        }
    });

    // Improve accessibility - add focus indicators
    const focusableElements = document.querySelectorAll('input, button, select, a, textarea');
    focusableElements.forEach(function(element) {
        element.addEventListener('focus', function() {
            this.classList.add('focused');
        });
        
        element.addEventListener('blur', function() {
            this.classList.remove('focused');
        });
    });

    // Add loading state for navigation links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            if (!this.classList.contains('logout-btn')) {
                this.style.opacity = '0.6';
            }
        });
    });

    // Calculate total hours in real-time on timesheet
    if (hoursInputs.length > 0) {
        function updateTotalHours() {
            let total = 0;
            hoursInputs.forEach(function(input) {
                const value = parseFloat(input.value) || 0;
                total += value;
            });
            
            // Update or create total display
            let totalDisplay = document.getElementById('hours-total');
            if (!totalDisplay) {
                totalDisplay = document.createElement('div');
                totalDisplay.id = 'hours-total';
                totalDisplay.className = 'hours-total';
                totalDisplay.innerHTML = '<strong>Total Hours: <span id="total-value">0.00</span></strong>';
                
                const formActions = document.querySelector('.form-actions');
                if (formActions) {
                    formActions.parentNode.insertBefore(totalDisplay, formActions);
                }
            }
            
            const totalValue = document.getElementById('total-value');
            if (totalValue) {
                totalValue.textContent = total.toFixed(2);
            }
        }
        
        hoursInputs.forEach(function(input) {
            input.addEventListener('input', updateTotalHours);
            input.addEventListener('blur', updateTotalHours);
        });
        
        // Initial calculation
        updateTotalHours();
    }
});

// Add styles for dynamically created elements
const style = document.createElement('style');
style.textContent = `
    .focused {
        outline: 2px solid #007bff;
        outline-offset: 2px;
    }
    
    .hours-total {
        background: #e9ecef;
        padding: 1rem;
        border-radius: 6px;
        text-align: center;
        margin: 1rem 0;
        font-size: 1.1rem;
        color: #333;
    }
    
    .hours-total #total-value {
        color: #007bff;
        font-size: 1.2rem;
    }
`;
document.head.appendChild(style);