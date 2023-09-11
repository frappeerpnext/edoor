<template>
    <ComDialogContent @onClose="onClose" @onOK="onSave" :loading="loading">
    <div class="">
        {{ selectedStay }}
        <ComReservationStayPanel title="Assign Room">
            <template #content> 
            <div class="n__re-custom">
                <table class="w-full">
                    <thead>
                        <tr>
                            <th class="text-left pe-2 w-12rem">
                                <label>Stay Date</label>
                            </th>
                            <!-- <th class="text-left px-2 w-14rem">
                                <label>End Date</label>
                            </th> --> 
                            <th class="text-left px-2">
                                <label>Rate Type</label>
                            </th>
                            <th class="text-left px-2">
                                <label>Room Type</label>
                            </th>
                            <th class="text-left px-2">
                                <label>Room Name</label>
                            </th>
                            <th class="text-center px-2 w-5rem">
                                <label class="text-center">Nights</label>
                            </th>
                           
                            <th class="text-right px-2">
                                <label>Rate</label>
                            </th>

                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="pe-2">
                                <div class="p-inputtext-pt border-1 border-white h-12 w-full white-space-nowrap">
                                    <span v-tooltip.top="'Arrival Date'">{{gv.dateFormat(moment(selectedStay.start_date))}}</span>
                                    &#8594;
                                    <span v-tooltip.top="'Departure Date'">{{gv.dateFormat(moment(selectedStay.end_date))}}</span>
                                </div>
                            </td>
                            <td class="text-right px-2 w-10rem"> 
                                <span class="p-inputtext-pt border-1 border-white h-12 w-full flex white-space-nowrap">{{ selectedStay.rate_type }}</span>
                            </td>
                            <td class="px-2 select-room-type-style">  
                                <ComSelectRoomTypeAvailability 
                                    v-model="selectedStay.room_type_id"
                                    @onSelected="onSelectRoomType"
                                    :rate-type="selectedStay.rate_type"
                                    :businessSource="selectedStay.business_source"
                                    :start-date="selectedStay.start_date"
                                    :end-date="selectedStay.end_date"/>
                            </td>
                            <td class="px-2 select-room-number-style">
                                <Dropdown v-model="d.room_id"
                                    :options="rooms"
                                    optionValue="name"   optionLabel="room_number"
                                    placeholder="Select Room" showClear filter class="w-full" />
                            </td>
                            <td class="text-center px-2 w-10rem"> 
                                <span class="p-inputtext-pt border-1 border-white h-12 w-full flex white-space-nowrap text-center justify-center">{{ selectedStay.room_nights }}</span>
                            </td>
                            <td class="px-2 w-15rem">
                                <span class="p-inputtext-pt border-1 border-white h-12 w-full flex white-space-nowrap justify-end">
                                    <CurrencyFormat :value="selectedStay.rate" />
                                </span>
                             
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
    import {inject,ref, getApi, onMounted,postApi,getDoc} from '@/plugin'
    import ComReservationStayPanel from './ComReservationStayPanel.vue';
    // import ComReservationStayChangeRate from './ComReservationStayChangeRate.vue'
    const property = JSON.parse(localStorage.getItem("edoor_property"))
    const rs = inject('$reservation_stay')
    const socket = inject('$socket')
    const moment = inject('$moment')
    const gv = inject('$gv')
    const dialogRef = inject('dialogRef'); 
    const working_day = ref({})
    const op = ref()
    const loading = ref(false)
    const isOverrideRate = ref(false)
    const selectedStay = ref({})
    const rooms = ref([])
    const rate = ref(0)
 
    const onClose = (r) =>{ 
        dialogRef.value.close(r);
    }
 

    const onSelectRoomType = (r) => {
        selectedStay.value.rate = r.rate
        rate.value = r.rate
    }
    function onSave(){ 
        if(!selectedStay.value.room_type_id){
            gv.toast('warn','Please select room type.')
            return
        }
        loading.value = true
        const dataSave = {
            reservation_stay: dialogRef.value.options.data.reservation_stay_name ? dialogRef.value.options.data.reservation_stay_name : rs.reservationStay.name, 
            room_stay: selectedStay.value.name,
            room_type_id: selectedStay.value.room_type_id,
            room_id: selectedStay.value.room_id,
            is_manual_rate: selectedStay.value.is_manual_rate,
            is_override_rate: isOverrideRate.value,
            rate: selectedStay.value.rate,
            stay_room: selectedStay.value.stay_room
        }
        postApi("reservation.assign_room",{data: dataSave}).then((r)=>{
            loading.value = false
            socket.emit("RefreshReservationDetail", r.message.reservation);
            onClose(r)
        }).catch(()=>{
            loading.value = false
        })
    }

    function getRoom(){
        getApi("reservation.check_room_availability", {
                property: property.name,
                room_type_id:selectedStay.value.room_type_id,
                start_date: selectedStay.value.start_date, 
                end_date:  selectedStay.value.end_date
            })
                .then((result) => {
                    rooms.value = result.message;
                    
                })
    }
    onMounted(() => {
        getApi("frontdesk.get_working_day", {
            property: property.name
        }).then((result) => {
            working_day.value = (result.message)
            if(dialogRef.value.options.data.reservation_stay_name){
                getDoc("Reservation Stay", dialogRef.value.options.data.reservation_stay_name).then((r)=>{
                    if(r){
                        const selected = r.stays.find((r)=> r.name == dialogRef.value.options.data.stay_room)
                        selectedStay.value.room_type_id = selected.room_type_id
                        selectedStay.value.room_id = selected.room_id
                        selectedStay.value.start_date = selected.start_date
                        selectedStay.value.end_date = selected.end_date
                        selectedStay.value.room_nights = selected.room_nights
                        selectedStay.value.rate = selected.rate
                        selectedStay.value.rate_type = r.business_source
                        selectedStay.value.stay_room = selected.name
                        selectedStay.value.is_manual_rate = selected.is_manual_rate
                    }
                })
            }else{ 
                const selected = dialogRef.value.options.data.stay_room
                selectedStay.value.room_type_id = selected.room_type_id
                selectedStay.value.room_id = selected.room_id
                selectedStay.value.start_date = selected.start_date
                selectedStay.value.end_date = selected.end_date
                selectedStay.value.room_nights = selected.room_nights
                selectedStay.value.rate = selected.rate
                selectedStay.value.rate_type = selected.rate_type
                selectedStay.value.business_source = selected.business_source
                selectedStay.value.stay_room = selected.name
                selectedStay.value.is_manual_rate = selected.is_manual_rate
            }

            
            getRoom() 
        })
        
                
    });
</script>
<style scoped>
    .box-input{
        padding: .6rem .65rem;
    }
</style>