// 乐器相关JavaScript
// API基础URL已在config.js中定义

// 加载乐器详情
async function loadInstrumentDetail(instrumentId) {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/instruments/${instrumentId}`);
        const data = await response.json();
        
        if (data.success && data.instrument) {
            renderInstrumentDetail(data.instrument);
            loadRelatedInstruments(data.instrument.category_id, instrumentId);
        } else {
            showNotification('乐器不存在或已被下架', 'error');
            setTimeout(() => window.location.href = 'index.html', 2000);
        }
    } catch (error) {
        console.error('加载乐器详情失败:', error);
        showNotification('加载失败，请稍后重试', 'error');
    }
}

// 渲染乐器详情
function renderInstrumentDetail(instrument) {
    // 更新页面标题
    document.title = `${instrument.title} - 校园乐器汇`;
    
    // 更新面包屑导航
    const categoryName = document.getElementById('categoryName');
    if (categoryName) {
        categoryName.textContent = instrument.category_name || instrument.title;
    }
    
    // 更新主图
    const mainImage = document.getElementById('mainImage');
    if (mainImage) {
        const mainImg = instrument.images.find(img => img.is_main) || instrument.images[0];
        if (mainImg) {
            mainImage.innerHTML = `
                <img src="${mainImg.full_url}" alt="${instrument.title}" id="currentImage">
            `;
        }
    }
    
    // 更新缩略图
    const thumbnailList = document.getElementById('thumbnailList');
    if (thumbnailList && instrument.images.length > 0) {
        thumbnailList.innerHTML = instrument.images.map((img, index) => `
            <div class="thumbnail ${index === 0 ? 'active' : ''}" onclick="changeMainImage('${img.full_url}', this)">
                <img src="${img.full_url}" alt="缩略图 ${index + 1}">
            </div>
        `).join('');
    }
    
    // 更新乐器信息
    document.getElementById('productTitle').textContent = instrument.title;
    document.getElementById('viewCount').textContent = instrument.view_count;
    document.getElementById('favoriteCount').textContent = instrument.favorite_count;
    document.getElementById('currentPrice').textContent = formatPrice(instrument.price);
    
    const originalPrice = document.getElementById('originalPrice');
    if (instrument.original_price) {
        originalPrice.textContent = formatPrice(instrument.original_price);
        originalPrice.style.display = 'inline';
    }
    
    document.getElementById('descriptionContent').textContent = instrument.description;
    document.getElementById('brandValue').textContent = instrument.brand || '未知';
    document.getElementById('modelValue').textContent = instrument.model || '未知';
    document.getElementById('conditionValue').textContent = getConditionText(instrument.condition);
    document.getElementById('locationValue').textContent = instrument.location || '未设置';
    
    // 更新成色标签
    const conditionBadge = document.getElementById('conditionBadge');
    if (conditionBadge) {
        conditionBadge.textContent = getConditionText(instrument.condition);
        conditionBadge.className = `condition-badge ${instrument.condition}`;
    }
    
    // 更新音频试听
    const audioPreview = document.getElementById('audioPreview');
    const audioPlayer = document.getElementById('audioPlayer');
    if (instrument.audio_url && audioPreview && audioPlayer) {
        audioPreview.style.display = 'block';
        audioPlayer.src = instrument.audio_url;
    }
    
    // 更新卖家信息
    renderSellerInfo(instrument.user);
    
    // 更新收藏按钮状态
    updateFavoriteButton(instrument.is_favorited);
    
    // 绑定收藏按钮事件
    const favoriteBtn = document.getElementById('favoriteBtn');
    if (favoriteBtn) {
        favoriteBtn.onclick = () => toggleFavorite(instrument.id);
    }
    
    // 绑定添加到购物车按钮
    const addToCartBtn = document.getElementById('addToCartBtn');
    if (addToCartBtn) {
        addToCartBtn.onclick = () => addToCartFromDetail(instrument.id);
    }
    
    // 绑定立即购买按钮
    const buyNowBtn = document.getElementById('buyNowBtn');
    if (buyNowBtn) {
        buyNowBtn.onclick = () => buyNow(instrument.id);
    }
}

// 渲染卖家信息
function renderSellerInfo(seller) {
    const sellerCard = document.getElementById('sellerCard');
    if (!sellerCard || !seller) return;
    
    sellerCard.innerHTML = `
        <div class="seller-profile">
            <img src="${seller.avatar || 'images/default-avatar.svg'}" 
                 alt="${seller.real_name || seller.username}"
                 class="seller-avatar">
            <div class="seller-info">
                <h4>${seller.real_name || seller.username}</h4>
                <div class="seller-stats">
                    <span class="credit-score">
                        <i class="fas fa-star"></i> 信用分: ${seller.credit_score}
                    </span>
                </div>
            </div>
        </div>
        <div class="seller-actions">
            <button class="btn btn-outline btn-sm" onclick="contactSeller(${seller.id})">
                <i class="fas fa-comment"></i> 联系卖家
            </button>
        </div>
    `;
}

// 加载相关乐器
async function loadRelatedInstruments(categoryId, excludeId, limit = 4) {
    const relatedGrid = document.getElementById('relatedGrid');
    if (!relatedGrid) return;
    
    try {
        const response = await fetch(`${CONFIG.API_BASE}/instruments?category_id=${categoryId}&page_size=${limit}`);
        const data = await response.json();
        
        if (data.success && data.instruments) {
            // 过滤掉当前乐器
            const related = data.instruments.filter(inst => inst.id !== excludeId).slice(0, limit);
            
            if (related.length > 0) {
                relatedGrid.innerHTML = related.map(instrument => `
                    <div class="instrument-card" onclick="window.location.href='detail.html?id=${instrument.id}'">
                        <div class="instrument-image">
                            <img src="${instrument.main_image || 'images/default-instrument.jpg'}" 
                                 alt="${instrument.title}"
                                 onerror="this.src='images/default-instrument.jpg'">
                            <span class="condition-badge ${instrument.condition}">
                                ${getConditionText(instrument.condition)}
                            </span>
                        </div>
                        <div class="instrument-info">
                            <h4 class="title">${instrument.title}</h4>
                            <div class="price">${formatPrice(instrument.price)}</div>
                        </div>
                    </div>
                `).join('');
            } else {
                relatedGrid.innerHTML = '<p class="no-data">暂无相关乐器</p>';
            }
        }
    } catch (error) {
        console.error('加载相关乐器失败:', error);
        relatedGrid.innerHTML = '<p class="error">加载失败</p>';
    }
}

// 切换主图
function changeMainImage(imageUrl, thumbnail) {
    const currentImage = document.getElementById('currentImage');
    if (currentImage) {
        currentImage.src = imageUrl;
    }
    
    // 更新缩略图选中状态
    document.querySelectorAll('.thumbnail').forEach(thumb => {
        thumb.classList.remove('active');
    });
    thumbnail.classList.add('active');
}

// 切换收藏状态
async function toggleFavorite(instrumentId) {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/instruments/${instrumentId}/favorite`, {
            method: 'POST',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message, 'success');
            updateFavoriteButton(data.is_favorited);
            
            // 更新收藏数
            const favoriteCount = document.getElementById('favoriteCount');
            if (favoriteCount) {
                favoriteCount.textContent = data.favorite_count;
            }
        } else {
            showNotification(data.message || '操作失败', 'error');
        }
    } catch (error) {
        console.error('收藏操作失败:', error);
        showNotification('请先登录', 'error');
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 1500);
    }
}

