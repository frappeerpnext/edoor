<template>
    <ComDialogContent @onClose="onClose" @onOK="onSave" :loading="loading">
    <div>
        <ComReservationStayPanel title="Change Stay">
            <template #content> 
            <div class="n__re-custom">
                <table class="w-full">
                    <thead>
                        <tr>
                            <th class="text-left pe-2">
                                <label>Start Date<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-left px-2">
                                <label>End Date<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-center px-2">
                                <label class="text-center">Nights</label>
                            </th>
                            <th class="text-left px-2">
                                <label>Room Type<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-left ps-2">
                                <label>Room Name<span class="text-red-500">*</span></label>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="pe-2"> 
                                <Calendar class="w-full" showIcon v-model="stay.start_date" :disabled="rs.reservationStay.reservation_status == 'In-house'" :min-date="new Date(working_day.date_working_day)" @update:modelValue="onStartDate" dateFormat="dd-mm-yy"/>
                            </td>
                            <td class="px-2">
                                <Calendar class="w-full" showIcon v-model="stay.end_date" :min-date="minDate" :max-date="maxDate" @update:modelValue="onEndDate" dateFormat="dd-mm-yy"/>
                            </td>
                            <td class="text-center px-2 w-5rem">
                                <InputNumber v-model="stay.room_nights" @update:modelValue="onNight" inputId="stacked-buttons" showButtons :max="maxNight" :min="1" class="child-adults-txt w-full" />
                            </td>
                            <td class="px-2"> 
                                <span class="p-inputtext-pt text-start border-1 border-white h-12 w-full flex white-space-nowrap">{{ stay.room_type }}</span>
                            </td>
                            <td class="ps-2">
                                <span class="p-inputtext-pt text-start border-1 border-white h-12 w-full flex">{{ stay.room_number }}</span>
                            </td> 
                        </tr>
                    </tbody>
                    <tbody>
                        <tr>
                            <td colspan="5">
                                <div class="text-right pt-2">
                                    <div>
                                        <Checkbox class="mr-1" v-model="stay.is_override_rate" :binary="true" inputId="disabled" />
                                        <label for="disabled"> Override Room Rate</label>
                                    </div>
                                </div>
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
    const socket = inject('$socket')
    const dialogRef = inject('dialogRef'); 
    const loading = ref(false) 
    const maxNight = ref(null) 
    const stay = ref(JSON.parse(JSON.stringify(dialogRef.value.data.item)))
    stay.value.start_date = moment(stay.value.start_date).toDate()
    stay.value.end_date = moment(stay.value.end_date).toDate()
    const minDate = computed(()=>{
        if(moment(stay.value.start_date).isSame(working_day.date_working_day) || moment(stay.value.start_date).isBefore(working_day.date_working_day)){
            return new Date(moment(working_day.date_working_day).add(1,'days'))
        }else{
            return new Date(moment(stay.value.start_date).add(1,'days'))
        }
    })
    const maxDate = computed(()=>{
        const data = Enumerable.from(rs.reservationStay.stays).orderBy("$.start_date").toArray()
        const index = data.findIndex(p => p.name == stay.value.name)
        if(data[index + 1]){ 
            maxNight.value = moment(data[index + 1].end_date).diff(moment(stay.value.start_date), 'days') - 1
            return moment(data[index + 1].end_date).subtract(1, "days").toDate()
        }
        return null
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
        if(moment(stay.value.start_date).isSame(stay.value.end_date)){
            gv.toast('warn','Start date cannot same end date.')
            loading.value = false
            return
        }
        var newData = JSON.parse(JSON.stringify(stay.value))
        newData.start_date = gv.dateApiFormat(newData.start_date)
        newData.end_date = gv.dateApiFormat(newData.end_date)

        postApi('reservation.change_stay', {data: newData}).then((r)=>{
            loading.value = false 
            rs.getReservationDetail(rs.reservationStay.name)
            socket.emit("RefreshReservationDetail", rs.reservationStay.reservation);
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