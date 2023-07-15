<template>
    <div>
       {{ data }}
    </div>
</template>
<script setup>
import {ref, getDoc} from '@/plugin'
const data = ref()
getDoc("Reservation Stay","ST2023-1057").then((r)=>{
    data.value = r
})
</script>
<style lang="">
    
</style>