<template>
    <ul>
        <li v-for="(item, index) in list" :key="index">
            <slot v-bind:data="item">
              
            </slot>
        </li>
    </ul>
</template>
<script setup>
    import {ref} from 'vue'
    const props = defineProps({
        list: Array
    })
</script>