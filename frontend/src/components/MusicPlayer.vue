<template>
  <div class="music-player">
    
    <!-- 上传区域 -->
    <div class="upload-area">
      <input type="file" ref="fileInput" @change="handleFileUpload" accept=".mp3,.wav,.ogg,.flac" />
      <button @click="triggerFileInput" class="upload-btn">选择音乐文件</button>
    </div>
    
    <!-- 播放控制区域 -->
    <div class="player-controls" v-if="currentSong || status.current_song">
      <div class="song-info">
        <h3>{{ currentSong?.name || status.current_song }}</h3>
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
      <h2>播放列表</h2>
      <div v-if="songs.length === 0" class="empty-list">
        暂无音乐，请上传
      </div>
      <ul v-else>
        <li 
          v-for="song in songs" 
          :key="song.id"
          :class="{ active: status.current_song === song.name }"
          @click="playSong(song)"
        >
          <div class="song-item">
            <span class="song-name">{{ song.name }}</span>
            <span class="song-size">{{ (song.size).toFixed(2) }} MB</span>
            <button @click.stop="deleteSong(song)" class="delete-btn">删除</button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue';
import { apiService } from '../api';
import type { Song, PlaybackStatus } from '../api';

export default defineComponent({
  name: 'MusicPlayer',
  setup() {
    // 状态数据
    const songs = ref<Song[]>([]);
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
    const fileInput = ref<HTMLInputElement | null>(null);
    const statusInterval = ref<number | null>(null);
    const isVolumeUserControlled = ref(false); // 标记音量是否被用户手动调整
    
    // 获取歌曲列表
    const fetchSongs = async () => {
      try {
        songs.value = await apiService.getSongs();
      } catch (error) {
        console.error('获取歌曲列表失败:', error);
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
            currentSong.value = songs.value.find(song => song.name === status.value.current_song) || null;
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
        await apiService.playSong(song.name);
        currentSong.value = song;
        await fetchStatus();
      } catch (error) {
        console.error('播放歌曲失败:', error);
      }
    };
    
    // 处理播放/暂停
    const handlePlayPause = async () => {
      try {
        if (!status.value.active && songs.value.length > 0) {
          // 如果没有激活的歌曲，播放第一首
          await playSong(songs.value[0]);
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
      if (songs.value.length === 0) return;
      
      let nextIndex = 0;
      if (currentSong.value) {
        const currentIndex = songs.value.findIndex(song => song.id === currentSong.value?.id);
        nextIndex = (currentIndex + 1) % songs.value.length;
      }
      
      await playSong(songs.value[nextIndex]);
    };
    
    // 播放上一首
    const playPrevious = async () => {
      if (songs.value.length === 0) return;
      
      let prevIndex = songs.value.length - 1;
      if (currentSong.value) {
        const currentIndex = songs.value.findIndex(song => song.id === currentSong.value?.id);
        prevIndex = (currentIndex - 1 + songs.value.length) % songs.value.length;
      }
      
      await playSong(songs.value[prevIndex]);
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
    
    // 触发文件选择
    const triggerFileInput = () => {
      if (fileInput.value) {
        fileInput.value.click();
      }
    };
    
    // 处理文件上传
    const handleFileUpload = async (event: Event) => {
      const target = event.target as HTMLInputElement;
      const files = target.files;
      
      if (files && files.length > 0) {
        const file = files[0];
        
        try {
          await apiService.uploadSong(file);
          await fetchSongs();
          
          // 清空文件输入框，允许重复上传同一文件
          if (fileInput.value) {
            fileInput.value.value = '';
          }
        } catch (error) {
          console.error('上传歌曲失败:', error);
        }
      }
    };
    
    // 删除歌曲
    const deleteSong = async (song: Song) => {
      if (confirm(`确定要删除歌曲 "${song.name}" 吗？`)) {
        try {
          await apiService.deleteSong(song.name);
          await fetchSongs();
          
          // 如果删除的是当前播放的歌曲，更新状态
          if (currentSong.value?.id === song.id) {
            currentSong.value = null;
          }
          
          await fetchStatus();
        } catch (error) {
          console.error('删除歌曲失败:', error);
        }
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
    onMounted(() => {
      return () => {
        if (statusInterval.value) {
          clearInterval(statusInterval.value);
        }
      };
    });
    
    return {
      songs,
      status,
      currentSong,
      sliderPosition,
      volumeLevel,
      fileInput,
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
      triggerFileInput,
      handleFileUpload,
      deleteSong,
      formatTime
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
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-top: 30px;
}

.upload-area {
  display: flex;
  justify-content: center;
  margin-bottom: 30px;
}

.upload-area input[type="file"] {
  display: none;
}

.upload-btn {
  background-color: #4CAF50;
  color: white;
  padding: 10px 20px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.upload-btn:hover {
  background-color: #45a049;
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
  background-color: #ff9800;
}

.volume-control {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
}

.volume-slider {
  width: 100px;
}

.playlist {
  margin-top: 20px;
}

.playlist ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.playlist li {
  padding: 10px;
  border-bottom: 1px solid #eee;
  cursor: pointer;
}

.playlist li:hover {
  background-color: #f5f5f5;
}

.playlist li.active {
  background-color: #e3f2fd;
}

.song-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.song-name {
  flex: 1;
}

.song-size {
  color: #777;
  margin-right: 10px;
  font-size: 14px;
}

.delete-btn {
  background-color: #f44336;
  color: white;
  border: none;
  border-radius: 4px;
  padding: 5px 10px;
  cursor: pointer;
}

.delete-btn:hover {
  background-color: #d32f2f;
}

.empty-list {
  text-align: center;
  padding: 20px;
  color: #777;
  font-style: italic;
}
</style> 