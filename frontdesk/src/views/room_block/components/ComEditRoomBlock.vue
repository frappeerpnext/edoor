<template lang="">
    <ComDialogContent @onClose="onClose" @onOK="onSave" :loading="loading">
        
        Block Date
        <div class="card flex justify-content-left">
            <Calendar class="w-14rem" showIcon v-model="data.block_date" disabled dateFormat="dd-mm-yy"/>
        </div>
        Start Date
        <div class="card flex justify-content-left">
            <Calendar class="w-14rem" showIcon v-model="data.start_date" disabled dateFormat="dd-mm-yy"/>
        </div>
        Release Date
        <div class="card flex justify-content-left"> 
            <Calendar class="w-14rem" showIcon v-model="data.end_date" :min-date="new Date(moment(data.start_date).add(1,'days'))" dateFormat="dd-mm-yy"/>
        </div>
        Room Type
        <div class="card flex justify-content-left"> 
            <ComSelectRoomTypeAvailability 
                v-model="data.room_type_id"
                :start-date="data.start_date"
                :end-date="data.end_date"/>
        </div>
        Room Number
        <div class="card flex justify-content-left">
            <ComSelectRoomAvailability 
                v-model="data.room_id"
                :start-date="data.start_date"
                :end-date="data.end_date"
                :roomType="data.room_type_id" 
                exceptField="stay_room_id"
                :exceptValue="data.name"/>
        </div>
        Reason
        <div class="card flex justify-content-left">
            <Textarea v-model="data.reason" rows="5" cols="30" />
        </div>
    </ComDialogContent>
</template>
<script setup>
import {inject,ref, updateDoc} from '@/plugin'
const dialogRef = inject('dialogRef');
const moment = inject('$moment');
const gv = inject('$gv');
const data = ref({})
const loading = ref(false)
data.value = JSON.parse(JSON.stringify(dialogRef.value.data))
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
    })
}
function onClose(){
    dialogRef.value.close()
}
</script>
<style lang="">
    
</style>