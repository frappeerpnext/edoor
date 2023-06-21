<template>
    <ComDialogContent @onClose="onClose" @onOK="onSave" :loading="loading">
    <div>
        <ComReservationStayPanel class="mb-4" title="Last Stay Room">
            <template #content>
                {{stays}}
            <div class="n__re-custom">
                <table class="w-full">
                    <thead>
                        <tr>
                            <th class="text-left">
                                <label>Start Date</label>
                            </th>
                            <th class="text-left">
                                <label>End Date</label>
                            </th> 
                            <th class="text-left">
                                <label>Room</label>
                            </th>
                            <th class="text-right">
                                <label>Rate<span class="text-red-500">*</span></label>
                            </th> 
                            <th>
                                <label class="text-center">Nights</label>
                            </th>
                            <th class="text-right">
                                <label>Amount</label>
                            </th>

                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td> 
                                {{gv.dateFormat(lastStay.start_date)}}
                            </td>
                            <td>
                                <Calendar v-model="lastStay.end_date" :min-date="new Date(moment(lastStay.start_date).add(1,'days'))" :max-date="lastStayMaxEndDate" dateFormat="dd-mm-yy"/>
                            </td>
                            <td>
                                {{ lastStay.room_type_alias }} / {{ lastStay.room_number}}
                            </td>
                            <td class="text-right">
                                <CurrencyFormat :value="lastStay.rate" />
                            </td> 
                            <td class="text-center"> 
                                {{moment(lastStay.end_date).diff(moment(lastStay.start_date), 'days')}}
                            </td>
                            <td class="text-right">
                                <CurrencyFormat :value="Number(moment(lastStay.end_date).diff(moment(lastStay.start_date), 'days') || 0) * lastStay.rate" />
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            </template>
        </ComReservationStayPanel>
        <ComReservationStayPanel title="New Stay Room">
            <template #content> 
            <div class="n__re-custom">
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
                            <th class="text-right">
                                <label>Rate<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-right">
                                <label>Amount</label>
                            </th>

                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td> 
                                {{gv.dateFormat(moment(lastStay.end_date).add(1,'days'))}}
                            </td>
                            <td> 
                                <Calendar v-model="newRoom.end_date"  :min-date="new Date(moment(newRoom.start_date).add(1,'days'))" @update:modelValue="onEndDate" dateFormat="dd-mm-yy"/>
                            </td>
                            <td class="text-center"> 
                                <InputNumber v-model="newRoom.room_nights" @update:modelValue="onNight" inputId="stacked-buttons" showButtons :min="1" class="child-adults-txt" />
                            </td>
                            <td> 
                                <ComSelectRoomTypeAvailability v-model="newRoom.room_type_id" @onSelected="onSelectRoomType" :start-date="newRoom.start_date" :end-date="newRoom.end_date"/>
                            </td>
                            <td>
                                <ComSelectRoomAvailability v-model="newRoom.room_id" :except="lastStay.room_id" :start-date="newRoom.start_date" :end-date="newRoom.end_date" :roomType="newRoom.room_type_id" />
                            </td>
                            <td class="p-2 w-12rem text-right">
                                <span @click="onOpenChangeRate($event)" class="text-right w-full color-purple-edoor text-md font-italic ">
                                    <span class="link_line_action"><CurrencyFormat :value="newRoom.rate" /></span>
                                </span>
                            </td>
                            <td class="text-right">
                                <CurrencyFormat :value="(newRoom.room_nights   ?? 0) * (newRoom.rate ?? 0)" />
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            </template>
        </ComReservationStayPanel>
        <OverlayPanel ref="op">
            <ComReservationStayChangeRate v-model="rate" @onClose="onClose" @onUseRatePlan="onUseRatePlan" @onChangeRate="onChangeRate"/>
        </OverlayPanel>

    </div>
