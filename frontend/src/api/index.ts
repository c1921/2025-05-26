import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 10000
});

// 歌曲接口
export interface Song {
  id: string;           // MD5 ID
  name: string;
  path: string;
  size: number;
  add_time: number;
  source?: string;      // 音乐来源（library）
  full_path?: string;   // 完整文件路径（仅在后端使用）
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

// 配置接口
export interface Config {
  music_library_dirs: string[];
  supported_formats: string[];
  api_host: string;
  api_port: number;
  api_reload: boolean;
}

// API服务
export const apiService = {
  // 获取所有歌曲
  getSongs: async (): Promise<Song[]> => {
    const response = await api.get('/api/songs');
    return response.data;
  },

  // 播放歌曲
  playSong: async (songId: string): Promise<{ status: string; song: string; duration: number }> => {
    const response = await api.post(`/api/play/${songId}`);
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
  },
  
  // 获取音乐库路径列表
  getMusicLibraries: async (): Promise<string[]> => {
    const response = await api.get('/settings/libraries');
    return response.data;
  },
  
  // 设置音乐库路径列表
  setMusicLibraries: async (directories: string[]): Promise<{ message: string; directories: string[] }> => {
    const response = await api.post('/settings/libraries', { directories });
    return response.data;
  },
  
  // 获取完整配置
  getConfig: async (): Promise<Config> => {
    const response = await api.get('/settings/config');
    return response.data;
  },
  
  // 更新完整配置
  updateConfig: async (config: Config): Promise<{ message: string }> => {
    const response = await api.put('/settings/config', config);
    return response.data;
  },
  
  // 强制刷新音乐库
  refreshMusicLibrary: async (): Promise<{ success: boolean; message: string; file_count: number }> => {
    const response = await api.post('/settings/refresh-library');
    return response.data;
  }
}; 