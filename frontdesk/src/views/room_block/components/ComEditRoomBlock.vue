<template lang="">
    <ComDialogContent @onClose="onClose" @onOK="onSave" :loading="loading">
        <div class="grid">
        <div class="col-12 p-0">
            <div class="w-6 col">
                <label>Block Date</label>
            <div class="card flex justify-content-left">
                <Calendar class="w-full" showIcon v-model="data.block_date" disabled dateFormat="dd-mm-yy"/>
            </div>
            </div>
        </div>
        <div class="col-12 lg:col-6">
            <label>Start Date</label>
            <div class="card flex justify-content-left">
                <Calendar class="w-full" showIcon v-model="data.start_date" disabled dateFormat="dd-mm-yy"/>
            </div>
        </div>
        <div class="col-12 lg:col-6">
            <label>Release Date</label>
            <div class="card flex justify-content-left"> 
                <Calendar class="w-full" selectOtherMonths showIcon v-model="data.end_date" :min-date="new Date(moment(data.start_date).add(1,'days'))" dateFormat="dd-mm-yy"/>
            </div>
        </div>
        <div class="col-12">
 
      
        </div>
        <div class="col-12 lg:col-6">
        <label> Room Name </label>
        <div class="w-full card flex justify-content-left">
            <ComAutoComplete  v-model="data.room_id" class="pb-2"  doctype="Room"
            @onSelected="onSearch" :filters="['property','=',property.name]" />
        </div>
        </div>
        <div class="col-12">
            <label>Reason</label>
        <div class=" card w-full flex justify-content-left">
            <Textarea class="w-full" v-model="data.reason" />
        </div>
        </div>
    </div>
    </ComDialogContent>
</template>
<script setup>
import {inject,ref, updateDoc, getDoc, onMounted} from '@/plugin'
const dialogRef = inject('dialogRef');
const gv = inject('$gv');
const moment = inject('$moment');
const data = ref({})
const loading = ref(false)
const property = JSON.parse(localStorage.getItem("edoor_property"))
 
function onSave (){
    loading.value = true
    var savedData = {
        name: data.value.name,
        end_date: gv.dateApiFormat(data.value.end_date),
        room_type_id: data.value.room_type_id,
        room_id: data.value.room_id,
        reason: data.value.reason
    }
    updateDoc('Room Block', data.value.name, savedData).then((r)=>{
        dialogRef.value.close(r)
        loading.value = false
    }).catch((err)=>{
        loading.value = false
    })
}
function onClose(){

    dialogRef.value.close()
}

onMounted(()=>{

    if(dialogRef.value.data.name){
       
        data.value = JSON.parse(JSON.stringify(dialogRef.value.data))
        data.value.start_date =moment(data.value.start_date).toDate()
        data.value.end_date = moment(data.value.end_date).toDate()
        data.value.block_date = moment(data.value.block_date).toDate()
      
    }else {
    }
})
</script>
<style lang="">
    
</style>