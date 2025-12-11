// 主应用JavaScript

// 工具函数
function showNotification(message, type = 'success') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">&times;</button>
    `;
    document.body.appendChild(notification);
    setTimeout(() => notification.remove(), 3000);
}

function formatPrice(price) {
    return '¥' + parseFloat(price).toFixed(2);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('zh-CN');
}

// 检查登录状态
async function checkAuthStatus() {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/auth/check_auth`, {
            credentials: 'include'
        });
        const data = await response.json();
        
        if (data.authenticated) {
            updateUserUI(data.user);
            return data.user;
        } else {
            clearUserUI();
            return null;
        }
    } catch (error) {
        console.error('检查登录状态失败:', error);
        return null;
    }
}

function updateUserUI(user) {
    const userBtn = document.getElementById('userBtn');
    const authButtons = document.getElementById('authButtons');
    const usernameSpan = document.getElementById('username');
    
    if (userBtn && authButtons && usernameSpan) {
        userBtn.style.display = 'flex';
        authButtons.style.display = 'none';
        usernameSpan.textContent = user.username;
    }
}

function clearUserUI() {
    const userBtn = document.getElementById('userBtn');
    const authButtons = document.getElementById('authButtons');
    
    if (userBtn && authButtons) {
        userBtn.style.display = 'none';
        authButtons.style.display = 'flex';
    }
}

// 页面初始化
document.addEventListener('DOMContentLoaded', function() {
    // 检查登录状态
    checkAuthStatus();
    
    // 绑定事件
    bindEvents();
    
    // 加载数据
    loadData();
});

function bindEvents() {
    // 搜索功能
    const searchBtn = document.getElementById('searchBtn');
    const searchInput = document.getElementById('searchInput');
    
    if (searchBtn && searchInput) {
        searchBtn.addEventListener('click', handleSearch);
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') handleSearch();
        });
    }
    
    // 登出功能
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', handleLogout);
    }
    
    // 用户菜单
    const userBtn = document.getElementById('userBtn');
    const userMenu = document.getElementById('userMenu');
    
    if (userBtn && userMenu) {
        userBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            userMenu.classList.toggle('show');
        });
        
        // 点击其他地方关闭菜单
        document.addEventListener('click', function() {
            userMenu.classList.remove('show');
        });
    }
}

async function handleSearch() {
    const searchInput = document.getElementById('searchInput');
    if (!searchInput) return;
    
    const keyword = searchInput.value.trim();
    if (keyword) {
        window.location.href = `search.html?q=${encodeURIComponent(keyword)}`;
    }
}

async function handleLogout(e) {
    e.preventDefault();
    
    try {
        const response = await fetch(`${CONFIG.API_BASE}/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        const data = await response.json();
        
        if (data.success) {
            showNotification('已退出登录', 'success');
            setTimeout(() => {
                window.location.href = 'index.html';
            }, 1000);
        }
    } catch (error) {
        console.error('登出失败:', error);
        showNotification('登出失败', 'error');
    }
}

// 加载页面数据
async function loadData() {
    // 加载分类
    await loadCategories();
    
    // 加载热门乐器
    await loadHotInstruments();
    
    // 加载最新乐器
    await loadLatestInstruments();
}

async function loadCategories() {
    const categoriesGrid = document.getElementById('categoriesGrid');
    if (!categoriesGrid) return;
    
    try {
        const response = await fetch(`${CONFIG.API_BASE}/categories`);
        const data = await response.json();
        
        if (data.success && data.categories) {
            categoriesGrid.innerHTML = data.categories.map(category => `
                <div class="category-card" onclick="filterByCategory(${category.id})">
                    <div class="category-icon">
                        <i class="${category.icon || 'fas fa-guitar'}"></i>
                    </div>
                    <h3>${category.name}</h3>
                    <p>${category.instrument_count || 0}件商品</p>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('加载分类失败:', error);
    }
}

async function loadHotInstruments() {
    const hotInstruments = document.getElementById('hotInstruments');
    if (!hotInstruments) return;
    
    try {
        const response = await fetch(`${CONFIG.API_BASE}/instruments/hot?limit=6`);
        const data = await response.json();
        
        if (data.success && data.instruments) {
            hotInstruments.innerHTML = data.instruments.map(instrument => `
                <div class="instrument-card" onclick="viewInstrument(${instrument.id})">
                    <div class="instrument-image">
                        <img src="${instrument.main_image || 'images/default-instrument.jpg'}" 
                             alt="${instrument.title}"
                             onerror="this.src='images/default-instrument.jpg'">
                        <span class="condition-badge ${instrument.condition}">
                            ${getConditionText(instrument.condition)}
                        </span>
                    </div>
                    <div class="instrument-info">
                        <h3 class="title">${instrument.title}</h3>
                        <p class="description">${instrument.description ? instrument.description.substring(0, 50) + '...' : '暂无描述'}</p>
                        <div class="price">${formatPrice(instrument.price)}</div>
                        <div class="meta">
                            <span><i class="fas fa-eye"></i> ${instrument.view_count}</span>
                            <span><i class="fas fa-heart"></i> ${instrument.favorite_count}</span>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('加载热门乐器失败:', error);
    }
}

async function loadLatestInstruments() {
    const instrumentsGrid = document.getElementById('instrumentsGrid');
    if (!instrumentsGrid) return;
    
    try {
        const response = await fetch(`${CONFIG.API_BASE}/instruments?page_size=12`);
        const data = await response.json();
        
        if (data.success && data.instruments) {
            instrumentsGrid.innerHTML = data.instruments.map(instrument => `
                <div class="instrument-card" onclick="viewInstrument(${instrument.id})">
                    <div class="instrument-image">
                        <img src="${instrument.main_image || 'images/default-instrument.jpg'}" 
                             alt="${instrument.title}"
                             onerror="this.src='images/default-instrument.jpg'">
                        <span class="condition-badge ${instrument.condition}">
                            ${getConditionText(instrument.condition)}
                        </span>
                    </div>
                    <div class="instrument-info">
                        <h3 class="title">${instrument.title}</h3>
                        <p class="description">${instrument.description ? instrument.description.substring(0, 50) + '...' : '暂无描述'}</p>
                        <div class="price">${formatPrice(instrument.price)}</div>
                        <div class="meta">
                            <span><i class="fas fa-eye"></i> ${instrument.view_count}</span>
                            <span><i class="fas fa-heart"></i> ${instrument.favorite_count}</span>
                        </div>
                    </div>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('加载乐器失败:', error);
    }
}

function filterByCategory(categoryId) {
    window.location.href = `search.html?category=${categoryId}`;
}

function viewInstrument(instrumentId) {
    window.location.href = `detail.html?id=${instrumentId}`;
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