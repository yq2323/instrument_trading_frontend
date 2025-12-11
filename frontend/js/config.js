// 全局配置文件
const CONFIG = {
    // 自动检测API地址，如果是本地开发则使用localhost，否则使用当前域名
    API_BASE: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
        ? 'http://localhost:5000/api' 
        : `${window.location.protocol}//${window.location.host}/api`
};