<template>
    
    <Button style="height: 20px!important;font-size: 10px!important;" v-if="status='Closed'" :label="status" severity="warn" rounded  />
    <Button style="height: 20px!important;font-size: 10px!important;" v-else="status='Closed'" :label="status" severity="success" rounded  />
</template>
<script setup>
    const props = defineProps({
        status:String
    })


</script>