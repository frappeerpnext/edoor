<template>
  <div :class="bgcolor" class="bg-white rounded-xl px-3 py-2 h-full"> 
    <div class="text-lg font-bold">
        {{$t(label)}} <template v-if="date">- {{ date }}</template> 
    </div>      
    <hr class="mt-1 pb-1 mb-2">
        <slot></slot>
</div> 
 </template>
   
   <script setup>
    import {i18n} from '@/i18n';
    const { t: $t } = i18n.global;
   const props = defineProps({
     label: {
       type: String,
     },
     date: {
       type: String,
       default:""
     },
     bgcolor: {
       type: String,
       default:"bg-white"
     },
   });
   </script>