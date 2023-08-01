<template>
    <ComDialogContent @onOK="onOk" hideButtonClose titleButtonOK="Ok" :hideIcon="false" :loading="loading">
        <label for="reason-text" class="mb-1 font-medium block">Reason</label>
        <Textarea v-model="note" id="reason-text" rows="3" cols="50" placeholder="Please Enter Reason" class="w-full"/>
    </ComDialogContent>

</template>
<script setup>
import { inject, ref } from "@/plugin"
import { useToast } from "primevue/usetoast";
import Textarea from 'primevue/textarea';
const dialogRef = inject("dialogRef");
const toast = useToast();
const emit = defineEmits('ok')
const props = defineProps({
    loading: Boolean,
    value:{
        type:String,
        default:''
    },
    autoClose: {
        type: Boolean,
        default: true
    }
})
const note = ref(props.value)

function onOk(){
    if(note.value){
        if(props.autoClose){
            dialogRef.value.close(note.value);
        }
        else{
            emit('ok', note.value)
        }
    }else{
        toast.add({ severity: 'warn', summary: 'Enter Note', detail: "Please Enter Note", life: 3000 })
    }
    
}
</script>