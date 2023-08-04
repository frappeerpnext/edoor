<template>
    <ComDialogContent @onClose="onClose" @onOK="onSave" :loading="loading">
    <div class="">
        <ComReservationStayPanel class="mb-4" :title="'Last Stay in' + ' ' + lastStay?.room_type">
            <template #content>
            <div class="n__re-custom">
                <table class="w-full">
                    <thead>
                        <tr>
                            <th class="text-left pe-2 w-14rem">
                                <label>Start Date</label>
                            </th>
                            <th class="text-left px-2">
                                <label>End Date</label>
                            </th> 
                            <th class="text-left px-2">
                                <label>Room</label>
                            </th>
                            <th class="text-right px-2">
                                <label>Rate</label>
                            </th> 
                            <th class="px-2 w-8rem text-center">
                                <label>Nights</label>
                            </th>
                            <th class="text-right ps-2">
                                <label>Amount</label>
                            </th>

                        </tr>
                    </thead>
                    <tbody>
                        <tr v-if="lastStay">
                            <td class="pe-2 flex"> 
                                <span class="box-input-detail">{{gv.dateFormat(lastStay.start_date)}}</span>
                            </td>
                            <td class="px-2 w-14rem"> 
                                <Calendar class="w-14rem" showIcon v-model="lastStay.end_date" :min-date="new Date(moment(lastStay.start_date).add(1,'days'))" :max-date="lastStayMaxEndDate" dateFormat="dd-mm-yy"/>
                            </td>
                            <td class="px-2 text-left">
                                <div class="box-input-detail flex"><span v-tooltip.top="lastStay?.room_type ? lastStay.room_type : ''">{{ lastStay?.room_type_alias }}</span>/<span v-tooltip.top="lastStay?.room_number ? lastStay.room_number : ''">{{ lastStay?.room_number ? lastStay.room_number : 'Room No (Unassign)' }}</span></div>
                            </td>
                            <td class="text-right px-2">
                                <span class="box-input-detail flex justify-end white-space-nowrap">
                                    <CurrencyFormat :value="lastStay.rate" />
                                </span>
                            </td> 
                            <td class="text-right px-2"> 
                                <span class="box-input-detail flex justify-center">{{moment(lastStay.end_date).diff(moment(lastStay.start_date), 'days')}}</span>
                            </td>
                            <td class="text-right ps-2">
                                <span class="box-input-detail flex justify-end white-space-nowrap">
                                    <CurrencyFormat :value="Number(moment(lastStay.end_date).diff(moment(lastStay.start_date), 'days') || 0) * lastStay.rate" />
                                </span>
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
                            <th class="text-left pe-2 w-12rem">
                                <label>Start Date<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-left px-2 w-14rem">
                                <label>End Date<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-left px-2">
                                <label>Room Type<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-left px-2">
                                <label>Room Name</label>
                            </th>
                            <th class="text-center px-2 w-5rem">
                                <label class="text-center">Nights</label>
                            </th>
                            <th class="text-right px-2">
                                <label>Rate<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-right ps-2">
                                <label>Amount</label>
                            </th>

                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="pe-2 w-12rem"> 
                                <span class="p-inputtext-pt border-1 border-white h-12 w-full flex white-space-nowrap">{{gv.dateFormat(moment(lastStay.end_date))}}</span>
                            </td>
                            <td class="px-2 w-14rem">
                                <Calendar showIcon v-model="newRoom.end_date"  :min-date="new Date(moment(newRoom.start_date).add(1,'days'))" @update:modelValue="onEndDate" dateFormat="dd-mm-yy" class="w-full"/>
                            </td>
                            <td class="px-2 w-16rem"> 
                                <ComSelectRoomTypeAvailability v-model="newRoom.room_type_id" @onSelected="onSelectRoomType" :businessSource="rs.reservationStay.business_source" :rate-type="rs.reservationStay.rate_type" :start-date="newRoom.start_date" :end-date="newRoom.end_date"/>
                            </td>
                            <td class="px-2 w-8rem">
                                <ComSelectRoomAvailability showClear v-model="newRoom.room_id" :except="lastStay.room_id" :start-date="newRoom.start_date" :end-date="newRoom.end_date" :roomType="newRoom.room_type_id" />
                            </td>
                            <td class="text-center px-2 w-5rem ">
                                
                                    <InputNumber v-model="newRoom.room_nights" @update:modelValue="onNight" inputId="stacked-buttons" showButtons :min="1" class="w-full nig_in-put"/>
                                
                            </td>
                            <td class="text-right px-2 w-10rem">
                                <div class="box-input-detail">
                                <span class="white-space-nowrap">
                                    <span @click="onOpenChangeRate($event)" class="text-right w-full color-purple-edoor text-md font-italic ">
                                        <span class="link_line_action flex justify-between">
                                            <div>
                                                <span class="text-sm" v-if="newRoom?.is_manual_rate"> (Manual) </span>
                                                   <span class="text-sm" v-else>(Plan)</span>
                                            </div>
                                            <CurrencyFormat :value="newRoom.rate" />
                                        </span>
                                    </span>
                                </span>
                                </div> 
                            </td>
                            <td class="text-right ps-2 w-10rem">
                                <span class="p-inputtext-pt border-1 border-white h-12 w-full flex justify-end">
                                    <CurrencyFormat :value="(newRoom.room_nights   ?? 0) * (newRoom.rate ?? 0)" />
                                </span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            </template>
        </ComReservationStayPanel>
        <OverlayPanel ref="op">
            <ComReservationStayChangeRate v-model="rate" @onClose="onCloseRate" @onUseRatePlan="onUseRatePlan" @onChangeRate="onChangeRate"/>
        </OverlayPanel>

    </div>
