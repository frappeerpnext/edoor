<template >
    <div>
        {{ room_type }}
        <ComSelect isMultipleSelect doctype="Room Type" v-model="room_type" optionValue="name" optionLabel="room_type" @onSelected="onSelected"/>

        <ComSelect extraFields="housekeeping_icon" isMultipleSelect doctype="Room" groupFilterField="room_type_id" :groupFilterValue="room_type" optionValue="name" optionLabel="room_number" v-model="room" @onSelected="onSelected"/>
 
    </div>
</template>
<script setup>
import {ref} from 'vue'
 let room = ref()
 let room_type = ref([])
 let list = ref([{label: 'Male', value: 'm'},{label: 'Female', value: 'f'}])
 function onSelected(x){
    console.log(x)
 }
</script> 