</ComDialogContent>
</template>
<script setup>
    import {inject,ref, getApi, onMounted,updateDoc, useDialog, computed,watch} from '@/plugin'
    import ComReservationStayPanel from './ComReservationStayPanel.vue';
    import ComReservationStayChangeRate from './ComReservationStayChangeRate.vue'
    import ComSelectRoomAvailability from './form/ComSelectRoomAvailability.vue'
    import Enumerable from 'linq'
    const property = JSON.parse(localStorage.getItem("edoor_property"))
    const rs = inject('$reservation_stay')
    const moment = inject('$moment')
    const gv = inject('$gv')
    const dialogRef = inject('dialogRef'); 
    const lastStay = ref(JSON.parse(JSON.stringify(Enumerable.from(rs.reservationStay.stays).orderByDescending("$.end_date").toArray()[0])))
    const lastStayMaxEndDate = new Date(lastStay.value.end_date)
    const room_types = ref([])
    const rooms = ref([])
    const working_day = ref({})
    const op = ref()
    const loading = ref(false)
    const selectedStay = ref({})
    const rate = ref(0)
    const newRoom = ref({
        room_nights: 1,
        end_date: '',
        start_date:'',
        rate: 0,
        room_type_id: '',
        room_id:''
    })

    watch(lastStay.value,(newValue)=>{
        onUpdateDateNewRoom(newValue)
    })
 
    function onUpdateDateNewRoom(newValue){
        newRoom.value.start_date = new Date(moment(newValue.end_date).add(1,'days'))
        newRoom.value.end_date = new Date(moment(newValue.end_date).add(2,'days'))
        newRoom.value.room_nights = moment(newRoom.value.end_date).diff(moment(newRoom.value.start_date), 'days')
    }
    function onNight(newValue){
        newRoom.value.end_date = new Date(moment(newRoom.value.start_date).add(newValue,'days'))
    }
    function onEndDate(newValue){
        newRoom.value.room_nights = moment(newValue).diff(moment(newRoom.value.start_date), 'days')
    }

    const onUseRatePlan = () => {
        newRoom.value.is_manual_rate = false;
        op.value.hide();
    }
    const onClose = () =>{
        op.value.hide()
        dialogRef.value.close();
    }
    const onChangeRate = () => {
        newRoom.value.rate = rate.value
        newRoom.value.is_manual_rate = true
        op.value.hide();
    }

    const onOpenChangeRate = (event) => {
        console.log(newRoom.value)
        rate.value = JSON.parse(JSON.stringify(newRoom.value)).rate
        op.value.toggle(event);
    }

    const onSelectRoomType = (r) => {
        newRoom.value.rate = r.rate
        rate.value = r.rate
    }
    function onSave(){
        loading.value = true
        if(!newRoom.value.room_type_id){
            window.postMessage('show_alert|' + 'Please select room type', '*')
            loading.value = false
            return
        }
        else if(!newRoom.value.room_id){
            window.postMessage('show_alert|' + 'Please select room', '*')
            loading.value = false
            return
        }
 
        const data = JSON.parse(JSON.stringify(rs))
        var newData = JSON.parse(JSON.stringify(newRoom.value))
        newData.start_date = gv.dateApiFormat(newData.start_date)
        newData.end_date = gv.dateApiFormat(newData.end_date)
        newData.total_amount = (newData.room_nights || 0) * (newData.rate || 0)
        data.reservationStay.stays = data.reservationStay.stays.map(i=>{
            if(i.name === lastStay.value.name){
                return  {...i, end_date: gv.dateApiFormat(lastStay.value.end_date)}
            }
            return i
        })
        data.reservationStay.stays.push(newData)
        updateDoc('Reservation Stay', data.reservationStay.name,data.reservationStay).then((r)=>{
            loading.value = false
            rs.getReservationDetail(data.reservationStay.name)
            onClose()
        }).catch(()=>{
            loading.value= false
        })
    }
    onMounted(() => {
        getApi("frontdesk.get_working_day", {
            property: property.name
        }).then((result) => {
            working_day.value = (result.message) 
            onUpdateDateNewRoom(lastStay.value)
        })
});
</script>
<style lang="">
    
</style>