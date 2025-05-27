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
  title?: string;       // 歌曲标题（元数据）
  artist?: string;      // 艺术家（元数据）
  album?: string;       // 专辑（元数据）
  duration?: number;    // 时长（元数据）
  metadata?: {          // 完整元数据
    title: string | null;
    artist: string | null;
    album: string | null;
    year: string | null;
    track: string | null;
    genre: string | null;
    duration: number | null;
    bitrate: number | null;
    sample_rate: number | null;
  };
  score?: number;       // 搜索匹配评分
  match_reasons?: string[]; // 搜索匹配原因
}

// 搜索结果接口
export interface SearchResult {
  items: Song[];
  total: number;
  query: string;
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

// 扫描状态接口
export interface ScanStatus {
  is_scanning: boolean;
  last_scan_time: number;
  has_result: boolean;
}

// API服务
export const apiService = {
  // 获取所有歌曲
  getSongs: async (includeMetadata: boolean = false): Promise<Song[]> => {
    const response = await api.get('/api/songs', {
      params: { include_metadata: includeMetadata }
    });
    return response.data;
  },

  // 搜索歌曲
  searchSongs: async (
    query: string,
    limit: number = 50,
    filters?: {
      artist?: string;
      album?: string;
      genre?: string;
      minDuration?: number;
      maxDuration?: number;
    }
  ): Promise<SearchResult> => {
    const params: any = { q: query, limit };
    
    if (filters) {
      if (filters.artist) params.artist = filters.artist;
      if (filters.album) params.album = filters.album;
      if (filters.genre) params.genre = filters.genre;
      if (filters.minDuration !== undefined) params.min_duration = filters.minDuration;
      if (filters.maxDuration !== undefined) params.max_duration = filters.maxDuration;
    }
    
    const response = await api.get('/api/songs/search', { params });
    return response.data;
  },

  // 获取歌曲元数据
  getSongMetadata: async (songId: string): Promise<any> => {
    const response = await api.get(`/api/songs/${songId}/metadata`);
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
  
  // 获取音乐库信息
  getLibraryInfo: async (): Promise<{ libraries: string[]; count: number }> => {
    const response = await api.get('/api/library');
    return response.data;
  },
  
  // 更新音乐库目录
  updateLibrary: async (libraries: string[]): Promise<{ success: boolean; libraries: string[]; count: number }> => {
    const response = await api.post('/api/library', { libraries });
    return response.data;
  },
  
  // 开始异步扫描音乐库
  startLibraryScan: async (includeMetadata: boolean = true): Promise<{ success: boolean; message: string; status: ScanStatus }> => {
    const response = await api.post('/api/library/scan', null, {
      params: { include_metadata: includeMetadata }
    });
    return response.data;
  },
  
  // 获取扫描状态
  getScanStatus: async (): Promise<ScanStatus> => {
    const response = await api.get('/api/library/scan/status');
    return response.data;
  },
  
  // 清除缓存
  clearCache: async (): Promise<{ success: boolean; message: string }> => {
    const response = await api.post('/api/library/clear-cache');
    return response.data;
  },
  
  // 获取完整配置
  getConfig: async (): Promise<Config> => {
    const response = await api.get('/api/settings/config');
    return response.data;
  },
  
  // 更新完整配置
  updateConfig: async (config: Config): Promise<{ success: boolean; message: string }> => {
    const response = await api.put('/api/settings/config', config);
    return response.data;
  }
}; 