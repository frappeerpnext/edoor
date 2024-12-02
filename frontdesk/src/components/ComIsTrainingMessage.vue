<template>
    <div class="training_site" v-if="is_training_site==1">
        This is training site
    </div>
    
</template>
<script setup>
import {ref, getApi,onMounted } from "@/plugin"
const is_training_site = ref(0)
onMounted(()=>{
    getApi("api.is_training_site","","epos_restaurant_2023.api.").then(result=>{
        console.log(result)
        is_training_site.value = result.message
    })
})
</script>