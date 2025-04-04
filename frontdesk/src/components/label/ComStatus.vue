<template>
    <template v-if="status">
     <span v-if="status=='Unpaid'"   class="border-round-lg line-height-2 py-1 px-3 text-black font-medium bg-red-200 me-1 uppercase">
           Unpaid
        </span>
        
     <span v-else-if="status=='Paid'"   class="border-round-lg line-height-2 py-1 px-3 text-black font-medium bg-green-200 me-1 uppercase">
           Unpaid
        </span>   
     <span v-else-if="status=='Partially Paid'"   class="border-round-lg line-height-2 py-1 px-3 text-black font-medium bg-orange-200 me-1 uppercase">
           Unpaid
        </span>
 
    <ComOpenStatus v-if="status == 'Open' || status == 'Closed'" :status="status" />
</template>
</template>
<script setup>
    const props = defineProps({
        status:String
    })


</script>