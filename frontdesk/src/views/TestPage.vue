<template>
    <div>
    <ul>
        <li v-for="(item, index) in list" :key="index">
            <slot v-bind:data="item">
              
            </slot>
        </li>
    </ul>
    <div>
        {{ location }}
        <Button @click="updateLocation('is me')">xx</Button>
    </div>
</div>
    
</template>
<script setup>
    import {inject, watchEffect, watchPostEffect} from 'vue'
    const props = defineProps({
        list: Array,
        test: String
    })
    const { location, updateLocation } = inject('location')
    watchEffect(()=>{
        console.log(props.test)
    })
</script>