// 更新收藏按钮状态
function updateFavoriteButton(isFavorited) {
    const favoriteBtn = document.getElementById('favoriteBtn');
    if (!favoriteBtn) return;
    
    if (isFavorited) {
        favoriteBtn.innerHTML = '<i class="fas fa-heart"></i> 已收藏';
        favoriteBtn.classList.add('favorited');
    } else {
        favoriteBtn.innerHTML = '<i class="far fa-heart"></i> 收藏';
        favoriteBtn.classList.remove('favorited');
    }
}

// 从详情页添加到购物车
async function addToCartFromDetail(instrumentId) {
    const quantity = parseInt(document.getElementById('quantity')?.value) || 1;
    const success = await addToCart(instrumentId, quantity);
    
    if (success) {
        // 显示成功消息
        showNotification('已添加到购物车', 'success');
    }
}

// 立即购买
async function buyNow(instrumentId) {
    const quantity = parseInt(document.getElementById('quantity')?.value) || 1;
    
    try {
        const response = await fetch(`${CONFIG.API_BASE}/orders`, {
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
            showNotification('订单创建成功', 'success');
            setTimeout(() => {
                window.location.href = `order.html?order_id=${data.order_id}`;
            }, 1500);
        } else {
            showNotification(data.message || '购买失败', 'error');
        }
    } catch (error) {
        console.error('立即购买失败:', error);
        showNotification('请先登录', 'error');
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 1500);
    }
}

// 联系卖家
function contactSeller(sellerId) {
    const message = prompt('请输入您想对卖家说的话：');
    if (message && message.trim()) {
        // 这里可以实现发送消息的功能
        alert('消息已发送给卖家');
    }
}

// 发布乐器
async function publishInstrument(formData) {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/instruments`, {
            method: 'POST',
            credentials: 'include',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('乐器发布成功！', 'success');
            setTimeout(() => {
                window.location.href = `detail.html?id=${data.instrument_id}`;
            }, 1500);
        } else {
            showNotification(data.message || '发布失败', 'error');
        }
    } catch (error) {
        console.error('发布乐器失败:', error);
        showNotification('发布失败，请检查网络', 'error');
    }
}

// 更新乐器信息
async function updateInstrument(instrumentId, formData) {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/instruments/${instrumentId}`, {
            method: 'PUT',
            credentials: 'include',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('乐器信息更新成功！', 'success');
            setTimeout(() => {
                window.location.href = `detail.html?id=${instrumentId}`;
            }, 1500);
        } else {
            showNotification(data.message || '更新失败', 'error');
        }
    } catch (error) {
        console.error('更新乐器失败:', error);
        showNotification('更新失败，请检查网络', 'error');
    }
}

