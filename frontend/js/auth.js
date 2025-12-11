// 认证相关JavaScript
// API基础URL已在config.js中定义

// 获取CSRF token
async function getCsrfToken() {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/auth/csrf_token`, {
            credentials: 'include'
        });
        const data = await response.json();
        return data.csrf_token;
    } catch (error) {
        console.error('获取CSRF token失败:', error);
        return null;
    }
}

// 登录功能
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value.trim();
    const password = document.getElementById('password').value;
    const remember = document.getElementById('remember').checked;
    
    if (!username || !password) {
        showNotification('请输入用户名和密码', 'error');
        return;
    }
    
    const loginBtn = document.getElementById('loginBtn');
    const loginText = document.getElementById('loginText');
    const loginLoading = document.getElementById('loginLoading');
    
    // 显示加载状态
    if (loginText) loginText.style.display = 'none';
    if (loginLoading) loginLoading.style.display = 'inline-block';
    loginBtn.disabled = true;
    
    try {
        // 获取CSRF token
        const csrfToken = await getCsrfToken();
        
        // 添加超时处理
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超时
        
        const response = await fetch(`${CONFIG.API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'include',
            body: JSON.stringify({
                username: username,
                password: password,
                remember: remember
            }),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `网络错误，状态码: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('登录成功！正在跳转到个人中心...', 'success');
            
            // 保存用户信息到sessionStorage
            sessionStorage.setItem('user', JSON.stringify(data.user));
            
            // 重定向到用户界面或原页面
            setTimeout(() => {
                const redirectUrl = sessionStorage.getItem('redirectUrl') || 'user.html';
                sessionStorage.removeItem('redirectUrl');
                window.location.href = redirectUrl;
            }, 1000);
        } else {
            showNotification(data.message || '登录失败', 'error');
        }
    } catch (error) {
        console.error('登录失败:', error);
        if (error.name === 'AbortError') {
            showNotification('请求超时，请检查网络连接', 'error');
        } else {
            showNotification(error.message || '网络错误，请稍后重试', 'error');
        }
    } finally {
        // 恢复按钮状态
        if (loginText) loginText.style.display = 'inline-block';
        if (loginLoading) loginLoading.style.display = 'none';
        loginBtn.disabled = false;
    }
}

// 注册功能
async function handleRegister(event) {
    event.preventDefault();
    
    // 先调用register.html中的validateForm函数进行前端验证
    if (typeof validateForm === 'function') {
        const isValid = validateForm();
        if (!isValid) {
            return;
        }
    }
    
    const username = document.getElementById('username').value.trim();
    const email = document.getElementById('email').value.trim();
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    const phone = document.getElementById('phone')?.value.trim() || '';
    const realName = document.getElementById('real_name')?.value.trim() || '';
    const studentId = document.getElementById('student_id')?.value.trim() || '';
    const school = document.getElementById('school')?.value.trim() || '';
    
    const registerBtn = document.getElementById('registerBtn');
    const originalText = registerBtn.innerHTML;
    registerBtn.disabled = true;
    registerBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 注册中...';
    
    try {
        // 获取CSRF token
        const csrfToken = await getCsrfToken();
        if (!csrfToken) {
            throw new Error('获取安全令牌失败');
        }
        
        // 添加超时处理
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000); // 10秒超时
        
        const response = await fetch(`${CONFIG.API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            credentials: 'include',
            body: JSON.stringify({
                username: username,
                email: email,
                password: password,
                confirm_password: confirmPassword,
                phone: phone,
                real_name: realName,
                student_id: studentId,
                school: school
            }),
            signal: controller.signal
        });
        
        clearTimeout(timeoutId);
        
        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.message || `网络错误，状态码: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('注册成功！正在跳转到登录页面...', 'success');
            
            // 保存用户信息
            sessionStorage.setItem('user', JSON.stringify(data.user));
            
            // 跳转到登录页面
            setTimeout(() => {
                window.location.href = 'login.html?message=' + encodeURIComponent('注册成功，请登录');
            }, 1500);
        } else {
            showNotification(data.message || '注册失败', 'error');
        }
    } catch (error) {
        console.error('注册失败:', error);
        if (error.name === 'AbortError') {
            showNotification('请求超时，请检查网络连接', 'error');
        } else {
            showNotification(error.message || '网络错误，请稍后重试', 'error');
        }
    } finally {
        registerBtn.disabled = false;
        registerBtn.innerHTML = originalText;
    }
}

// 检查登录状态
async function checkAuth() {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/auth/check_auth`, {
            credentials: 'include'
        });
        const data = await response.json();
        
        if (data.authenticated) {
            return data.user;
        }
        return null;
    } catch (error) {
        console.error('检查登录状态失败:', error);
        return null;
    }
}

