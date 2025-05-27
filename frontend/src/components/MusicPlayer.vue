<template>
  <div class="music-player">
    <!-- 搜索栏组件 -->
    <SearchBar 
      v-model="searchQuery"
      :isSearchMode="isSearchMode"
      @search="handleSearch"
      @clear="clearSearch"
    />
    
    <!-- 播放控制区域组件 -->
    <PlayerControls 
      v-if="currentSong || status.current_song"
      :status="status"
      :currentSong="currentSong"
      :songTitle="songTitle"
      :sliderPosition="sliderPosition"
      :volumeLevel="volumeLevel"
      @play-pause="handlePlayPause"
      @stop="stopPlayback"
      @previous="playPrevious"
      @next="playNext"
      @seek-input="handleSliderInput"
      @seek-change="handleSliderChange"
      @volume-start="handleVolumeStart"
      @volume-change="handleVolumeChange"
      @loop-toggle="handleLoop"
    />
    
    <!-- 播放列表组件 -->
    <PlayList
      :loading="loading"
      :isSearchMode="isSearchMode"
      :searchResults="searchResults"
      :songs="songs"
      :displayedSongs="displayedSongs"
      :status="status"
      @play="playSong"
      @refresh="refreshLibrary"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, onUnmounted } from 'vue';
import { apiService } from '../api';
import type { Song, PlaybackStatus } from '../api';

// 导入子组件
import SearchBar from './music-player/SearchBar.vue';
import PlayerControls from './music-player/PlayerControls.vue';
import PlayList from './music-player/PlayList.vue';

export default defineComponent({
  name: 'MusicPlayer',
  components: {
    SearchBar,
    PlayerControls,
    PlayList
  },
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
</style> 