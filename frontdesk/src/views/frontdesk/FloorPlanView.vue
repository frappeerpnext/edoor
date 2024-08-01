<template>
    <div v-interact="{ draggable: true, resizable: true }" class="draggable-box">
      Drag and Resize Me!
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  
  const x = ref(0);
  const y = ref(0);
  </script>
  
  <style>
  .draggable-box {
    width: 100px;
    height: 100px;
    background-color: lightblue;
    display: flex;
    justify-content: center;
    align-items: center;
    user-select: none;
    touch-action: none;
    position: relative;
  }
  </style>
  