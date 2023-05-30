<template >
    <div id="xx">
        {{ room_type }}
        <ComSelect v-model="room_type" optionLabel="label" optionValue="value" :options="list" @onSelected="onSelected"/>

        <ComSelect extraFields="housekeeping_icon" isMultipleSelect doctype="Room" groupFilterField="room_type_id" :groupFilterValue="room_type" optionValue="name" optionLabel="room_number" v-model="room" @onSelected="onSelected"/>
 
    </div>
</template>
<script setup>
import {ref} from 'vue'
 let room = ref({
    backgroundColor: '#000'
 })
 let room_type = ref([])
 let list = ref([{'label': 'Male', 'value': 'm'},{'label': 'Female', 'value': 'f'}])
 function onSelected(x){
    console.log(x)
 }
</script> 
<style>
 
</style>