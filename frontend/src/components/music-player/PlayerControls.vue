<template>
  <div class="player-controls">
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
        :value="sliderPosition"
        @input="$emit('seek-input', $event)"
        @change="$emit('seek-change')"
        class="progress-slider"
      />
      <span class="time">{{ formatTime(status.duration) }}</span>
    </div>
    
    <!-- 控制按钮 -->
    <div class="control-buttons">
      <button @click="$emit('loop-toggle')" :class="{ active: status.loop }" class="loop-btn">
        {{ status.loop ? '循环开' : '循环关' }}
      </button>
      <button @click="$emit('previous')" class="control-btn">上一首</button>
      <button @click="$emit('play-pause')" class="control-btn main-btn">
        {{ status.playing ? '暂停' : '播放' }}
      </button>
      <button @click="$emit('stop')" class="control-btn">停止</button>
      <button @click="$emit('next')" class="control-btn">下一首</button>
    </div>
    
    <!-- 音量控制 -->
    <div class="volume-control">
      <span>音量:</span>
      <input 
        type="range" 
        min="0" 
        max="1" 
        step="0.01"
        :value="volumeLevel"
        @input="$emit('volume-start')"
        @change="$emit('volume-change')"
        class="volume-slider"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';
import type { Song, PlaybackStatus } from '../../api';

export default defineComponent({
  name: 'PlayerControls',
  props: {
    status: {
      type: Object as () => PlaybackStatus,
      required: true
    },
    currentSong: {
      type: Object as () => Song | null,
      default: null
    },
    songTitle: {
      type: String,
      default: ''
    },
    sliderPosition: {
      type: Number,
      default: 0
    },
    volumeLevel: {
      type: Number,
      default: 1
    }
  },
  emits: [
    'play-pause', 'stop', 'previous', 'next', 
    'seek-input', 'seek-change', 
    'volume-start', 'volume-change', 
    'loop-toggle'
  ],
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
</style> 