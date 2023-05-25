<template >
    <div>
        <ComSelect doctype="Room Type" v-model="room_type" @onSelected="onSelected"/>

        <ComSelect doctype="Room" groupFilterField="room_type_id" :groupFilterValue="room_type" optionValue="room_number" optionLabel="name" v-model="room" @onSelected="onSelected"/>
    </div>
</template>
<script setup>
import {ref} from 'vue'
 let room = ref('')
 let room_type = ref('RT-0005')
 let list = ref([{label: 'Male', value: 'm'},{label: 'Female', value: 'f'}])
 function onSelected(x){
    console.log(x)
 }
</script> 