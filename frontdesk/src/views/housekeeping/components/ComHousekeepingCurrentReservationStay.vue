
<template>
    <div class="card">
        <div class="flex gap-2 justify-content-center">
            <Button icon="pi pi-arrow-left" @click="visibleRight = true" />
        </div>
  
        <Sidebar v-model:visible="visibleRight" position="right">
            <h2>Right Sidebar</h2>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
        </Sidebar>
  
    </div>
  </template>

  <script setup>

  import { ref } from "vue";
  const visibleRight = ref(false);
  
  </script>