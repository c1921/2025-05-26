<template>
  <div class="settings-container">
    <h2>音乐库设置</h2>
    
    <div class="library-settings">
      <h3>音乐库路径</h3>
      
      <div v-if="libraries.length === 0" class="empty-message">
        尚未添加任何音乐库，请添加至少一个音乐库路径
      </div>
      
      <ul class="library-list">
        <li v-for="(lib, index) in libraries" :key="index" class="library-item">
          <div class="library-path">{{ lib }}</div>
          <button class="remove-btn" @click="removeLibrary(index)">删除</button>
        </li>
      </ul>
      
      <div class="add-library">
        <input 
          v-model="newLibraryPath" 
          placeholder="输入音乐库路径，例如: D:\Music" 
          class="path-input"
        />
        <button class="add-btn" @click="addLibrary">添加路径</button>
      </div>
      
      <div class="actions">
        <button class="save-btn" @click="saveLibraries" :disabled="!hasChanges">保存更改</button>
        <button class="cancel-btn" @click="resetLibraries" :disabled="!hasChanges">取消</button>
      </div>
      
      <div class="tip-box">
        <p>保存设置后，系统会自动刷新音乐库。如果您没有看到新添加目录中的音乐，可以尝试手动刷新。</p>
        <div class="refresh-actions">
          <button class="refresh-btn" @click="startScan" :disabled="scanStatus.is_scanning">
            {{ scanStatus.is_scanning ? '扫描中...' : '扫描音乐库' }}
          </button>
          <button class="clear-cache-btn" @click="clearCache" :disabled="scanStatus.is_scanning">清除缓存</button>
          <button class="reload-btn" @click="refreshPage">刷新页面</button>
        </div>
        
        <!-- 扫描状态显示 -->
        <div v-if="scanStatus.is_scanning" class="scan-status">
          <div class="progress-indicator">
            <div class="progress-bar-animated"></div>
          </div>
          <p>正在扫描音乐库，这可能需要一些时间...</p>
        </div>
        
        <div v-else-if="scanStatus.last_scan_time > 0" class="scan-status">
          <p>上次扫描时间: {{ formatScanTime(scanStatus.last_scan_time) }}</p>
          <p>
            <label class="checkbox-container">
              <input type="checkbox" v-model="includeMetadata" />
              <span class="checkmark"></span>
              包含音乐元数据（扫描时间会更长）
            </label>
          </p>
        </div>
        
        <div v-if="refreshMessage" class="refresh-message">
          {{ refreshMessage }}
        </div>
      </div>
      
      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>
      
      <div v-if="successMessage" class="success-message">
        {{ successMessage }}
      </div>
    </div>
    
    <div class="format-settings">
      <h3>支持的音频格式</h3>
      <div class="formats-display">
        <span v-for="(format, index) in supportedFormats" :key="index" class="format-tag">
          {{ format }}
        </span>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed, onUnmounted } from 'vue';
import { apiService } from '../api';
import type { ScanStatus } from '../api';

