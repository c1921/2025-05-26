<script setup lang="ts">
import { ref } from 'vue';
import MusicPlayer from './components/MusicPlayer.vue';
import Settings from './components/Settings.vue';

const currentPage = ref('player'); // 默认显示播放器页面

// 页面切换函数
const navigateTo = (page: string) => {
  currentPage.value = page;
};
</script>

<template>
  <div class="app-container">
    <header class="app-header">
      <h1 class="app-title">音乐播放器</h1>
      <nav class="main-nav">
        <button 
          :class="['nav-button', currentPage === 'player' ? 'active' : '']" 
          @click="navigateTo('player')"
        >
          播放器
        </button>
        <button 
          :class="['nav-button', currentPage === 'settings' ? 'active' : '']" 
          @click="navigateTo('settings')"
        >
          设置
        </button>
      </nav>
    </header>
    
    <main class="app-content">
      <MusicPlayer v-if="currentPage === 'player'" />
      <Settings v-if="currentPage === 'settings'" />
    </main>
  </div>
</template>

<style>
body {
  margin: 0;
  padding: 0;
  background-color: #f5f5f5;
  font-family: Arial, sans-serif;
}

.app-container {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 15px;
  border-bottom: 1px solid #e8e8e8;
}

.app-title {
  margin: 0;
  color: #1890ff;
  font-size: 24px;
}

.main-nav {
  display: flex;
  gap: 10px;
}

.nav-button {
  padding: 8px 16px;
  background-color: #f0f0f0;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
}

.nav-button.active {
  background-color: #1890ff;
  color: white;
  border-color: #1890ff;
}

.nav-button:hover {
  background-color: #e6f7ff;
  border-color: #1890ff;
}

.nav-button.active:hover {
  background-color: #40a9ff;
}

.app-content {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}
</style>
