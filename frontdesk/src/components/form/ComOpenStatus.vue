<template>
   
        <Chip label="Open" v-if="status=='Open'" class="bg-yellow-500"/>
        <Chip label="Close" v-else class="bg-red-500"/>
        when u see me pls fix me and remove me

</template>
<script setup>
    const props =defineProps({
        status:{
            type:String,
            default:"Open"
        }
    }
    )
</script>