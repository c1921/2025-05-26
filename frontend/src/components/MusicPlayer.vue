<template>
  <div class="music-player">
    <!-- 搜索栏 -->
    <div class="search-bar">
      <input 
        type="text" 
        v-model="searchQuery" 
        placeholder="搜索歌曲、艺术家或专辑..." 
        @keyup.enter="handleSearch"
      />
      <button class="search-btn" @click="handleSearch">搜索</button>
      <button class="clear-btn" @click="clearSearch" v-if="isSearchMode">清除</button>
    </div>
    
    <!-- 播放控制区域 -->
    <div class="player-controls" v-if="currentSong || status.current_song">
      <div class="song-info">
        <h3>{{ songTitle }}</h3>
        <div class="metadata-display" v-if="currentSong && currentSong.metadata">
          <span v-if="currentSong.artist">艺术家: {{ currentSong.artist }}</span>
          <span v-if="currentSong.album">专辑: {{ currentSong.album }}</span>
        </div>
      </div>
      
      <!-- 进度条 -->
      <div class="progress-bar">
        <span class="time">{{ formatTime(status.position) }}</span>
        <input 
          type="range" 
          min="0" 
          :max="status.duration" 
          v-model="sliderPosition"
          @input="handleSliderInput"
          @change="handleSliderChange"
          class="progress-slider"
        />
        <span class="time">{{ formatTime(status.duration) }}</span>
      </div>
      
      <!-- 控制按钮 -->
      <div class="control-buttons">
        <button @click="handleLoop" :class="{ active: status.loop }" class="loop-btn">
          {{ status.loop ? '循环开' : '循环关' }}
        </button>
        <button @click="playPrevious" class="control-btn">上一首</button>
        <button @click="handlePlayPause" class="control-btn main-btn">
          {{ status.playing ? '暂停' : '播放' }}
        </button>
        <button @click="stopPlayback" class="control-btn">停止</button>
        <button @click="playNext" class="control-btn">下一首</button>
      </div>
      
      <!-- 音量控制 -->
      <div class="volume-control">
        <span>音量:</span>
        <input 
          type="range" 
          min="0" 
          max="1" 
          step="0.01"
          v-model="volumeLevel"
          @input="handleVolumeStart"
          @change="handleVolumeChange"
          class="volume-slider"
        />
      </div>
    </div>
    
    <!-- 播放列表 -->
    <div class="playlist">
      <div class="playlist-header">
        <h2>{{ isSearchMode ? '搜索结果' : '播放列表' }}</h2>
        <div class="playlist-controls">
          <button @click="refreshLibrary" class="refresh-btn">刷新库</button>
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
          @click="playSong(song)"
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
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, onUnmounted } from 'vue';
import { apiService } from '../api';
import type { Song, PlaybackStatus } from '../api';

