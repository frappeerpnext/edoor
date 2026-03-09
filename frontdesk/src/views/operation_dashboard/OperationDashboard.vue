<template> 
    <ComHeader isRefresh >
        <template #start>
             Hello
        </template>
        <template #center>
            world
              
        </template>
        <template #end>
           action
        </template>
    </ComHeader>
     
</template>

<script setup>
import { inject, ref, onUnmounted, onMounted, computed } from '@/plugin' 


</script>