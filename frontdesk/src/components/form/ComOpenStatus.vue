<template>
   
        <span v-if="status=='Open'" class=" line-height-2 py-1 px-3 text-green-700 font-medium border-round-lg bg-green-200 me-1">
            OPEN
        </span>
        <span v-else class="border-round-lg line-height-2 py-1 px-3 text-black font-medium bg-gray-200 me-1">
            CLOSE
        </span>
        <!-- <Chip label="Close" v-else class="bg-red-500"/> -->

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