export default defineComponent({
  name: 'MusicPlayer',
  setup() {
    // 状态数据
    const songs = ref<Song[]>([]);
    const searchResults = ref<Song[]>([]);
    const status = ref<PlaybackStatus>({
      active: false,
      playing: false,
      current_song: null,
      position: 0,
      duration: 0,
      volume: 1,
      loop: false
    });
    const currentSong = ref<Song | null>(null);
    const sliderPosition = ref(0);
    const volumeLevel = ref(1);
    const statusInterval = ref<number | null>(null);
    const isVolumeUserControlled = ref(false); // 标记音量是否被用户手动调整
    
    // 加载状态
    const loading = ref(false);
    
    // 搜索相关状态
    const searchQuery = ref('');
    const isSearchMode = ref(false);
    
    // 计算属性：当前显示的歌曲列表
    const displayedSongs = computed(() => {
      return isSearchMode.value ? searchResults.value : songs.value;
    });
    
    // 计算属性：歌曲标题（优先使用元数据的标题）
    const songTitle = computed(() => {
      if (currentSong.value && currentSong.value.title) {
        return currentSong.value.title;
      }
      return currentSong.value?.name || status.value.current_song || '';
    });
    
    // 获取歌曲列表
    const fetchSongs = async () => {
      loading.value = true;
      try {
        songs.value = await apiService.getSongs(true); // 包含元数据
      } catch (error) {
        console.error('获取歌曲列表失败:', error);
        songs.value = [];
      } finally {
        loading.value = false;
      }
    };
    
    // 搜索歌曲
    const handleSearch = async () => {
      if (!searchQuery.value.trim()) {
        clearSearch();
        return;
      }
      
      loading.value = true;
      isSearchMode.value = true;
      
      try {
        const result = await apiService.searchSongs(searchQuery.value);
        searchResults.value = result.items;
      } catch (error) {
        console.error('搜索歌曲失败:', error);
        searchResults.value = [];
      } finally {
        loading.value = false;
      }
    };
    
    // 清除搜索，返回全部歌曲列表
    const clearSearch = () => {
      searchQuery.value = '';
      searchResults.value = [];
      isSearchMode.value = false;
    };
    
    // 刷新音乐库
    const refreshLibrary = async () => {
      loading.value = true;
      try {
        // 开始异步扫描
        await apiService.startLibraryScan(true);
        
        // 等待2秒后重新加载歌曲列表
        setTimeout(() => {
          fetchSongs();
        }, 2000);
      } catch (error) {
        console.error('刷新音乐库失败:', error);
      } finally {
        loading.value = false;
      }
    };
    
    // 获取播放状态
    const fetchStatus = async () => {
      try {
        const newStatus = await apiService.getStatus();
        
        // 更新除了音量以外的所有状态
        status.value = {
          ...newStatus,
          // 如果用户正在控制音量，保留当前的音量设置
          volume: isVolumeUserControlled.value ? volumeLevel.value : newStatus.volume
        };
        
        if (status.value.active) {
          sliderPosition.value = status.value.position;
          
          // 只有在初始化或未被用户控制时才更新音量
          if (!isVolumeUserControlled.value) {
            volumeLevel.value = status.value.volume;
          }
          
          // 找到当前播放的歌曲
          if (status.value.current_song) {
            // 使用解码后的文件名进行比较
            const songName = status.value.current_song;
            
            // 在显示的歌曲中查找
            currentSong.value = displayedSongs.value.find(song => song.name === songName) || null;
            
            // 如果找不到匹配的歌曲，可能是因为编码问题，则创建一个临时歌曲对象
            if (!currentSong.value) {
              console.log('找不到匹配的歌曲，创建临时歌曲对象:', songName);
              currentSong.value = {
                id: '', // 空字符串ID
                name: songName,
                path: '',
                size: 0,
                add_time: 0
              };
            }
          }
        }
      } catch (error) {
        console.error('获取播放状态失败:', error);
      }
    };
    
    // 启动定时获取状态
    const startStatusInterval = () => {
      // 先清除已有的定时器
      if (statusInterval.value) {
        clearInterval(statusInterval.value);
      }
      // 设置新的定时器，每秒更新一次状态
      statusInterval.value = setInterval(fetchStatus, 1000) as unknown as number;
    };
    
    // 播放歌曲
    const playSong = async (song: Song) => {
      try {
        await apiService.playSong(song.id);
        currentSong.value = song;
        await fetchStatus();
      } catch (error) {
        console.error('播放歌曲失败:', error);
      }
    };
    
    // 处理播放/暂停
    const handlePlayPause = async () => {
      try {
        if (!status.value.active && displayedSongs.value.length > 0) {
          // 如果没有激活的歌曲，播放第一首
          await playSong(displayedSongs.value[0]);
        } else if (status.value.playing) {
          await apiService.pauseSong();
        } else {
          await apiService.resumeSong();
        }
        await fetchStatus();
      } catch (error) {
        console.error('播放/暂停操作失败:', error);
      }
    };
    
    // 停止播放
    const stopPlayback = async () => {
      try {
        await apiService.stopSong();
        currentSong.value = null;
        await fetchStatus();
      } catch (error) {
        console.error('停止播放失败:', error);
      }
    };
    
    // 播放下一首
    const playNext = async () => {
      if (displayedSongs.value.length === 0) return;
      
      let nextIndex = 0;
      if (currentSong.value) {
        const currentIndex = displayedSongs.value.findIndex(song => song.id === currentSong.value?.id);
        if (currentIndex !== -1) {
          nextIndex = (currentIndex + 1) % displayedSongs.value.length;
        }
      }
      
      await playSong(displayedSongs.value[nextIndex]);
    };
    
    // 播放上一首
    const playPrevious = async () => {
      if (displayedSongs.value.length === 0) return;
      
      let prevIndex = displayedSongs.value.length - 1;
      if (currentSong.value) {
        const currentIndex = displayedSongs.value.findIndex(song => song.id === currentSong.value?.id);
        if (currentIndex !== -1) {
          prevIndex = (currentIndex - 1 + displayedSongs.value.length) % displayedSongs.value.length;
        }
      }
      
      await playSong(displayedSongs.value[prevIndex]);
    };
    
    // 处理进度条输入
    const handleSliderInput = (event: Event) => {
      const target = event.target as HTMLInputElement;
      sliderPosition.value = parseFloat(target.value);
    };
    
    // 处理进度条变更
    const handleSliderChange = async () => {
      try {
        await apiService.seekPosition(sliderPosition.value);
      } catch (error) {
        console.error('设置播放位置失败:', error);
      }
    };
    
    // 处理音量变更开始
    const handleVolumeStart = () => {
      isVolumeUserControlled.value = true;
    };
    
    // 处理音量变更
    const handleVolumeChange = async () => {
      try {
        await apiService.setVolume(volumeLevel.value);
        
        // 3秒后取消用户控制标记，允许服务器再次更新音量
        setTimeout(() => {
          isVolumeUserControlled.value = false;
        }, 3000);
      } catch (error) {
        console.error('设置音量失败:', error);
      }
    };
    
    // 处理循环播放切换
    const handleLoop = async () => {
      try {
        await apiService.setLoop(!status.value.loop);
        await fetchStatus();
      } catch (error) {
        console.error('设置循环播放失败:', error);
      }
    };
    
    // 格式化时间
    const formatTime = (seconds: number): string => {
      if (isNaN(seconds) || seconds === 0) return '00:00';
      
      const min = Math.floor(seconds / 60);
      const sec = Math.floor(seconds % 60);
      return `${min.toString().padStart(2, '0')}:${sec.toString().padStart(2, '0')}`;
    };
    
    // 组件挂载时加载数据并启动状态更新
    onMounted(async () => {
      await fetchSongs();
      await fetchStatus();
      startStatusInterval();
    });
    
    // 组件卸载时清除定时器
    onUnmounted(() => {
      if (statusInterval.value) {
        clearInterval(statusInterval.value);
      }
    });
    
    return {
      songs,
      searchResults,
      status,
      currentSong,
      sliderPosition,
      volumeLevel,
      loading,
      searchQuery,
      isSearchMode,
      displayedSongs,
      songTitle,
      playSong,
      handlePlayPause,
      stopPlayback,
      playNext,
      playPrevious,
      handleSliderInput,
      handleSliderChange,
      handleVolumeStart,
      handleVolumeChange,
      handleLoop,
      formatTime,
      handleSearch,
      clearSearch,
      refreshLibrary
    };
  }
});
</script>

