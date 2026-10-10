// Use mock data from main.js (in a real app, this would be an API call)
const products = [
    { id: 1, name: 'Smartphone X', price: 699, image: 'https://images.unsplash.com/photo-1511707171634-5883666ecf7a?auto=format&fit=crop&w=300&q=80', description: 'The Smartphone X is the pinnacle of mobile technology. Featuring a stunning 6.7-inch OLED display, a revolutionary triple-lens camera system, and the lightning-fast Quantum chip, it is designed for those who demand the best in every aspect of their digital life.' },
    { id: 2, name: 'Wireless Headphones', price: 199, image: 'https://images.unsplash.com/photo-1505740420928-5e5647145e3d?auto=format&fit=crop&w=300&q=80', description: 'Immerse yourself in pure sound. Our Wireless Headphones offer industry-leading noise cancellation and high-fidelity audio that brings every note to life. With 40 hours of battery life and ergonomic design, your music never has to stop.' },
    { id: 3, name: 'Smart Watch', price: 249, image: 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?auto=format&fit=crop&w=300&q=80', description: 'Stay connected and healthy. The Smart Watch tracks your heart rate, sleep patterns, and daily activity with pinpoint accuracy. Sync seamlessly with your phone to receive notifications and calls right on your wrist.' },
    { id: 4, name: 'Bluetooth Speaker', price: 89, image: 'https://images.unsplash.com/photo-1589003077474-5767526도?auto=format&fit=crop&w=300&q=80', description: 'Bring the party anywhere. This Bluetooth Speaker delivers crystal clear highs and deep, booming bass in a compact, water-resistant shell. Perfect for outdoor adventures, beach days, or simply filling your room with sound.' },
];

function loadProductDetails() {
    const params = new URLSearchParams(window.location.search);
    const productId = params.get('id'); // For static demo, we can use search param ?id=1

    // Fallback for demo: if no ID, try to get it from path (which requires a server)
    // Since we are doing frontend only now, we'll look for ?id=X
    const product = products.find(p => p.id == productId);
    const container = document.getElementById('product-detail');

    if (!product) {
        container.innerHTML = '<h2>Product not found!</h2><a href="/" class="btn">Back to Home</a>';
        return;
    }

    container.innerHTML = `
        <div class="product-detail-image">
            <img src="${product.image}" alt="${product.name}">
        </div>
        <div class="product-detail-info">
            <h1>${product.name}</h1>
            <p class="price-tag">$${product.price}</p>
            <p class="description">${product.description}</p>
            <button class="btn" onclick="addToCart(${product.id})">Add to Cart</button>
        </div>
    `;
}

function addToCart(productId) {
    let cart = JSON.parse(localStorage.getItem('cart')) || [];
    const product = products.find(p => p.id === productId);

    if (product) {
        cart.push(product);
        localStorage.setItem('cart', JSON.stringify(cart));
        alert(`${product.name} added to cart!`);
        updateCartCount();
    }
}

document.addEventListener('DOMContentLoaded', () => {
    loadProductDetails();
});