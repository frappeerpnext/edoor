<template>
    <ComDialogContent @onOK="onOk"   hideButtonClose titleButtonOK="Ok" :hideIcon="true">
    <h1>Reason:</h1>
    <Textarea v-model="note" rows="3" cols="50" placeholder="Please enter reason"/>
    </ComDialogContent>

</template>
<script setup>
import { inject, ref } from "@/plugin"
import { useToast } from "primevue/usetoast";

import Textarea from 'primevue/textarea';
const dialogRef = inject("dialogRef");
const toast = useToast();

const note = ref("")
function onOk(){
    if(note.value){
        dialogRef.value.close(note.value);
    }else{
        toast.add({ severity: 'warn', summary: 'Enter Note', detail: "Please enter note", life: 3000 })
    }
    
}
</script>