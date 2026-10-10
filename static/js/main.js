document.addEventListener('DOMContentLoaded', () => {
    updateCartCount();
    setupLiveSearch();
});

function updateCartCount() {
    const countElement = document.getElementById('cart-count');
    if (!countElement) return;

    const realCount = countElement.getAttribute('data-count');
    if (realCount) {
        countElement.innerText = realCount;
    }
}

/**
 * Toast Notification System
 */
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerText = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s ease forwards';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * AJAX Cart Actions
 */
async function ajaxAddToCart(productId) {
    try {
        const response = await fetch(`/add_to_cart/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.status === 'success') {
            showToast(`${data.product_name} added to cart!`);
            updateCartCount();
            // Update the data-count attribute to maintain state
            const countElement = document.getElementById('cart-count');
            if (countElement) {
                countElement.setAttribute('data-count', data.cart_count);
            }
        } else {
            showToast(data.message || 'Failed to add item to cart', 'error');
        }
    } catch (error) {
        console.error('Error adding to cart:', error);
        showToast('An unexpected error occurred', 'error');
    }
}

async function ajaxRemoveFromCart(productId) {
    try {
        const response = await fetch(`/remove_from_cart/${productId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });

        const data = await response.json();

        if (data.status === 'success') {
            showToast('Item removed from cart');
            updateCartCount();
            const countElement = document.getElementById('cart-count');
            if (countElement) {
                countElement.setAttribute('data-count', data.cart_count);
            }
        } else {
            showToast(data.message || 'Failed to remove item from cart', 'error');
        }
    } catch (error) {
        console.error('Error removing from cart:', error);
        showToast('An unexpected error occurred', 'error');
    }
}

/**
 * Live Search Implementation
 */
function setupLiveSearch() {
    const searchInput = document.getElementById('live-search');
    if (!searchInput) return;

    let timeout = null;
    searchInput.addEventListener('input', () => {
        clearTimeout(timeout);
        timeout = setTimeout(async () => {
            const query = searchInput.value.trim();
            if (query.length < 2) return;

            try {
                const response = await fetch(`/api/search/?q=${encodeURIComponent(query)}`);
                const data = await response.json();

                // This assumes a product grid exists on the page
                const grid = document.querySelector('.product-grid');
                if (grid) {
                    updateProductGrid(data.products);
                }
            } catch (error) {
                console.error('Live search error:', error);
            }
        }, 300);
    });
}

function updateProductGrid(products) {
    const grid = document.querySelector('.product-grid');
    if (!grid) return;

    if (products.length === 0) {
        grid.innerHTML = '<p>No products found.</p>';
        return;
    }

    grid.innerHTML = products.map(product => `
        <div class="product-card">
            <img src="${product.image || '/static/images/default-product.png'}" alt="${product.name}">
            <h3>${product.name}</h3>
            <p>₹${product.price}</p>
            <button class="btn" onclick="ajaxAddToCart(${product.id})">Add to Cart</button>
        </div>
    `).join('');
}

/**
 * Utility: Get CSRF Token from Cookie
 */
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