export default defineComponent({
  name: 'Settings',
  
  setup() {
    const libraries = ref<string[]>([]);
    const originalLibraries = ref<string[]>([]);
    const newLibraryPath = ref('');
    const errorMessage = ref('');
    const successMessage = ref('');
    const refreshMessage = ref('');
    const includeMetadata = ref(true);
    const supportedFormats = ref<string[]>([]);
    const scanStatus = ref<ScanStatus>({
      is_scanning: false,
      last_scan_time: 0,
      has_result: false
    });
    const statusCheckInterval = ref<number | null>(null);
    
    // 计算是否有未保存的更改
    const hasChanges = computed(() => {
      if (libraries.value.length !== originalLibraries.value.length) {
        return true;
      }
      
      for (let i = 0; i < libraries.value.length; i++) {
        if (libraries.value[i] !== originalLibraries.value[i]) {
          return true;
        }
      }
      
      return false;
    });
    
    // 加载音乐库路径
    const loadLibraries = async () => {
      try {
        const data = await apiService.getLibraryInfo();
        libraries.value = [...data.libraries];
        originalLibraries.value = [...data.libraries];
        errorMessage.value = '';
      } catch (error) {
        console.error('加载音乐库路径失败:', error);
        errorMessage.value = '加载音乐库路径失败，请稍后再试';
      }
    };
    
    // 加载配置
    const loadConfig = async () => {
      try {
        const config = await apiService.getConfig();
        supportedFormats.value = config.supported_formats;
      } catch (error) {
        console.error('加载配置失败:', error);
      }
    };
    
    // 获取扫描状态
    const checkScanStatus = async () => {
      try {
        scanStatus.value = await apiService.getScanStatus();
      } catch (error) {
        console.error('获取扫描状态失败:', error);
      }
    };
    
    // 开始扫描
    const startScan = async () => {
      try {
        const result = await apiService.startLibraryScan(includeMetadata.value);
        
        if (result.success) {
          refreshMessage.value = result.message;
          scanStatus.value = result.status;
          
          // 设置定时器以更频繁地检查状态
          if (statusCheckInterval.value) {
            clearInterval(statusCheckInterval.value);
          }
          statusCheckInterval.value = setInterval(checkScanStatus, 1000) as unknown as number;
          
          setTimeout(() => {
            refreshMessage.value = '';
          }, 5000);
        } else {
          errorMessage.value = result.message;
        }
      } catch (error: any) {
        console.error('开始扫描失败:', error);
        errorMessage.value = '开始扫描失败，请稍后再试';
      }
    };
    
    // 清除缓存
    const clearCache = async () => {
      try {
        const result = await apiService.clearCache();
        
        if (result.success) {
          successMessage.value = result.message;
          setTimeout(() => {
            successMessage.value = '';
          }, 3000);
        } else {
          errorMessage.value = '清除缓存失败';
        }
      } catch (error) {
        console.error('清除缓存失败:', error);
        errorMessage.value = '清除缓存失败，请稍后再试';
      }
    };
    
    // 添加新的音乐库路径
    const addLibrary = () => {
      if (!newLibraryPath.value.trim()) {
        errorMessage.value = '请输入有效的路径';
        return;
      }
      
      // 检查是否已存在
      if (libraries.value.includes(newLibraryPath.value)) {
        errorMessage.value = '该路径已添加';
        return;
      }
      
      libraries.value.push(newLibraryPath.value);
      newLibraryPath.value = '';
      errorMessage.value = '';
      successMessage.value = '';
      refreshMessage.value = '';
    };
    
    // 移除音乐库路径
    const removeLibrary = (index: number) => {
      libraries.value.splice(index, 1);
      errorMessage.value = '';
      successMessage.value = '';
      refreshMessage.value = '';
    };
    
    // 保存音乐库路径
    const saveLibraries = async () => {
      try {
        const result = await apiService.updateLibrary(libraries.value);
        
        if (result.success) {
          originalLibraries.value = [...libraries.value];
          successMessage.value = '音乐库路径已保存，系统正在准备扫描新的音乐文件';
          
          // 开始扫描
          startScan();
          
          errorMessage.value = '';
          refreshMessage.value = '';
        } else {
          errorMessage.value = '保存失败';
        }
        
        // 3秒后清除成功消息
        setTimeout(() => {
          successMessage.value = '';
        }, 3000);
      } catch (error: any) {
        console.error('保存音乐库路径失败:', error);
        if (error.response && error.response.data && error.response.data.detail) {
          errorMessage.value = error.response.data.detail;
        } else {
          errorMessage.value = '保存音乐库路径失败，请稍后再试';
        }
      }
    };
    
    // 重置为原始值
    const resetLibraries = () => {
      libraries.value = [...originalLibraries.value];
      errorMessage.value = '';
      successMessage.value = '';
      refreshMessage.value = '';
    };
    
    // 刷新页面
    const refreshPage = () => {
      window.location.reload();
    };
    
    // 格式化扫描时间
    const formatScanTime = (timestamp: number): string => {
      if (!timestamp) return '未进行过扫描';
      
      const date = new Date(timestamp * 1000);
      return date.toLocaleString();
    };
    
    // 组件挂载时加载数据并设置定时检查
    onMounted(async () => {
      await loadLibraries();
      await loadConfig();
      await checkScanStatus();
      
      // 设置定时器检查扫描状态
      statusCheckInterval.value = setInterval(checkScanStatus, 3000) as unknown as number;
    });
    
    // 组件卸载时清除定时器
    onUnmounted(() => {
      if (statusCheckInterval.value) {
        clearInterval(statusCheckInterval.value);
      }
    });
    
    return {
      libraries,
      newLibraryPath,
      errorMessage,
      successMessage,
      refreshMessage,
      scanStatus,
      includeMetadata,
      supportedFormats,
      hasChanges,
      addLibrary,
      removeLibrary,
      saveLibraries,
      resetLibraries,
      startScan,
      clearCache,
      refreshPage,
      formatScanTime
    };
  }
});
</script>

