<template>
    <ul>
        <li v-for="(item, index) in list" :key="index">
            <slot v-bind:data="item">
              
            </slot>
        </li>
    </ul>
    {{ test }}zz
</template>
<script setup>
    import {ref, watchEffect, watchPostEffect} from 'vue'
    const props = defineProps({
        list: Array,
        test: String
    })
    watchEffect(()=>{
        console.log(props.test)
    })
</script>