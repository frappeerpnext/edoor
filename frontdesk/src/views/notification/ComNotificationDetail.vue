<template>
    <ComDialogContent :titleButtonOK="'View ' + doc.document_type + ' Detail'" @onOK="onViewDetail"   :loading="isSaving" hideButtonClose>
        <!-- {{ $t('Notification Detail') }} -->
        <div class="flex gap-2 align-items-center">
            <div>
                <Avatar :label="avatar_letter" class="mr-2" size="large" style="background-color: #ece9fc; color: #2a1261;border-radius: 50% !important;" shape="circle" />
            </div> 
            <div>
                <div><strong>{{ doc.modified_by }}</strong></div>
                <i><ComTimeago :date='doc.modified' /></i>
            </div>
        </div>
        <div>
            <hr class="my-3"/>
            <!-- <Message :closable="false" severity="info" icon="pi pi-bell" ></Message>   -->
            <div style="white-space: pre-line;" v-html="doc.subject"></div>
        </div> 
 
        
        
    </ComDialogContent>
</template>
<script setup>

import { defineComponent, onMounted } from 'vue';
import {ref,inject,updateDoc} from "@/plugin"
const dialogRef = inject('dialogRef');
const avatar_letter = ref('')
const doc = ref({})
function onViewDetail(){
   
 
    window.postMessage(`view_${doc.value.document_type.toLowerCase().replaceAll(" ","_")}_detail|${doc.value.document_name}`,"*")
}
onMounted(()=>{
    doc.value = dialogRef.value.data
    avatar_letter.value = doc.value.modified_by.charAt(0).toUpperCase()
    console.log(doc.value)
    // set as reat

        updateDoc("Notification Log",doc.value.name,{read:1},"",false)
   

    
})
</script>