// 删除乐器
async function deleteInstrument(instrumentId) {
    if (!confirm('确定要删除这个乐器吗？此操作不可撤销。')) {
        return;
    }
    
    try {
        const response = await fetch(`${CONFIG.API_BASE}/instruments/${instrumentId}`, {
            method: 'DELETE',
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('乐器已删除', 'success');
            setTimeout(() => {
                window.location.href = 'user.html';
            }, 1500);
        } else {
            showNotification(data.message || '删除失败', 'error');
        }
    } catch (error) {
        console.error('删除乐器失败:', error);
        showNotification('删除失败，请检查网络', 'error');
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
    // 如果是详情页，加载乐器详情
    const urlParams = new URLSearchParams(window.location.search);
    const instrumentId = urlParams.get('id');
    
    if (instrumentId && window.location.pathname.includes('detail.html')) {
        loadInstrumentDetail(parseInt(instrumentId));
    }
    
    // 如果是发布页，初始化表单
    if (window.location.pathname.includes('publish.html')) {
        initPublishForm();
    }
    
    // 如果是编辑页，加载乐器数据
    const editInstrumentId = urlParams.get('edit');
    if (editInstrumentId && window.location.pathname.includes('publish.html')) {
        loadInstrumentForEdit(parseInt(editInstrumentId));
    }
});

// 初始化发布表单
async function initPublishForm() {
    // 加载分类
    await loadCategoriesForForm();
    
    // 绑定表单提交事件
    const publishForm = document.getElementById('publishForm');
    if (publishForm) {
        publishForm.addEventListener('submit', handlePublishSubmit);
    }
    
    // 图片预览功能
    const imageInput = document.getElementById('images');
    if (imageInput) {
        imageInput.addEventListener('change', previewImages);
    }
}

// 加载分类到表单
async function loadCategoriesForForm() {
    const categorySelect = document.getElementById('category_id');
    if (!categorySelect) return;
    
    try {
        const response = await fetch(`${CONFIG.API_BASE}/categories`);
        const data = await response.json();
        
        if (data.success && data.categories) {
            categorySelect.innerHTML = data.categories.map(category => `
                <option value="${category.id}">${category.name}</option>
            `).join('');
        }
    } catch (error) {
        console.error('加载分类失败:', error);
    }
}

// 预览图片
function previewImages(event) {
    const previewContainer = document.getElementById('imagePreview');
    if (!previewContainer) return;
    
    previewContainer.innerHTML = '';
    const files = event.target.files;
    
    for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const reader = new FileReader();
        
        reader.onload = function(e) {
            const img = document.createElement('img');
            img.src = e.target.result;
            img.className = 'preview-image';
            img.dataset.index = i;
            
            previewContainer.appendChild(img);
        }
        
        reader.readAsDataURL(file);
    }
}

// 处理发布表单提交
async function handlePublishSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const formData = new FormData(form);
    
    // 添加主图索引
    const mainImageIndex = parseInt(formData.get('main_image_index') || 0);
    formData.set('main_image_index', mainImageIndex);
    
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 发布中...';
    
    const instrumentId = form.dataset.instrumentId;
    
    try {
        if (instrumentId) {
            await updateInstrument(instrumentId, formData);
        } else {
            await publishInstrument(formData);
        }
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

// 加载要编辑的乐器
async function loadInstrumentForEdit(instrumentId) {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/instruments/${instrumentId}`);
        const data = await response.json();
        
        if (data.success && data.instrument) {
            populateEditForm(data.instrument);
        }
    } catch (error) {
        console.error('加载乐器编辑数据失败:', error);
        showNotification('加载失败', 'error');
    }
}

// 填充编辑表单
function populateEditForm(instrument) {
    const form = document.getElementById('publishForm');
    if (!form) return;
    
    form.dataset.instrumentId = instrument.id;
    
    // 设置表单值
    document.getElementById('title').value = instrument.title;
    document.getElementById('description').value = instrument.description;
    document.getElementById('price').value = instrument.price;
    document.getElementById('original_price').value = instrument.original_price || '';
    document.getElementById('category_id').value = instrument.category_id;
    document.getElementById('condition').value = instrument.condition;
    document.getElementById('brand').value = instrument.brand || '';
    document.getElementById('model').value = instrument.model || '';
    document.getElementById('location').value = instrument.location || '';
    
    // 更新标题和按钮文本
    const pageTitle = document.querySelector('.page-title');
    if (pageTitle) {
        pageTitle.textContent = '编辑乐器';
    }
    
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
        submitBtn.textContent = '更新乐器';
    }
    
    // 显示现有图片
    if (instrument.images && instrument.images.length > 0) {
        const previewContainer = document.getElementById('imagePreview');
        if (previewContainer) {
            previewContainer.innerHTML = instrument.images.map((img, index) => `
                <img src="${img.full_url}" class="preview-image" data-index="${index}">
            `).join('');
        }
    }
}