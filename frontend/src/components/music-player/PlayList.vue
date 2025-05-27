<template>
  <div class="playlist">
    <div class="playlist-header">
      <h2>{{ isSearchMode ? '搜索结果' : '播放列表' }}</h2>
      <div class="playlist-controls">
        <button @click="$emit('refresh')" class="refresh-btn">刷新库</button>
      </div>
    </div>
    
    <div v-if="loading" class="loading-indicator">
      加载中...
    </div>
    
    <div v-else-if="isSearchMode && searchResults.length === 0" class="empty-list">
      未找到匹配的音乐文件
    </div>
    
    <div v-else-if="!isSearchMode && songs.length === 0" class="empty-list">
      未找到音乐文件，请检查音乐库目录配置
    </div>
    
    <ul v-else>
      <li 
        v-for="song in displayedSongs" 
        :key="song.id"
        :class="{ 
          active: status.current_song === song.name,
          'has-metadata': song.metadata
        }"
        @click="$emit('play', song)"
      >
        <div class="song-item">
          <div class="song-main-info">
            <span class="song-name">{{ song.title || song.name }}</span>
            <span v-if="song.metadata && song.metadata.artist" class="song-artist">
              {{ song.metadata.artist }}
            </span>
          </div>
          <div class="song-extra-info">
            <span v-if="song.metadata && song.metadata.duration" class="song-duration">
              {{ formatTime(song.metadata.duration) }}
            </span>
            <span class="song-size">{{ (song.size).toFixed(2) }} MB</span>
          </div>
        </div>
      </li>
    </ul>
    
    <!-- 搜索模式下显示结果数 -->
    <div class="search-info" v-if="isSearchMode">
      找到 {{ searchResults.length }} 个匹配结果
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import type { Song, PlaybackStatus } from '../../api';

export default defineComponent({
  name: 'PlayList',
  props: {
    loading: {
      type: Boolean,
      default: false
    },
    isSearchMode: {
      type: Boolean,
      default: false
    },
    searchResults: {
      type: Array as () => Song[],
      default: () => []
    },
    songs: {
      type: Array as () => Song[],
      default: () => []
    },
    displayedSongs: {
      type: Array as () => Song[],
      default: () => []
    },
    status: {
      type: Object as () => PlaybackStatus,
      required: true
    }
  },
  emits: ['play', 'refresh'],
  setup() {
    // 格式化时间
    const formatTime = (seconds: number): string => {
      if (isNaN(seconds) || seconds === 0) return '00:00';
      
      const min = Math.floor(seconds / 60);
      const sec = Math.floor(seconds % 60);
      return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
    };
    
    return {
      formatTime
    };
  }
});
</script>

<style scoped>
.playlist {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

h2 {
  color: #444;
  margin-top: 0;
  margin-bottom: 15px;
}

.playlist-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.playlist-controls {
  display: flex;
  gap: 10px;
}

.refresh-btn {
  padding: 5px 10px;
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.empty-list {
  text-align: center;
  padding: 20px;
  color: #777;
  font-style: italic;
}

.loading-indicator {
  text-align: center;
  padding: 20px;
  color: #2196F3;
  font-weight: bold;
}

ul {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 400px;
  overflow-y: auto;
}

li {
  border-bottom: 1px solid #eee;
  transition: background-color 0.2s;
  cursor: pointer;
}

li:hover {
  background-color: #f5f5f5;
}

li.active {
  background-color: #e3f2fd;
}

.song-item {
  padding: 12px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.song-main-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.song-name {
  font-weight: 500;
}

.song-artist {
  font-size: 12px;
  color: #777;
  margin-top: 3px;
}

.song-extra-info {
  display: flex;
  gap: 15px;
  align-items: center;
}

.song-duration {
  color: #555;
  font-size: 13px;
}

.song-size {
  color: #888;
  font-size: 12px;
}

.search-info {
  text-align: center;
  margin-top: 20px;
  font-size: 14px;
  color: #555;
}
</style> 