<style scoped>
.music-player {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  text-align: center;
  color: #333;
  margin-bottom: 30px;
}

h2 {
  color: #444;
  margin-top: 0;
  margin-bottom: 15px;
}

.search-bar {
  margin-bottom: 20px;
  display: flex;
  gap: 10px;
}

.search-bar input {
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}

.search-btn {
  padding: 8px 15px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.clear-btn {
  padding: 8px 15px;
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.player-controls {
  background-color: #f9f9f9;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 30px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.song-info {
  text-align: center;
  margin-bottom: 15px;
}

.song-info h3 {
  margin-bottom: 5px;
}

.metadata-display {
  font-size: 14px;
  color: #666;
  display: flex;
  justify-content: center;
  gap: 15px;
}

.progress-bar {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.time {
  min-width: 45px;
  text-align: center;
  font-size: 14px;
  color: #777;
}

.progress-slider {
  flex: 1;
  margin: 0 10px;
  height: 5px;
}

.control-buttons {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}

.control-btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  background-color: #2196F3;
  color: white;
  cursor: pointer;
}

.control-btn:hover {
  background-color: #0b7dda;
}

.main-btn {
  font-weight: bold;
  padding: 8px 25px;
}

.loop-btn {
  padding: 8px 15px;
  border: none;
  border-radius: 4px;
  background-color: #9e9e9e;
  color: white;
  cursor: pointer;
}

.loop-btn.active {
  background-color: #4caf50;
}

.volume-control {
  display: flex;
  align-items: center;
  gap: 10px;
  justify-content: center;
}

.volume-slider {
  width: 100px;
}

.playlist {
  background-color: #fff;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
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