<template>
    <ComDialogContent @onClose="onClose()" :hideButtonOK="true"   :hideButtonClose="False" :hideIcon="false" :loading="loading">
        {{ data }} 
        <hr/>
        {{ dialogRef.data.room_type_rate  }}
    </ComDialogContent>

</template>
<script setup>
import {ref,inject,onMounted,getApi} from "@/plugin"

const dialogRef = inject("dialogRef");
const data = ref()
const loading = ref(false)
function onClose(){
    dialogRef.value.close();
}
onMounted(()=>{
    loading.value = true
    getApi("utils.get_package_detail",{
        rate_type:dialogRef.value.data.rate_type,
        date:dialogRef.value.data.date,
        property: window.property_name,
        business_source:dialogRef.value.data.business_source
    }).then(result=>{
        data.value = result.message
        loading.value = false
    }).catch(err=>{
        loading.value = false
    })
})


</script>