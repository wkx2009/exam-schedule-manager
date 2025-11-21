// 考试数据
let examData = [];
let currentJsonUrl = '';

// DOM元素
const examTableBody = document.getElementById('examTableBody');
const formatModal = document.getElementById('formatModal');
const addExamModal = document.getElementById('addExamModal');
const examForm = document.getElementById('examForm');
const jsonUrlInput = document.getElementById('jsonUrl');
const loadDataBtn = document.getElementById('loadDataBtn');
const refreshBtn = document.getElementById('refreshBtn');
const showFormatBtn = document.getElementById('showFormatBtn');
const exportBtn = document.getElementById('exportBtn');
const loadStatus = document.getElementById('loadStatus');
const lastUpdateSpan = document.getElementById('lastUpdate');
const dataSourceSpan = document.getElementById('dataSource');

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    // 初始化时钟
    updateClock();
    setInterval(updateClock, 1000);
    
    // 尝试从默认URL加载数据
    loadExamData('data.json');
    
    // 事件监听器
    loadDataBtn.addEventListener('click', handleLoadData);
    refreshBtn.addEventListener('click', handleRefresh);
    showFormatBtn.addEventListener('click', showFormatModal);
    exportBtn.addEventListener('click', exportToJson);
    document.getElementById('closeFormatModal').addEventListener('click', hideFormatModal);
    document.getElementById('closeFormatBtn').addEventListener('click', hideFormatModal);
    document.getElementById('addExamBtn').addEventListener('click', showAddExamModal);
    document.getElementById('closeAddExamModal').addEventListener('click', hideAddExamModal);
    examForm.addEventListener('submit', handleExamFormSubmit);
    
    // 点击模态框外部关闭
    window.addEventListener('click', function(event) {
        if (event.target === formatModal) {
            hideFormatModal();
        }
        if (event.target === addExamModal) {
            hideAddExamModal();
        }
    });
});

// 获取网络时间函数
async function getNetworkTime() {
    try {
        const response = await fetch('https://worldtimeapi.org/api/ip');
        const data = await response.json();
        return new Date(data.datetime);
    } catch (error) {
        console.error('获取网络时间失败，使用本地时间:', error);
        return new Date();
    }
}

// 更新时钟显示
function updateClock() {
    getNetworkTime().then(networkTime => {
        const now = networkTime;
        
        // 更新日期显示
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const weekdays = ['日', '一', '二', '三', '四', '五', '六'];
        const weekday = weekdays[now.getDay()];
        document.getElementById('date').textContent = `${year}年${month}月${day}日 星期${weekday}`;
        
        // 更新时间显示
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        const seconds = String(now.getSeconds()).padStart(2, '0');
        document.getElementById('clock').textContent = `${hours}:${minutes}:${seconds}`;
    });
}

// 加载考试数据
async function loadExamData(url) {
    showLoading();
    currentJsonUrl = url;
    
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`HTTP错误! 状态: ${response.status}`);
        }
        const data = await response.json();
        
        if (Array.isArray(data)) {
            examData = data;
            renderExamTable();
            updateLastUpdateTime();
            dataSourceSpan.textContent = url;
            showSuccess('数据加载成功！');
        } else {
            throw new Error('JSON格式错误：数据不是数组');
        }
    } catch (error) {
        console.error('加载数据失败:', error);
        showError(`加载数据失败: ${error.message}`);
        // 使用示例数据作为后备
        loadFallbackData();
    }
}

// 加载后备数据（示例数据）
function loadFallbackData() {
    examData = [
        {
            subject: "示例",
            date: "1145-1-4",
            startTime: "00:00",
            endTime: "23:59",
            paperInfo: "该试卷共xx张xx页xx道大题"
        }
    ];
    renderExamTable();
    updateLastUpdateTime();
    dataSourceSpan.textContent = '示例数据';
}

// 显示加载状态
function showLoading() {
    loadStatus.innerHTML = '<div class="loading">正在加载数据...</div>';
}