<style scoped>
.settings-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

h2 {
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 20px;
}

h3 {
  color: #555;
  margin-top: 25px;
  margin-bottom: 15px;
}

.library-settings {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.empty-message {
  color: #999;
  font-style: italic;
  margin-bottom: 15px;
}

.library-list {
  list-style: none;
  padding: 0;
  margin-bottom: 20px;
}

.library-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 10px;
}

.library-path {
  flex: 1;
  font-family: 'Courier New', monospace;
  word-break: break-all;
}

.remove-btn {
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 5px 10px;
  margin-left: 10px;
  cursor: pointer;
}

.add-library {
  display: flex;
  margin-bottom: 20px;
  gap: 10px;
}

.path-input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}

.add-btn {
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 8px 15px;
  cursor: pointer;
}

.actions {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.save-btn, .cancel-btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn {
  background-color: #2196F3;
  color: white;
}

.save-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.cancel-btn {
  background-color: #9e9e9e;
  color: white;
}

.cancel-btn:disabled {
  background-color: #ddd;
  cursor: not-allowed;
}

.tip-box {
  background-color: #e8f4f8;
  border-left: 4px solid #2196F3;
  padding: 15px;
  margin-bottom: 20px;
  border-radius: 4px;
}

.refresh-actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}

.refresh-btn, .clear-cache-btn, .reload-btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.refresh-btn {
  background-color: #4CAF50;
  color: white;
}

.clear-cache-btn {
  background-color: #ff9800;
  color: white;
}

.reload-btn {
  background-color: #9e9e9e;
  color: white;
}

.refresh-message, .error-message, .success-message {
  margin-top: 15px;
  padding: 10px;
  border-radius: 4px;
}

.refresh-message {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.error-message {
  background-color: #ffebee;
  color: #c62828;
}

.success-message {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.scan-status {
  margin-top: 15px;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.progress-indicator {
  height: 6px;
  background-color: #e0e0e0;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-bar-animated {
  height: 100%;
  width: 30%;
  background-color: #2196F3;
  border-radius: 3px;
  animation: progress-animation 1.5s infinite ease-in-out;
}

@keyframes progress-animation {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(400%);
  }
}

.checkbox-container {
  display: block;
  position: relative;
  padding-left: 35px;
  margin-bottom: 12px;
  cursor: pointer;
  user-select: none;
}

.checkbox-container input {
  position: absolute;
  opacity: 0;
  cursor: pointer;
  height: 0;
  width: 0;
}

.checkmark {
  position: absolute;
  top: 0;
  left: 0;
  height: 20px;
  width: 20px;
  background-color: #eee;
  border-radius: 3px;
}

.checkbox-container:hover input ~ .checkmark {
  background-color: #ccc;
}

.checkbox-container input:checked ~ .checkmark {
  background-color: #2196F3;
}

.checkmark:after {
  content: "";
  position: absolute;
  display: none;
}

.checkbox-container input:checked ~ .checkmark:after {
  display: block;
}

.checkbox-container .checkmark:after {
  left: 7px;
  top: 3px;
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
}

.format-settings {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.formats-display {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.format-tag {
  background-color: #e0e0e0;
  color: #333;
  padding: 5px 10px;
  border-radius: 15px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
}
</style> 