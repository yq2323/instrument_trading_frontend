// 购物车相关JavaScript
// API基础URL已在config.js中定义

// 获取购物车
async function getCart() {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/cart`, {
            credentials: 'include'
        });
        const data = await response.json();
        
        if (data.success) {
            return data;
        }
        return null;
    } catch (error) {
        console.error('获取购物车失败:', error);
        return null;
    }
}

// 添加到购物车
async function addToCart(instrumentId, quantity = 1) {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/cart/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                instrument_id: instrumentId,
                quantity: quantity
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('已添加到购物车', 'success');
            updateCartCount();
            return true;
        } else {
            showNotification(data.message || '添加失败', 'error');
            return false;
        }
    } catch (error) {
        console.error('添加到购物车失败:', error);
        showNotification('网络错误，请稍后重试', 'error');
        return false;
    }
}

// 从购物车移除
async function removeFromCart(itemId) {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/cart/${itemId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('已从购物车移除', 'success');
            updateCartCount();
            return true;
        } else {
            showNotification(data.message || '移除失败', 'error');
            return false;
        }
    } catch (error) {
        console.error('从购物车移除失败:', error);
        showNotification('网络错误，请稍后重试', 'error');
        return false;
    }
}

// 更新购物车商品数量
async function updateCartItemQuantity(itemId, quantity) {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/cart/${itemId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ quantity: quantity })
        });
        
        const data = await response.json();
        
        if (data.success) {
            return true;
        } else {
            showNotification(data.message || '更新失败', 'error');
            return false;
        }
    } catch (error) {
        console.error('更新购物车商品数量失败:', error);
        showNotification('网络错误，请稍后重试', 'error');
        return false;
    }
}

// 更新购物车数量显示
async function updateCartCount() {
    const cartCount = document.querySelector('.cart-count');
    if (!cartCount) return;
    
    const cart = await getCart();
    if (cart && cart.items) {
        cartCount.textContent = cart.items.length;
    } else {
        cartCount.textContent = '0';
    }
}

// 清空购物车
async function clearCart() {
    try {
        const cart = await getCart();
        if (!cart || !cart.items || cart.items.length === 0) return;
        
        // 逐一删除购物车商品
        const deletePromises = cart.items.map(item => 
            removeFromCart(item.id)
        );
        
        await Promise.all(deletePromises);
        showNotification('购物车已清空', 'success');
        updateCartCount();
        
        // 重新加载购物车页面
        if (window.location.pathname.includes('cart.html')) {
            setTimeout(() => location.reload(), 500);
        }
    } catch (error) {
        console.error('清空购物车失败:', error);
        showNotification('清空失败，请重试', 'error');
    }
}

// 渲染购物车页面
async function renderCartPage() {
    const cartContainer = document.getElementById('cartContainer');
    if (!cartContainer) return;
    
    try {
        const cart = await getCart();
        
        if (!cart || !cart.items || cart.items.length === 0) {
            cartContainer.innerHTML = `
                <div class="empty-cart">
                    <i class="fas fa-shopping-cart"></i>
                    <h3>购物车是空的</h3>
                    <p>去发现一些好乐器吧！</p>
                    <a href="index.html" class="btn btn-primary">去逛逛</a>
                </div>
            `;
            return;
        }
        
        // 渲染购物车商品列表
        let html = `
            <div class="cart-header">
                <h2>我的购物车 (${cart.items.length}件商品)</h2>
                <button class="btn btn-outline" onclick="clearCart()">
                    <i class="fas fa-trash"></i> 清空购物车
                </button>
            </div>
            
            <div class="cart-items">
                ${cart.items.map(item => `
                    <div class="cart-item" data-item-id="${item.id}">
                        <div class="item-info">
                            <img src="${item.instrument.main_image || 'images/default-instrument.jpg'}" 
                                 alt="${item.instrument.title}"
                                 onerror="this.src='images/default-instrument.jpg'">
                            <div>
                                <h4>${item.instrument.title}</h4>
                                <p class="category">${item.instrument.category_name || '未分类'}</p>
                                <p class="condition">成色：${getConditionText(item.instrument.condition)}</p>
                            </div>
                        </div>
                        
                        <div class="item-price">
                            ${formatPrice(item.instrument.price)}
                        </div>
                        
                        <div class="item-quantity">
                            <button class="quantity-btn" onclick="updateQuantity(${item.id}, ${item.quantity - 1})" ${item.quantity <= 1 ? 'disabled' : ''}>
                                <i class="fas fa-minus"></i>
                            </button>
                            <span class="quantity">${item.quantity}</span>
                            <button class="quantity-btn" onclick="updateQuantity(${item.id}, ${item.quantity + 1})">
                                <i class="fas fa-plus"></i>
                            </button>
                        </div>
                        
                        <div class="item-total">
                            ${formatPrice(item.instrument.price * item.quantity)}
                        </div>
                        
                        <div class="item-actions">
                            <button class="btn btn-outline btn-sm" onclick="removeItem(${item.id})">
                                <i class="fas fa-trash"></i>
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
            
            <div class="cart-summary">
                <div class="summary-details">
                    <div class="summary-row">
                        <span>商品总数：</span>
                        <span>${cart.items.length}件</span>
                    </div>
                    <div class="summary-row">
                        <span>商品总价：</span>
                        <span>${formatPrice(cart.total_price)}</span>
                    </div>
                    <div class="summary-row total">
                        <span>应付总额：</span>
                        <span class="total-price">${formatPrice(cart.total_price)}</span>
                    </div>
                </div>
                
                <div class="summary-actions">
                    <a href="index.html" class="btn btn-outline">继续购物</a>
                    <button class="btn btn-primary" onclick="checkout()">去结算</button>
                </div>
            </div>
        `;
        
        cartContainer.innerHTML = html;
        
    } catch (error) {
        console.error('渲染购物车失败:', error);
        cartContainer.innerHTML = '<p class="error">加载购物车失败，请稍后重试</p>';
    }
}

// 更新商品数量
async function updateQuantity(itemId, newQuantity) {
    if (newQuantity < 1) return;
    
    const success = await updateCartItemQuantity(itemId, newQuantity);
    if (success) {
        // 更新UI
        const quantitySpan = document.querySelector(`.cart-item[data-item-id="${itemId}"] .quantity`);
        if (quantitySpan) {
            quantitySpan.textContent = newQuantity;
        }
        
        // 重新计算总价
        updateCartTotals();
    }
}

// 移除商品
async function removeItem(itemId) {
    const success = await removeFromCart(itemId);
    if (success) {
        // 移除UI元素
        const itemElement = document.querySelector(`.cart-item[data-item-id="${itemId}"]`);
        if (itemElement) {
            itemElement.remove();
        }
        
        // 更新总计
        updateCartTotals();
        
        // 如果购物车为空，显示空状态
        const cartItems = document.querySelectorAll('.cart-item');
        if (cartItems.length === 0) {
            renderCartPage();
        }
    }
}

// 更新购物车总计
async function updateCartTotals() {
    const cart = await getCart();
    if (!cart || !cart.items) return;
    
    // 重新计算总价
    let totalPrice = 0;
    cart.items.forEach(item => {
        const quantity = parseInt(document.querySelector(`.cart-item[data-item-id="${item.id}"] .quantity`)?.textContent || item.quantity);
        totalPrice += item.instrument.price * quantity;
    });
    
    // 更新UI
    const totalPriceElement = document.querySelector('.total-price');
    if (totalPriceElement) {
        totalPriceElement.textContent = formatPrice(totalPrice);
    }
}

// 结算功能
async function checkout() {
    try {
        const cart = await getCart();
        if (!cart || !cart.items || cart.items.length === 0) {
            showNotification('购物车是空的', 'error');
            return;
        }
        
        // 跳转到订单确认页面
        window.location.href = 'checkout.html';
        
    } catch (error) {
        console.error('结算失败:', error);
        showNotification('结算失败，请重试', 'error');
    }
}

// 工具函数
function formatPrice(price) {
    return '¥' + parseFloat(price).toFixed(2);
}

function getConditionText(condition) {
    const conditions = {
        'new': '全新',
        'like_new': '几乎全新',
        'good': '良好',
        'fair': '一般',
        'poor': '较差'
    };
    return conditions[condition] || '良好';
}

function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">&times;</button>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 3000);
}

// 页面初始化
document.addEventListener('DOMContentLoaded', function() {
    // 如果是购物车页面，渲染购物车
    if (window.location.pathname.includes('cart.html')) {
        renderCartPage();
    }
    
    // 更新购物车数量
    updateCartCount();
    
    // 绑定添加到购物车按钮
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('add-to-cart-btn') || 
            e.target.closest('.add-to-cart-btn')) {
            e.preventDefault();
            
            const button = e.target.classList.contains('add-to-cart-btn') ? 
                          e.target : e.target.closest('.add-to-cart-btn');
            
            const instrumentId = button.dataset.instrumentId;
            const quantity = parseInt(button.dataset.quantity) || 1;
            
            if (instrumentId) {
                addToCart(parseInt(instrumentId), quantity);
            }
        }
    });
});