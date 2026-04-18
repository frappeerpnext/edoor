<template>
    <div>Channel manger sync status all status</div>
    {{ data }}
</template>
<script setup>
import { onMounted, ref } from 'vue';

const data = ref()
const property = JSON.parse(localStorage.getItem("edoor_property"))
async function getData(){
    const res = await app.getApi("edoor.channel_managers.utils.get_all_cm_sync_status",{
        property:property.name
    })
    if(res.data){
        data.value = res.data
    }
}

onMounted(async ()=>{
    await getData()
})

</script>