</ComDialogContent>
</template>
<script setup>
    import {inject,ref, getApi, onMounted,postApi,watch} from '@/plugin'
    import ComReservationStayPanel from './ComReservationStayPanel.vue';
    import ComReservationStayChangeRate from './ComReservationStayChangeRate.vue'
    import ComSelectRoomAvailability from './form/ComSelectRoomAvailability.vue'
    import Enumerable from 'linq'
    const property = JSON.parse(localStorage.getItem("edoor_property"))
    const rs = inject('$reservation_stay')
    const moment = inject('$moment')
    const gv = inject('$gv')
    const socket = inject('$socket')
    const dialogRef = inject('dialogRef'); 
    const lastStay = ref(JSON.parse(JSON.stringify(Enumerable.from(rs.reservationStay.stays).orderByDescending("$.end_date").toArray()[0])))
    lastStay.value.end_date = new Date(lastStay.value.end_date)
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
        newRoom.value.start_date = moment(newValue.end_date).toDate() 
        if(!newRoom.value.end_date || moment(newRoom.value.start_date).isSame(newRoom.value.end_date) || moment(newRoom.value.start_date).isAfter(newRoom.value.end_date)){
            newRoom.value.end_date = moment(newRoom.value.start_date).add(1,'days').toDate()
        }
        newRoom.value.room_nights = moment(newRoom.value.end_date).diff(moment(newRoom.value.start_date), 'days')
    }
    function onNight(newValue){
        newRoom.value.end_date = moment(newRoom.value.start_date).add(newValue,'days').toDate()
    }
    function onEndDate(newValue){
        newRoom.value.room_nights = moment(newValue).diff(moment(newRoom.value.start_date), 'days')
    }

    const onUseRatePlan = () => {
        newRoom.value.is_manual_rate = false;
        newRoom.value.rate = newRoom.value.original_rate
        op.value.hide();
    }
    const onClose = () =>{
        dialogRef.value.close();
    }
    function onCloseRate(){
        op.value.hide()
    }
    const onChangeRate = () => {
        newRoom.value.rate = rate.value
        newRoom.value.is_manual_rate = true
        op.value.hide();
    }

    const onOpenChangeRate = (event) => {
        rate.value = JSON.parse(JSON.stringify(newRoom.value)).rate
        op.value.toggle(event);
    }

    const onSelectRoomType = (r) => {
        if (!newRoom.value.is_manual_rate)
            newRoom.value.rate = r.rate
        newRoom.value.original_rate = r.rate
        rate.value = r.rate
    }
    function onSave(){
        loading.value = true
        if(!newRoom.value.room_type_id){
            window.postMessage('show_alert|' + 'Please select room type', '*')
            loading.value = false
            return
        }
 
        const data = JSON.parse(JSON.stringify(rs))
        var newData = JSON.parse(JSON.stringify(newRoom.value))
        newData.start_date = gv.dateApiFormat(newData.start_date)
        newData.end_date = gv.dateApiFormat(newData.end_date)
        newData.input_rate = newData.rate
        newData.total_amount = (newData.room_nights || 0) * (newData.rate || 0)
        data.reservationStay.stays = data.reservationStay.stays.map(i=>{
            if(i.name === lastStay.value.name){
                return  {...i, end_date: gv.dateApiFormat(lastStay.value.end_date)}
            }
            return i
        })
        data.reservationStay.stays.push(newData)
        
        postApi('reservation.upgrade_room',{doc: data.reservationStay}).then((doc) => { 
            loading.value = false;
            socket.emit("RefreshReservationDetail", doc.reservation);
            rs.getReservationDetail(data.reservationStay.name)
            onClose()
        }).catch((ex) => {
            loading.value = false;
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
<style scoped>
    .box-input{
        padding: .6rem .65rem;
    }
</style>