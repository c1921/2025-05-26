import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000
});

// 歌曲接口
export interface Song {
  id: number;
  name: string;
  path: string;
  size: number;
  add_time: number;
}

// 播放状态接口
export interface PlaybackStatus {
  active: boolean;
  playing: boolean;
  current_song: string | null;
  position: number;
  duration: number;
  volume: number;
  loop: boolean;
}

// API服务
export const apiService = {
  // 获取所有歌曲
  getSongs: async (): Promise<Song[]> => {
    const response = await api.get('/api/songs');
    return response.data;
  },

  // 上传歌曲
  uploadSong: async (file: File): Promise<{ filename: string; status: string }> => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  },

  // 删除歌曲
  deleteSong: async (filename: string): Promise<{ filename: string; status: string }> => {
    const response = await api.delete(`/api/songs/${filename}`);
    return response.data;
  },

  // 播放歌曲
  playSong: async (filename: string): Promise<{ status: string; song: string; duration: number }> => {
    const response = await api.post(`/api/play/${filename}`);
    return response.data;
  },

  // 暂停播放
  pauseSong: async (): Promise<{ status: string }> => {
    const response = await api.post('/api/pause');
    return response.data;
  },

  // 恢复播放
  resumeSong: async (): Promise<{ status: string }> => {
    const response = await api.post('/api/resume');
    return response.data;
  },

  // 停止播放
  stopSong: async (): Promise<{ status: string }> => {
    const response = await api.post('/api/stop');
    return response.data;
  },

  // 设置播放位置
  seekPosition: async (position: number): Promise<{ status: string; position: number }> => {
    const response = await api.post('/api/seek', { position });
    return response.data;
  },

  // 设置音量
  setVolume: async (volume: number): Promise<{ status: string; volume: number }> => {
    const response = await api.post('/api/volume', { volume });
    return response.data;
  },

  // 设置循环播放
  setLoop: async (loop: boolean): Promise<{ status: string; loop: boolean }> => {
    const response = await api.post('/api/loop', { loop });
    return response.data;
  },

  // 获取播放状态
  getStatus: async (): Promise<PlaybackStatus> => {
    const response = await api.get('/api/status');
    return response.data;
  }
}; 