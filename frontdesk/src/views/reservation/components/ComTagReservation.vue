<template>
<div></div>  
<span class="bg-card-info px-2 rounded-lg me-2" :style="style">
<b>{{ title }} {{ value }}
<slot></slot>
</b>
</span> 
</template>
<script setup>
    const props=defineProps({
        title:String,
        value:String,
        style:String
    })
</script>