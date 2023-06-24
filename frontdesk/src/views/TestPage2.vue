<template>
    <div>
        {{ x }}
        <ComInputCurrency v-model="x"/>
    </div>
</template>
<script setup> 
import {ref} from 'vue'
const x = ref(0)
// import {ref, getApi} from '@/plugin'
// const data = ref()
// await getApi('reservation.get_audit_test',{
//                 doctype: "Reservation",
//                 docname: "RS2023-0217"
//             }).then((r)=>{
//                 data = r
//             })
</script>
<style lang="">
    
</style>