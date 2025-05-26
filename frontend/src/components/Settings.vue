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
          <button class="refresh-btn" @click="refreshLibrary" :disabled="isRefreshing">
            {{ isRefreshing ? '刷新中...' : '刷新音乐库' }}
          </button>
          <button class="reload-btn" @click="refreshPage">刷新页面</button>
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
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, computed } from 'vue';
import { apiService } from '../api';

export default defineComponent({
  name: 'Settings',
  
  setup() {
    const libraries = ref<string[]>([]);
    const originalLibraries = ref<string[]>([]);
    const newLibraryPath = ref('');
    const errorMessage = ref('');
    const successMessage = ref('');
    const refreshMessage = ref('');
    const isRefreshing = ref(false);
    
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
        const data = await apiService.getMusicLibraries();
        libraries.value = [...data];
        originalLibraries.value = [...data];
        errorMessage.value = '';
      } catch (error) {
        console.error('加载音乐库路径失败:', error);
        errorMessage.value = '加载音乐库路径失败，请稍后再试';
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
        await apiService.setMusicLibraries(libraries.value);
        originalLibraries.value = [...libraries.value];
        successMessage.value = '音乐库路径已保存，系统正在扫描新的音乐文件';
        errorMessage.value = '';
        refreshMessage.value = '';
        
        // 3秒后清除成功消息
        setTimeout(() => {
          successMessage.value = '';
        }, 3000);
      } catch (error: any) {
        console.error('保存音乐库路径失败:', error);
        if (error.response && error.response.data && error.response.data.invalid_paths) {
          const invalidPaths = error.response.data.invalid_paths.join(', ');
          errorMessage.value = `以下路径无效或不存在: ${invalidPaths}`;
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
    
    // 刷新音乐库
    const refreshLibrary = async () => {
      isRefreshing.value = true;
      refreshMessage.value = '正在刷新音乐库，请稍候...';
      errorMessage.value = '';
      successMessage.value = '';
      
      try {
        const result = await apiService.refreshMusicLibrary();
        refreshMessage.value = result.message;
        setTimeout(() => {
          refreshMessage.value = '';
        }, 5000);
      } catch (error: any) {
        console.error('刷新音乐库失败:', error);
        refreshMessage.value = '';
        if (error.response && error.response.data && error.response.data.detail) {
          errorMessage.value = error.response.data.detail;
        } else {
          errorMessage.value = '刷新音乐库失败，请稍后再试';
        }
      } finally {
        isRefreshing.value = false;
      }
    };
    
    // 刷新页面
    const refreshPage = () => {
      window.location.reload();
    };
    
    // 组件挂载时加载数据
    onMounted(() => {
      loadLibraries();
    });
    
    return {
      libraries,
      newLibraryPath,
      errorMessage,
      successMessage,
      refreshMessage,
      isRefreshing,
      hasChanges,
      addLibrary,
      removeLibrary,
      saveLibraries,
      resetLibraries,
      refreshLibrary,
      refreshPage
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
  margin-bottom: 20px;
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

h3 {
  margin-top: 0;
  margin-bottom: 15px;
  color: #555;
}

.library-list {
  list-style: none;
  padding: 0;
  margin-bottom: 20px;
}

.library-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  margin-bottom: 8px;
}

.library-path {
  word-break: break-all;
  flex: 1;
}

.remove-btn {
  background-color: #ff4d4f;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  margin-left: 10px;
  cursor: pointer;
}

.add-library {
  display: flex;
  margin-bottom: 20px;
}

.path-input {
  flex: 1;
  padding: 8px 10px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  margin-right: 10px;
}

.add-btn {
  background-color: #1890ff;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}

.actions {
  display: flex;
  gap: 10px;
  margin-bottom: 15px;
}

.save-btn {
  background-color: #52c41a;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}

.save-btn:disabled {
  background-color: #d9d9d9;
  cursor: not-allowed;
}

.cancel-btn {
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #d9d9d9;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}

.cancel-btn:disabled {
  color: #d9d9d9;
  cursor: not-allowed;
}

.tip-box {
  background-color: #e6f7ff;
  border: 1px solid #91d5ff;
  border-radius: 4px;
  padding: 15px;
  margin: 20px 0;
}

.refresh-actions {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.refresh-btn {
  background-color: #1890ff;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}

.refresh-btn:disabled {
  background-color: #d9d9d9;
  cursor: not-allowed;
}

.reload-btn {
  background-color: #f5f5f5;
  color: #333;
  border: 1px solid #d9d9d9;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
}

.refresh-message {
  margin-top: 10px;
  color: #1890ff;
  font-weight: bold;
}

.error-message {
  color: #ff4d4f;
  margin-top: 10px;
}

.success-message {
  color: #52c41a;
  margin-top: 10px;
}

.empty-message {
  padding: 20px;
  background-color: #fafafa;
  border: 1px dashed #d9d9d9;
  border-radius: 4px;
  text-align: center;
  color: #888;
  margin-bottom: 20px;
}
</style> 