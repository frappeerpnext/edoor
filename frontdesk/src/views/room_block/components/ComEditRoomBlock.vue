<template lang="">
    <ComDialogContent @onClose="onClose" @onOK="onSave" :loading="loading">
        <div class="grid">
            <div class="col-6">
                <label>Block Date</label>
                <div>
                    <Calendar selectOtherMonths class="w-full" showIcon v-model="data.block_date" :disabled="data.name" dateFormat="dd-mm-yy"/>
                </div>
            </div> 
            <div class="col-6">
                <label> Room</label>
                <div class="w-full">
                    <ComAutoComplete placeholder="Select Room"  v-model="data.room_id" class="pb-2 w-full"  doctype="Room"
                    @onSelected="onSearch" :filters="['property','=',property.name]" :disabled="doc?.docstatus==1" />
                </div>
            </div>
            <div class="col-6">
                <label>Start Date</label>
                <div>
                    <Calendar selectOtherMonths class="w-full" showIcon v-model="data.start_date"   dateFormat="dd-mm-yy"/>
                </div>
            </div>

            <div class="col-6">
                <label>Release Date</label>
                <div> 
                    <Calendar class="w-full" selectOtherMonths showIcon v-model="data.end_date" :min-date="new Date(moment(data.start_date).add(1,'days'))" dateFormat="dd-mm-yy"/>
                </div>
            </div>
            <div class="col-12">
                <label>Reason</label>
                <div class=" card w-full flex justify-content-left">
                    <Textarea class="w-full" v-model="data.reason" autoResize />
                </div>
            </div> 
        </div>
    </ComDialogContent>
</template>
<script setup>
import {inject,ref, createUpdateDoc, onMounted} from '@/plugin'
const dialogRef = inject('dialogRef');
const gv = inject('$gv');
const moment = inject('$moment');
const data = ref({})
const loading = ref(false)
const property = JSON.parse(localStorage.getItem("edoor_property"))
 
function onSave (){
    if(!data.value.end_date){
        gv.toast('warn', 'Please select release date.')
        return
    }
    else if(!data.value.reason){
        gv.toast('warn', 'Please input reason.')
        return
    }
    loading.value = true
    var savedData = {
        name: data.value.name,
        end_date: gv.dateApiFormat(data.value.end_date),
        block_date: gv.dateApiFormat(data.value.block_date),
        start_date: gv.dateApiFormat(data.value.start_date),
        room_type_id: data.value.room_type_id,
        room_id: data.value.room_id,
        reason: data.value.reason,
        property: data.value.property,
        is_auto_submit: true
    }
    createUpdateDoc('Room Block', {data: savedData}).then((r)=>{
        dialogRef.value.close(r)
        window.socket.emit("RoomBlockList", window.property_name)
        window.socket.emit("Frontdesk", window.property_name)
        window.socket.emit("ComHousekeepingStatus", window.property_name)
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
        data.value.block_date = moment().toDate()
        data.value.start_date = moment().toDate()
        data.value.end_date = moment().toDate()
        data.value.property = property.name
    }
})
</script>
<style lang="">
    
</style>