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
        <hr class="my-3"/>
        <div class="p-2 border-round-xl surface-50 mb-3 px-2">
            
            <div style="white-space: pre-line;" v-html="doc.subject"></div>
        </div> 
 <ComNotificationInfo v-if="doc" :doc="doc"></ComNotificationInfo>
        
    </ComDialogContent>
</template>
<script setup>

import { defineComponent, onMounted } from 'vue';
import {ref,inject,updateDoc} from "@/plugin"
import ComNotificationInfo from "@/views/notification/ComNotificationInfo.vue" 
const dialogRef = inject('dialogRef');
const avatar_letter = ref('')
const doc = ref({})

function onViewDetail(){

   window.postMessage(`view_${doc.value.document_type.toLowerCase().replaceAll(" ","_")}_detail|${doc.value.document_name}`,"*")
}
onMounted(()=>{
    doc.value = dialogRef.value.data
    avatar_letter.value = doc.value.modified_by.charAt(0).toUpperCase()
  

        updateDoc("Notification Log",doc.value.name,{read:1},"",false)
   

    
})
</script>