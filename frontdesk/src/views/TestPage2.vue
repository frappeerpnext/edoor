<template>
    <div v-if="result">
        {{ result }}
        <ComInputTime v-model="result.drop_off_time" label="Drop Time"/>
        <Button label="Save" @click="onChange()"></Button>
    </div>
</template>
<script setup>
import {ref, updateDoc, getDoc } from '@/plugin'
import ComInputTime from '../components/form/ComInputTime.vue';
const time = ref('12:00:00.000000')
const result = ref()
function onChange(){
    updateDoc('Reservation Stay','ST2023-0162', result.value)
}

getDoc('Reservation Stay','ST2023-0162').then((r)=>{
    result.value = r
})
</script> 