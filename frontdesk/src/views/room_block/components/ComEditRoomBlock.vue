<template lang="">
    <ComDialogContent @onClose="onClose" @onOK="onSave" :loading="loading">
  
        <div class="grid">
            <div class="col-6">
                <label>Block Date</label>
                <div>
                    <Calendar selectOtherMonths class="w-full" showIcon v-model="data.block_date" :manualInput="false" :disabled="true" :min-date="working_day" dateFormat="dd-mm-yy"/>
                </div>
            </div> 
            <div class="col-6">
                <label> Room</label>
                <div class="w-full">
                    <ComAutoComplete placeholder="Select Room"  v-model="data.room_id" class="pb-2 w-full"  doctype="Room"
                    @onSelected="onSearch" :filters="['property','=',property.name]" :disabled="doc?.docstatus==1" />
                </div>
            </div>
            <div class="col-12"> 
                <div class="grid">
                    <div class="col-12 md:col">
                        <label>Start Date</label>
                        <div>
                            <Calendar showButtonBar panelClass="no-btn-clear" @date-select="onSelectStartDate" selectOtherMonths class="w-full" showIcon v-model="data.start_date" :min-date="working_day" dateFormat="dd-mm-yy"/>
                        </div>
                    </div>
                    <div class="night__wfit col-fixed px-0" style="width: 150px;">
                        <div>
                            <label class="invisible">Room Night<span class="text-red-500">*</span></label>
                        </div>
                        <ComReservationInputNight v-model="data.total_night"
                            @onUpdate="onRoomNightChanged" />
                    </div>
                    <div class="col">
                        <label>Release Date</label>
                        <div>
                            <Calendar showButtonBar panelClass="no-btn-clear" @date-select="onDateSelect" class="w-full" selectOtherMonths showIcon v-model="data.end_date" :min-date="new Date(moment(data.start_date).add(1, 'days').toDate())" dateFormat="dd-mm-yy"/>
                        </div>
                    </div>
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
import { inject, ref, createUpdateDoc, onMounted, watch } from '@/plugin'
import ComReservationInputNight from '@/views/reservation/components/ComReservationInputNight.vue';
const dialogRef = inject('dialogRef');
const gv = inject('$gv');
const isMobile = ref(window.isMobile) 
const moment = inject('$moment');
const data = ref({})
const loading = ref(false)
const property = JSON.parse(localStorage.getItem("edoor_property"))
const working_day = moment(window.current_working_date).toDate()


function onSave() {
    if (!data.value.room_id) {
        gv.toast('warn', 'Please select room.')
        return
    }
    else if (!data.value.end_date) {
        gv.toast('warn', 'Please select release date.')
        return
    }
    else if (!data.value.reason) {
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
        is_auto_submit: true,
        total_night_count: data.value.total_night
    }
    createUpdateDoc('Room Block', savedData).then((r) => {
        dialogRef.value.close(r)
        window.postMessage({action:"Housekeeping"},"*")
        loading.value = false
    }).catch((err) => {
        loading.value = false
    })
}
function onClose() {

    dialogRef.value.close()
}

onMounted(() => {
    if(window.isMobile){
    const elem = document.querySelector(".p-dialog");
		elem?.classList.add("p-dialog-maximized"); // adds the maximized class

 }
    if (dialogRef.value.data.name) {
        data.value = JSON.parse(JSON.stringify(dialogRef.value.data))
        data.value.start_date = moment(data.value.start_date).toDate()
        data.value.end_date = moment(data.value.end_date).toDate()
        data.value.block_date = moment(data.value.block_date).toDate()
        data.value.total_night = moment(data.value.end_date).diff(moment(data.value.start_date), 'days')

    } else {
        data.value.block_date = moment(window.current_working_date).toDate()
        data.value.room_id = dialogRef.value.data.room_id
        if (dialogRef.value.data.date){
            data.value.start_date = dialogRef.value.data.date
        }else {
            data.value.start_date = moment(window.current_working_date).toDate()
        }
        

        data.value.end_date = moment(data.value.start_date).add(1, 'days').toDate()
        data.value.property = property.name
    }
 
})

const onSelectStartDate = (date) => {
    if (moment(date).isSame(moment(data.value.end_date).format("yyyy-MM-DD")) || moment(date).isAfter(data.value.end_date)) {
        data.value.end_date = moment(date).add(1, 'days').toDate();
    }
}

const onRoomNightChanged = (event) => {
    data.value.end_date = moment(data.value.start_date).add(event, "Days").toDate()
}

watch(() => [data.value.start_date, data.value.end_date], ([newStartDate, newEndDate], [oldStartDate, oldEndDate]) => {
    data.value.total_night = moment(newEndDate).diff(moment(newStartDate), 'days')
}) 
</script>
<style lang="">
    
</style>