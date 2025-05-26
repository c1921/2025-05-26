<script setup lang="ts">
import MusicPlayer from './components/MusicPlayer.vue'
</script>

<template>
  <div class="app-container">
    <MusicPlayer />
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
</style>
