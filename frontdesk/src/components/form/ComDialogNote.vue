<template>
    <Dialog :header="header" v-model:visible="show" @update:visible="onHide" modal>
        <ComNote :loading="loading" :value="note" :autoClose="false" @ok="onOk"/>
    </Dialog>
</template>
<script setup>
import {computed} from 'vue'
const emit = defineEmits(['onOk','onClose'])
const props = defineProps({
    visible: Boolean,
    header: String,
    value:{
        type:String,
        default:''
    },
    loading: Boolean
})

let show = computed({
    get(){ 
        return props.visible
    },
    set(newValue){ 
        return newValue
    }
})

let note = computed({
    get(){
        return props.value
    },
    set(newValue){
        return newValue
    }
})
function onOk(note){
    emit('onOk',note) 
}
function onHide($event){
    show.value = $event 
    emit('onClose')
}
</script>
<style lang="">
    
</style>