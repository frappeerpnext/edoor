<template >
    <div id="xx">
        {{ room_type }}
        <ComSelect v-model="room_type" optionLabel="label" optionValue="value" :options="list" @onSelected="onSelected"/>

        <ComSelect extraFields="housekeeping_icon" isMultipleSelect doctype="Room" groupFilterField="room_type_id" :groupFilterValue="room_type" optionValue="name" optionLabel="room_number" v-model="room" @onSelected="onSelected"/>
        <Button @click="onShow">xxx</Button>
        <Button @click="onPrime">Prime</Button>
    </div>
</template>
<script setup>
import {ref, showToast, useToast} from '@/plugin'
const toast = useToast()
 let room = ref({
    backgroundColor: '#000'
 })
 let room_type = ref([])
 let list = ref([{'label': 'Male', 'value': 'm'},{'label': 'Female', 'value': 'f'}])
 function onSelected(x){
    console.log(x)
 }
 function onShow(){
    showToast()
 }
 function onPrime(){
    toast.add({ severity: 'success', summary: 'Success Message', detail: 'Message Content', life: 3000000 });
 }
</script> 
<style>
 
</style>