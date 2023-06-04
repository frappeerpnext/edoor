<template>
<div class="px-2 rounded-lg me-2 font-bold inline-block" :class="class">
{{ title }} {{ value }}
<slot></slot>
</div> 
</template>
<script setup>
import { inject } from '@/plugin'
    const props=defineProps({
        title:String,
        value:String,
        class:String
    })
const rs = inject('$reservation_stay');   
</script>