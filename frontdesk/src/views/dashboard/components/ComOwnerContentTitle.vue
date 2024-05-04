<template>
  <div class="bg-white rounded-xl px-3 py-2 h-full"> 
    <div class="text-lg font-bold">
        {{label}}  
    </div>      
    <hr class="mt-1 pb-1 mb-2">
    <div class="grid"> 
        <slot></slot>
    </div>
</div> 
 </template>
   
   <script setup>
   const props = defineProps({
     label: {
       type: String,
     },
   });
   </script>