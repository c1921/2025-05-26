<template>
  <div class="search-bar">
    <input 
      type="text" 
      :value="modelValue" 
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
      placeholder="搜索歌曲、艺术家或专辑..." 
      @keyup.enter="$emit('search')"
    />
    <button class="search-btn" @click="$emit('search')">搜索</button>
    <button class="clear-btn" @click="$emit('clear')" v-if="isSearchMode">清除</button>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue';

export default defineComponent({
  name: 'SearchBar',
  props: {
    modelValue: {
      type: String,
      required: true
    },
    isSearchMode: {
      type: Boolean,
      default: false
    }
  },
  emits: ['update:modelValue', 'search', 'clear']
});
</script>

<style scoped>
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
</style> 