// API 接口函数

// API基础URL已在config.js中定义

// 获取CSRF令牌
async function getCsrfToken() {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/auth/csrf_token`, {
            method: 'GET',
            credentials: 'include'
        });
        
        if (!response.ok) {
            throw new Error('获取CSRF令牌失败');
        }
        
        const data = await response.json();
        return data.csrf_token;
    } catch (error) {
        console.error('获取CSRF令牌失败:', error);
        return null;
    }
}

// 通用请求函数
async function request(endpoint, options = {}) {
    const csrfToken = await getCsrfToken();
    
    const defaultOptions = {
        credentials: 'include',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        }
    };
    
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    try {
        const response = await fetch(`${CONFIG.API_BASE}${endpoint}`, mergedOptions);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `请求失败: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API请求失败:', error);
        throw error;
    }
}

// 上传文件的请求函数
async function uploadRequest(endpoint, formData, options = {}) {
    const csrfToken = await getCsrfToken();
    
    const defaultOptions = {
        credentials: 'include',
        headers: {
            'X-CSRFToken': csrfToken
        }
    };
    
    const mergedOptions = {
        ...defaultOptions,
        ...options,
        body: formData,
        headers: {
            ...defaultOptions.headers,
            ...options.headers
        }
    };
    
    // 移除Content-Type，让浏览器自动设置
    delete mergedOptions.headers['Content-Type'];
    
    try {
        const response = await fetch(`${CONFIG.API_BASE}${endpoint}`, mergedOptions);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `上传失败: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('文件上传失败:', error);
        throw error;
    }
}

// 认证相关API

// 登录
async function login(username, password) {
    return await request('/auth/login', {
        method: 'POST',
        body: JSON.stringify({ username, password })
    });
}

// 注册
async function register(data) {
    return await request('/auth/register', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

// 退出登录
async function logout() {
    return await request('/auth/logout', {
        method: 'POST'
    });
}

// 检查登录状态
async function checkAuth() {
    return await request('/auth/check_auth', {
        method: 'GET'
    });
}

// 更新用户资料
async function updateProfile(data, avatarFile = null) {
    const formData = new FormData();
    
    // 添加文本字段
    for (const [key, value] of Object.entries(data)) {
        formData.append(key, value);
    }
    
    // 添加头像文件
    if (avatarFile) {
        formData.append('avatar', avatarFile);
    }
    
    return await uploadRequest('/auth/update_profile', formData, {
        method: 'POST'
    });
}

// 乐器相关API

// 获取乐器列表
async function getInstruments(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = `/instruments${queryString ? `?${queryString}` : ''}`;
    
    return await request(endpoint, {
        method: 'GET'
    });
}

// 获取乐器详情
async function getInstrumentDetail(id) {
    return await request(`/instruments/${id}`, {
        method: 'GET'
    });
}

// 发布乐器
async function publishInstrument(data, images) {
    const formData = new FormData();
    
    // 添加文本字段
    for (const [key, value] of Object.entries(data)) {
        formData.append(key, value);
    }
    
    // 添加图片文件
    images.forEach((image, index) => {
        formData.append('images', image);
    });
    
    return await uploadRequest('/instruments', formData, {
        method: 'POST'
    });
}

// 更新乐器
async function updateInstrument(id, data, images = []) {
    const formData = new FormData();
    
    // 添加文本字段
    for (const [key, value] of Object.entries(data)) {
        formData.append(key, value);
    }
    
    // 添加图片文件
    images.forEach((image, index) => {
        formData.append('images', image);
    });
    
    return await uploadRequest(`/instruments/${id}`, formData, {
        method: 'PUT'
    });
}

// 删除乐器
async function deleteInstrument(id) {
    return await request(`/instruments/${id}`, {
        method: 'DELETE'
    });
}

// 收藏相关API

// 收藏乐器
async function favoriteInstrument(id) {
    return await request(`/instruments/${id}/favorite`, {
        method: 'POST'
    });
}

// 取消收藏
async function unfavoriteInstrument(id) {
    return await request(`/instruments/${id}/unfavorite`, {
        method: 'POST'
    });
}

// 获取用户收藏列表
async function getUserFavorites() {
    return await request('/user/favorites', {
        method: 'GET'
    });
}

// 订单相关API

// 创建订单
async function createOrder(data) {
    return await request('/orders', {
        method: 'POST',
        body: JSON.stringify(data)
    });
}

// 获取用户订单列表
async function getUserOrders() {
    return await request('/user/orders', {
        method: 'GET'
    });
}

// 更新订单状态
async function updateOrderStatus(id, status) {
    return await request(`/orders/${id}/status`, {
        method: 'PUT',
        body: JSON.stringify({ status })
    });
}

// 分类相关API

// 获取分类列表
async function getCategories() {
    return await request('/categories', {
        method: 'GET'
    });
}

// 搜索相关API

// 搜索乐器
async function searchInstruments(query, params = {}) {
    const searchParams = new URLSearchParams({ query, ...params }).toString();
    return await request(`/search?${searchParams}`, {
        method: 'GET'
    });
}

// 导出API函数
window.api = {
    // 认证
    login,
    register,
    logout,
    checkAuth,
    updateProfile,
    
    // 乐器
    getInstruments,
    getInstrumentDetail,
    publishInstrument,
    updateInstrument,
    deleteInstrument,
    
    // 收藏
    favoriteInstrument,
    unfavoriteInstrument,
    getUserFavorites,
    
    // 订单
    createOrder,
    getUserOrders,
    updateOrderStatus,
    
    // 分类
    getCategories,
    
    // 搜索
    searchInstruments,
    
    // 工具函数
    getCsrfToken,
    request,
    uploadRequest
};