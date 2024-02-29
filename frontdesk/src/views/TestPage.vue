<template>
   
  
    <div class="drag-container">
      {{ $t('Close Shift') }}
    </div>
  </template>
  
  <script setup>
  import { ref } from 'vue';
  const colors = ref(['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet', 'pink', 'brown', 'gray']);
  const grid = ref([]);
  
  for (let i = 0; i < 400; i++) {
    grid.value.push({ id: i, content: { text: '', color: '' } });
  }
  
  const dragItem = ref(null);
  
  function dragStart(e, content) {
    e.dataTransfer.setData('text/plain', content.text);
    dragItem.value = content;
  }
  
  function drop(e, item) {
    const indexItem = grid.value.indexOf(item);
    
    if (dragItem.value !== null && !grid.value.some((item) => item.content.text === dragItem.value.text)) {
      grid.value[indexItem].content = dragItem.value;
      colors.value.splice(colors.value.indexOf(dragItem.value.color),1);
      dragItem.value = null;
      return true;
     }
     return false;
  }
  
  function allowDrop(e) {
     e.preventDefault();
  }
  
  </script>
  
  <style scoped>
  .grid-container {
    display: grid;
    grid-template-columns: repeat(20, auto);
  }
  
  .grid-item {
    border: 1px solid black;
    height: 50px;
  }
  
  .grid-item > div {
    width: 100%;
    height: 100%;
  }
  
  .drag-container {
    display: flex;
  }
  
  .drag-item {
    width: 50px;
    height: 50px;
    border: solid black;
  }
  </style>
  