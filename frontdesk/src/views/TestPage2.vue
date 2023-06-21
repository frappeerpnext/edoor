<template>
    <div>
        {{ data }}
    </div>
</template>
<script setup>
import {ref, getApi} from '@/plugin'
const data = ref()
await getApi('reservation.get_audit_test',{
                doctype: "Reservation Stay",
                docname: "ST2023-0255"
            }).then((r)=>{
                data = r
            })
</script>
<style lang="">
    
</style>