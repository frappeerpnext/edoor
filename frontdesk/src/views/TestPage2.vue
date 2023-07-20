<template>
    <div> 
        {{ rs }}
        <ComAutoComplete doctype="Reservation" v-model="r"/>
        <ComAutoComplete field-filter="reservation" :value-filter="r" doctype="Reservation Stay" v-model="rs"/>
    </div>
</template>
<script setup> 
import {ref, getApi} from '@/plugin'
import ComAutoComplete from '../components/form/ComAutoComplete.vue';
const rs = ref()
const r = ref()
</script>
<style lang="">
    
</style>