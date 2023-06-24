<template>
    <ComDialogContent @onClose="onClose" @onOK="onSave" :loading="loading">
    <div>
        <ComReservationStayPanel title="Change Stay">
            <template #content> 
            <div class="n__re-custom">
                {{ maxDate }}
                <table class="w-full">
                    <thead>
                        <tr>
                            <th class="text-left">
                                <label>Start Date<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-left">
                                <label>End Date<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-center">
                                <label class="text-center">Nights</label>
                            </th>
                            <th class="text-left">
                                <label>Room Type<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-left">
                                <label>Room Name<span class="text-red-500">*</span></label>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td> 
                                <Calendar v-model="stay.start_date" :disabled="rs.reservationStay.reservation_status == 'Checked In'" :min-date="new Date(working_day.date_working_day)" @update:modelValue="onStartDate" dateFormat="dd-mm-yy"/>
                            </td>
                            <td>
                                <Calendar v-model="stay.end_date" :min-date="minDate" @update:modelValue="onEndDate" dateFormat="dd-mm-yy"/>
                            </td>
                            <td class="text-center"> 
                                <InputNumber v-model="stay.room_nights" @update:modelValue="onNight" inputId="stacked-buttons" showButtons :min="1" class="child-adults-txt" />
                            </td>
                            <td> 
                                {{ stay.room_type }}
                            </td>
                            <td>
                                {{ stay.room_number }}
                            </td> 
                        </tr>
                    </tbody>
                </table>
            </div>
            </template>
        </ComReservationStayPanel>
    </div>
</ComDialogContent>
</template>
<script setup>
    import {inject,ref, getApi, onMounted,postApi, useDialog, computed,watch} from '@/plugin'
    import ComReservationStayPanel from './ComReservationStayPanel.vue';
    import Enumerable from 'linq'
    const property = JSON.parse(localStorage.getItem("edoor_property"))
    const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
    const rs = inject('$reservation_stay') 
    const moment = inject('$moment')
    const gv = inject('$gv')
    const dialogRef = inject('dialogRef'); 
    const loading = ref(false)
    const stay = ref(JSON.parse(JSON.stringify(dialogRef.value.data.item)))
    stay.value.start_date = moment(stay.value.start_date).toDate()
    stay.value.end_date = moment(stay.value.end_date).toDate()
    const minDate = computed(()=>{
        if(moment(stay.value.start_date).isSame(working_day.date_working_day) || moment(stay.value.start_date).isBefore(working_day.date_working_day)){
            return new Date(moment(working_day.date_working_day))
        }else{
            return new Date(moment(stay.value.start_date).add(1,'days'))
        }
    })
    const maxDate = computed(()=>{
        const data = Enumerable.from(rs.reservationStay.stays).orderBy("$.start_date").toArray()
        console.log(data)
        console.log(stay.value.name)
        const ex = [{name:'1'},{name:'2'},{name:'3'}]
        const index = ex.indexOf(p => p.name === '2')
        return index
    })
    function onStartDate(newValue){
        if(moment(newValue).isSame(stay.value.end_date) || moment(newValue).isAfter(stay.value.end_date)){
            stay.value.end_date = moment(stay.value.end_date).add(1,'days').toDate()
        }
        stay.value.room_nights = moment(stay.value.end_date).diff(moment(newValue), 'days') 
    }
    function onNight(newValue){
        stay.value.end_date = new Date(moment(stay.value.start_date).add(newValue,'days').toDate())
    }
    function onEndDate(newValue){
        stay.value.room_nights = moment(newValue).diff(moment(stay.value.start_date), 'days')
    }
    const onClose = () =>{
        dialogRef.value.close();
    }
    function onSave(){
        loading.value = true
        var newData = JSON.parse(JSON.stringify(stay.value))
        newData.start_date = gv.dateApiFormat(newData.start_date)
        newData.end_date = gv.dateApiFormat(newData.end_date)

        postApi('reservation.change_stay', {data: newData}).then((r)=>{
            loading.value = false 
            rs.getReservationDetail(rs.reservationStay.name)
            onClose(true)
        }).catch(()=>{
            loading.value= false
        })
    }
    onMounted(() => {
        getApi("frontdesk.get_working_day", {
            property: property.name
        }).then((result) => {
            working_day.value = (result.message)
        })
});
</script>
<style lang="">
    
</style>