<template>
    <ComDialogContent :hideButtonClose="true" :hideButtonOK="true">
        <template v-if="data">
        
            <ComServerReportViewer 
        :report_name="data?.report_path" 
        :params ="data?.params" 
        />
        </template>
       
        
    </ComDialogContent>
</template>
<script setup>
import {ref,onMounted,inject} from "@/plugin"
import ComServerReportViewer from "@/components/ComServerReportViewer.vue";
 
const dialogRef = inject("dialogRef");
const data = ref()
onMounted(()=>{
    data.value = dialogRef.value.data
})

</script>
 