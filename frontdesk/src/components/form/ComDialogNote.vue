<template>
    <Dialog :header="header" :visible="show" @update:visible="onHide" modal>
        <Message v-if="confirm_message" >
            <div v-html="confirm_message" />
        </Message>
    
        <ComNote :loading="loading" :value="note" :autoClose="false" @ok="onOk"/>

        <div v-if="show_reserved_room" class="py-2">
            <Checkbox inputId="no_show_sell_room" v-model="reserved_room" :binary="true" />
            <label for="no_show_sell_room" class="ml-1 cursor-pointer">Reserved room for this reservation.</label>
        </div>
    </Dialog>
</template>
<script setup>
import Message from 'primevue/message';
import {computed,ref} from 'vue'

const emit = defineEmits(['onOk','onClose'])
const props = defineProps({
    visible: Boolean,
    header: String,
    value:{
        type:String,
        default:''
    },
    loading: Boolean,
    confirm_message: String,
    show_reserved_room:Boolean
})
 
const reserved_room = ref(true)

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
    emit('onOk',{note:note ,reserved_room:reserved_room.value }) 
}
function onHide(){
    emit('onClose')
}
</script>
<style lang="">
    
</style>