// 显示成功消息
function showSuccess(message) {
    loadStatus.innerHTML = `<div style="color: #27ae60; padding: 10px;">✓ ${message}</div>`;
}

// 显示错误消息
function showError(message) {
    loadStatus.innerHTML = `<div class="error">✗ ${message}</div>`;
}

// 渲染考试表格
function renderExamTable() {
    if (examData.length === 0) {
        examTableBody.innerHTML = '<tr><td colspan="4" class="loading">暂无考试数据</td></tr>';
        return;
    }
    
    examTableBody.innerHTML = '';
    
    examData.forEach((exam, index) => {
        const row = document.createElement('tr');
        
        // 格式化考试时间
        const formattedDate = formatDate(exam.date);
        const examTime = `${formattedDate} ${exam.startTime}-${exam.endTime}`;
        
        // 计算考试状态
        const status = calculateExamStatus(exam.date, exam.startTime, exam.endTime);
        
        row.innerHTML = `
            <td>${exam.subject}</td>
            <td>${examTime}</td>
            <td>${exam.paperInfo}</td>
            <td><span class="status ${status.class}">${status.text}</span></td>
        `;
        
        examTableBody.appendChild(row);
    });
}

// 格式化日期
function formatDate(dateString) {
    const date = new Date(dateString);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}年${month}月${day}日`;
}

// 计算考试状态
function calculateExamStatus(date, startTime, endTime) {
    const now = new Date();
    const startDateTime = new Date(`${date}T${startTime}`);
    const endDateTime = new Date(`${date}T${endTime}`);
    
    if (now < startDateTime) {
        return { class: 'upcoming', text: '即将开始' };
    } else if (now >= startDateTime && now <= endDateTime) {
        return { class: 'ongoing', text: '进行中' };
    } else {
        return { class: 'completed', text: '已结束' };
    }
}

// 处理加载数据
function handleLoadData() {
    const url = jsonUrlInput.value.trim();
    if (!url) {
        showError('请输入JSON文件URL');
        return;
    }
    loadExamData(url);
}

// 处理刷新
function handleRefresh() {
    if (currentJsonUrl) {
        loadExamData(currentJsonUrl);
    } else {
        showError('没有可刷新的数据源');
    }
}

// 显示JSON格式模态框
function showFormatModal() {
    formatModal.style.display = 'flex';
}

// 隐藏JSON格式模态框
function hideFormatModal() {
    formatModal.style.display = 'none';
}

// 显示添加考试模态框
function showAddExamModal() {
    addExamModal.style.display = 'flex';
    // 清空表单
    examForm.reset();
}

// 隐藏添加考试模态框
function hideAddExamModal() {
    addExamModal.style.display = 'none';
}

// 处理考试表单提交
function handleExamFormSubmit(e) {
    e.preventDefault();
    
    const subject = document.getElementById('subject').value;
    const date = document.getElementById('examDate').value;
    const startTime = document.getElementById('startTime').value;
    const endTime = document.getElementById('endTime').value;
    const paperInfo = document.getElementById('paperInfo').value;
    
    if (!subject || !date || !startTime || !endTime || !paperInfo) {
        alert('请填写所有字段');
        return;
    }
    
    examData.push({
        subject,
        date,
        startTime,
        endTime,
        paperInfo
    });
    
    renderExamTable();
    updateLastUpdateTime();
    hideAddExamModal();
}

// 导出为JSON
function exportToJson() {
    const dataStr = JSON.stringify(examData, null, 2);
    const dataBlob = new Blob([dataStr], {type: 'application/json'});
    
    const url = URL.createObjectURL(dataBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'exam_data.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// 更新最后更新时间
function updateLastUpdateTime() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    const day = String(now.getDate()).padStart(2, '0');
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    lastUpdateSpan.textContent = `${year}年${month}月${day}日 ${hours}:${minutes}`;
}