// 退出登录
async function logout() {
    try {
        const response = await fetch(`${CONFIG.API_BASE}/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        });
        const data = await response.json();
        
        if (data.success) {
            // 清除本地存储的用户信息
            sessionStorage.removeItem('user');
            localStorage.removeItem('user');
            
            showNotification('已退出登录', 'success');
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 1000);
        }
    } catch (error) {
        console.error('退出登录失败:', error);
        showNotification('退出失败，请重试', 'error');
    }
}

// 更新用户资料
async function updateProfile(event) {
    event.preventDefault();
    
    const formData = new FormData(event.target);
    
    const updateBtn = event.target.querySelector('button[type="submit"]');
    const originalText = updateBtn.innerHTML;
    updateBtn.disabled = true;
    updateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 更新中...';
    
    try {
        const response = await fetch(`${CONFIG.API_BASE}/auth/update_profile`, {
            method: 'POST',
            credentials: 'include',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('资料更新成功', 'success');
            
            // 更新本地存储的用户信息
            const user = JSON.parse(sessionStorage.getItem('user') || '{}');
            if (formData.get('real_name')) user.real_name = formData.get('real_name');
            if (formData.get('phone')) user.phone = formData.get('phone');
            if (formData.get('student_id')) user.student_id = formData.get('student_id');
            sessionStorage.setItem('user', JSON.stringify(user));
            
            // 重新加载页面
            setTimeout(() => {
                location.reload();
            }, 1500);
        } else {
            showNotification(data.message || '更新失败', 'error');
        }
    } catch (error) {
        console.error('更新资料失败:', error);
        showNotification('网络错误，请稍后重试', 'error');
    } finally {
        updateBtn.disabled = false;
        updateBtn.innerHTML = originalText;
    }
}

// 修改密码
async function changePassword(event) {
    event.preventDefault();
    
    const oldPassword = document.getElementById('old_password').value;
    const newPassword = document.getElementById('new_password').value;
    const confirmPassword = document.getElementById('confirm_password').value;
    
    if (!oldPassword || !newPassword || !confirmPassword) {
        showNotification('请填写所有密码字段', 'error');
        return;
    }
    
    if (newPassword !== confirmPassword) {
        showNotification('两次输入的新密码不一致', 'error');
        return;
    }
    
    if (newPassword.length < 6) {
        showNotification('新密码长度至少为6位', 'error');
        return;
    }
    
    const changeBtn = event.target.querySelector('button[type="submit"]');
    const originalText = changeBtn.innerHTML;
    changeBtn.disabled = true;
    changeBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 修改中...';
    
    try {
        const response = await fetch(`${CONFIG.API_BASE}/auth/change_password`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                old_password: oldPassword,
                new_password: newPassword,
                confirm_password: confirmPassword
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('密码修改成功，请重新登录', 'success');
            
            // 退出登录并跳转到登录页
            setTimeout(() => {
                logout();
            }, 1500);
        } else {
            showNotification(data.message || '修改失败', 'error');
        }
    } catch (error) {
        console.error('修改密码失败:', error);
        showNotification('网络错误，请稍后重试', 'error');
    } finally {
        changeBtn.disabled = false;
        changeBtn.innerHTML = originalText;
    }
}

// 显示/隐藏密码
function togglePasswordVisibility(button) {
    const input = button.parentElement.previousElementSibling;
    const icon = button.querySelector('i');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    }
}

// 保护需要登录的页面
function protectPage() {
    const publicPages = ['login.html', 'register.html', 'index.html', 'detail.html', 'search.html'];
    const currentPage = window.location.pathname.split('/').pop();
    
    // 如果是公开页面，不进行保护
    if (publicPages.includes(currentPage)) {
        return;
    }
    
    checkAuth().then(user => {
        if (!user) {
            // 保存当前页面地址，登录后返回
            sessionStorage.setItem('redirectUrl', window.location.href);
            window.location.href = 'login.html';
        }
    });
}

// 初始化页面
document.addEventListener('DOMContentLoaded', function() {
    // 绑定表单提交事件
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', handleRegister);
    }
    
    const profileForm = document.getElementById('profileForm');
    if (profileForm) {
        profileForm.addEventListener('submit', updateProfile);
    }
    
    const passwordForm = document.getElementById('passwordForm');
    if (passwordForm) {
        passwordForm.addEventListener('submit', changePassword);
    }
    
    // 绑定退出登录按钮
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            logout();
        });
    }
    
    // 绑定显示/隐藏密码按钮
    document.querySelectorAll('.toggle-password, #togglePassword').forEach(button => {
        button.addEventListener('click', function() {
            togglePasswordVisibility(this);
        });
    });
    
    // 保护需要登录的页面
    protectPage();
    
    // 如果已登录，显示用户信息
    checkAuth().then(user => {
        if (user) {
            updateNavbarForLoggedInUser(user);
        }
    });
});

// 更新导航栏显示登录用户
function updateNavbarForLoggedInUser(user) {
    const authButtons = document.getElementById('authButtons');
    const userMenu = document.getElementById('userMenu');
    const usernameSpan = document.querySelector('#username:not(input)');
    
    if (authButtons) authButtons.style.display = 'none';
    if (userMenu) userMenu.style.display = 'block';
    if (usernameSpan) usernameSpan.textContent = user.username;
}

// 显示通知
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