/**
 * PolicyAssist AI - Main Client Script
 * Handles global interactions, mobile navigation, toast notifications,
 * and comparison storage helpers.
 */

// Mobile Navigation Toggle
document.addEventListener('DOMContentLoaded', () => {
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');

    if (navToggle && navLinks) {
        navToggle.addEventListener('click', () => {
            navLinks.classList.toggle('active');
        });
    }
});

// Toast Notification System
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'fa-circle-info';
    if (type === 'success') icon = 'fa-circle-check';
    if (type === 'error') icon = 'fa-circle-exclamation';
    if (type === 'warning') icon = 'fa-triangle-exclamation';

    toast.innerHTML = `<i class="fa-solid ${icon}"></i> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(10px)';
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}

// Format Currency in Indian Rupees (INR)
function formatCurrency(amount) {
    if (isNaN(amount) || amount === null) return '₹0';
    return '₹' + Number(amount).toLocaleString('en-IN');
}

// Comparison Storage Helpers (up to 3 policies)
const ComparisonStore = {
    getKey: () => 'policyassist_compare_ids',
    getIds: () => {
        try {
            return JSON.parse(localStorage.getItem(ComparisonStore.getKey()) || '[]');
        } catch {
            return [];
        }
    },
    addId: (id) => {
        const ids = ComparisonStore.getIds();
        if (!ids.includes(id)) {
            if (ids.length >= 3) {
                showToast('You can compare up to 3 policies at once.', 'warning');
                return false;
            }
            ids.push(id);
            localStorage.setItem(ComparisonStore.getKey(), JSON.stringify(ids));
            showToast(`Added ${id} to comparison.`, 'success');
            return true;
        }
        return false;
    },
    removeId: (id) => {
        let ids = ComparisonStore.getIds();
        ids = ids.filter(item => item !== id);
        localStorage.setItem(ComparisonStore.getKey(), JSON.stringify(ids));
        showToast(`Removed ${id} from comparison.`, 'info');
    },
    setIds: (ids) => {
        localStorage.setItem(ComparisonStore.getKey(), JSON.stringify(ids.slice(0, 3)));
    },
    clear: () => {
        localStorage.removeItem(ComparisonStore.getKey());
    }
};
