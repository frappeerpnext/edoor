<template>
    <ComDialogContent>
    <div>
        <ComReservationStayPanel class="mb-4" title="Last Stay Room">
            <template #content>
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
                                <label class="px-2">Room</label>
                            </th>
                            <th class="text-right">
                                <label class="px-2">Rate<span class="text-red-500">*</span></label>
                            </th> 
                            <th>
                                <label class="text-center px-2">Total Nights</label>
                            </th>
                            <th class="text-right">
                                <label class="px-2">Amount</label>
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
                            <td class="pr-2">
                                {{ lastStay.room_type_alias }} / {{ lastStay.room_number}}
                            </td>
                            <td class="p-2 w-12rem text-right">
                                <CurrencyFormat :value="lastStay.rate" />
                            </td> 
                            <td class="p-2 w-8rem">
                                <div class="p-inputtext-pt text-center border-1 border-white h-12">xx</div>
                            </td>
                            <td class="p-2 w-10rem">
                                <div class="p-inputtext-pt text-end border-1 border-white h-12">
                                    <CurrencyFormat :value="(rs.reservation.room_night ?? 0) * (lastStay.rate ?? 0)" />
                                </div>
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
                                <label class="px-2">Room Name<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-right">
                                <label class="px-2">Rate<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-right">
                                <label class="px-2">Amount</label>
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
                                <InputNumber v-model="newRoom.night" @update:modelValue="onNight" inputId="stacked-buttons" showButtons :min="1" class="child-adults-txt" />
                            </td>
                            <td>
                                <!-- <Dropdown v-model="newRoom.room_type_id" :options="room_types" optionValue="name" @change="onSelectRoomType()" optionLabel="room_type" placeholder="Select Room Type" class="w-full" /> -->
                                {{newRoom.room_type_id}}
                                <ComSelectRoomTypeAvailability v-model="newRoom.room_type_id" @onSelected="onSelectRoomType" :start-date="newRoom.start_date" :end-date="newRoom.end_date"/>
                            </td>
                            <td>
                                <Dropdown v-model="newRoom.room_id" :options="rooms.filter((r) => (r.room_type_id == newRoom.room_type_id && r.room_number != lastStay.room_number))"
                                    optionValue="name" @change="OnSelectRoom" optionLabel="room_number"
                                    placeholder="Select Room" showClear filter class="w-full" />
                            </td>
                            <td class="p-2 w-12rem text-right">
                                <span @click="onOpenChangeRate($event)" class="text-right w-full color-purple-edoor text-md font-italic ">
                                    <span class="link_line_action"><CurrencyFormat :value="newRoom.rate" /></span>
                                </span>
                            </td>
                            <td class="p-2 w-10rem">
                                <div class="p-inputtext-pt text-end border-1 border-white h-12">
                                    <CurrencyFormat :value="(rs.reservation.room_night ?? 0) * (newRoom.rate ?? 0)" />
                                </div>
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
    import {inject,ref, getApi, onMounted, useDialog, computed,watch} from '@/plugin'
    import ComReservationStayPanel from './ComReservationStayPanel.vue';
    import ComReservationStayChangeRate from './ComReservationStayChangeRate.vue'
    const property = JSON.parse(localStorage.getItem("edoor_property"))
    const rs = inject('$reservation_stay')
    const moment = inject('$moment')
    const gv = inject('$gv') 
    const lastStay = ref(rs.reservationStay.stays[rs.reservationStay.stays.length - 1])
    const lastStayMaxEndDate = new Date(lastStay.value.end_date)
    const room_types = ref([])
    const rooms = ref([])
    const working_day = ref({})
    const op = ref()
    const selectedStay = ref({})
    const rate = ref(0)
    const newRoom = ref({})
    const doc = ref({
        reservation: {
            doctype: "Reservation",
            property: property.name,
            reservation_type: "FIT",
            arrival_time: '12:00:00',
            departure_time: '12:00:00',
            adult: 1,
            child: 0,
            reservation_status: 'Reserved'
        },
        guest_info: {
            "doctype": "Customer",
            "gender": "Not Set"
        },
        reservation_stay: [{ rate: 0, adult: 1, child: 0, is_manual_rate: false },]
    })

    watch(lastStay.value,(newValue)=>{
        onUpdateDateNewRoom(newValue)
    })
 
    function onUpdateDateNewRoom(newValue){
        newRoom.value.start_date = new Date(moment(newValue.end_date).add(1,'days'))
        newRoom.value.end_date = new Date(moment(newValue.end_date).add(2,'days'))
        
        newRoom.value.night = moment(newRoom.value.end_date).diff(moment(newRoom.value.start_date), 'days')
    }
    function onNight(newValue){
        newRoom.value.end_date = new Date(moment(newRoom.value.start_date).add(newValue,'days'))
    }
    function onEndDate(newValue){
        newRoom.value.night = moment(newValue).diff(moment(newRoom.value.start_date), 'days')
    }

    const onUseRatePlan = () => {
        newRoom.value.is_manual_rate = false;
        updateRate()
        op.value.hide();
    }
    const onClose = () =>{
        op.value.hide()
    }
    const onChangeRate = () => {
        newRoom.value.rate = rate.value
        newRoom.value.is_manual_rate = true
        op.value.hide();
    }
    const onDateSelect = (date) => {
        getRoomType()
        getRooms()
    }

    const onOpenChangeRate = (event) => {
        console.log(newRoom.value)
        rate.value = JSON.parse(JSON.stringify(newRoom.value)).rate
        op.value.toggle(event);
    }
 
    const getRoomType = () => {

    getApi("reservation.check_room_type_availability", {
        property: property.name,
        start_date: moment(doc.value.reservation.reservation_date).format("yyyy-MM-DD"),
        end_date: moment(doc.value.reservation.departure_date).format("yyyy-MM-DD"),
        rate_type: doc.value.reservation.rate_type,
        business_source: doc.value.reservation.business_source
    })
        .then((result) => {
            room_types.value = result.message;
            console.log(result.message)
            updateRate()
        }).catch((error) => {
            gv.showErrorMessage(error)
        })
    }

    const getRooms = () => { 
        getApi("reservation.check_room_availability", {
            property: property.name,
            start_date: moment(doc.value.reservation.arrival_date).format("yyyy-MM-DD"),
            end_date: moment(doc.value.reservation.departure_date).format("yyyy-MM-DD")
        })
        .then((result) => { 
            rooms.value = result.message; 
        })
    }
    const onSelectRoomType = (r) => {
        newRoom.value.rate = r.rate
        rate.value = r.rate
    }
    const updateRate = (r) => {
        console.log(r)
        // const room_type = room_types.value.find(r => r.name == newRoom.value.room_type_id)
        // if (room_type) {
        //     newRoom.value.rate = room_type.rate
        //     rate.value = room_type.rate
        // }
    }
    onMounted(() => {
        getApi("frontdesk.get_working_day", {
            property: property.name
        }).then((result) => {
            working_day.value = (result.message)
            doc.value.reservation.reservation_date = moment(working_day.value.date_working_day).toDate()
            //getRoomType()
            getRooms()
            doc.value.reservation.room_night = moment(doc.value.reservation.departure_date).diff(moment(doc.value.reservation.arrival_date), 'days')

            onUpdateDateNewRoom(lastStay.value)

        })
});
</script>
<style lang="">
    
</style>