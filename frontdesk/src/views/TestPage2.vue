
<template>
    <div>
        <Calendar v-model="date" />
        <Calendar v-model="endDate" />
        {{s}}
        <ComSelect v-model="s" doctype="Business Source" valueOption="name" labelOption="business_source"/>
        <ComSelect v-model="t" doctype="Rate Type" valueOption="name" labelOption="rate_type"/>
        {{x}}
        <ComSelectRoomTypeAvailability v-model="x" :business-source="s" :start-date="date" :end-date="endDate" :rate-type="t" @onSelected="onSelected"/>
    </div>
</template>

<script setup>
 import {ref} from 'vue'
 const date = ref(new Date())
 const endDate = ref(new Date())
 const s = ref()
 const t = ref()
 const x = ref('RT-0004')
 function onSelected(r){
    console.log(r)
 }
</script>