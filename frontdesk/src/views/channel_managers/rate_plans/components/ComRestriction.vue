<template>
        restrictuion
    </template>
<script setup>
import { onMounted } from 'vue';


onMounted(async()=>{
    const l = await window.showLoading()
    setTimeout(() => {
        l.close()
    }, 3000);
})
</script>