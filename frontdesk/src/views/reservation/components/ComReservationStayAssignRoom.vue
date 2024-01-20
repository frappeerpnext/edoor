<template>
    <ComDialogContent @onClose="onClose" @onOK="onSave" :loading="loading">
    <div class="">

        <ComReservationStayPanel title="Assign Room">
            <template #content> 
 
            <div class="n__re-custom">
                <table class="w-full">
                    <thead>
                        <tr>
                            <th class="text-left pe-2 w-12rem">
                                <label>Stay Date</label>
                            </th>

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
                                    <span  v-tippy="'Arrival Date'">{{gv.dateFormat(moment(selectedStay.start_date))}}</span>
                                    &#8594;
                                    <span  v-tippy="'Departure Date'">{{gv.dateFormat(moment(selectedStay.end_date))}}</span>
                                </div>
                            </td>
                            <td class="text-right px-2 w-10rem"> 
                                <span class="p-inputtext-pt border-1 border-white h-12 w-full flex white-space-nowrap">{{ selectedStay.rate_type }}</span>
                            </td>
                            <td class="px-2 select-room-type-style">  
                            <Dropdown v-model="selectedStay.room_type_id" :options="room_types" optionValue="name"
                                @change="onSelectRoomType" optionLabel="room_type" placeholder="Select Room Type"
                                class="w-full"  >

                                <template #option="slotProps">
                                    <div class="flex align-items-center">
                                 <div>{{ slotProps.option.room_type }} ({{ slotProps.option.total_vacant_room }})</div>
                                  </div>
                                </template>
                            </Dropdown>
                                
                                
                            </td>
                            <td class="px-2 select-room-number-style">
                                <Dropdown v-model="selectedStay.room_id"
                                    :options="rooms.filter(r=>r.room_type_id==selectedStay.room_type_id)"
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
                <Message v-if="selectedStay.room_type_id != selectedStay.old_room_type_id">
                    <Checkbox v-model="selectedStay.is_override_rate"  @input="onUpdateRate"  :binary="true"  />
                    <label class="mr-3 cursor-pointer"  >Room type of this reservation stay is changed. Do you want to update rate?</label>
                </Message>
            </div>
            </template>
        </ComReservationStayPanel>
        <div class="flex gap-3 justify-content-end mt-3">
        <Button type="button" class="border-none" label="View Room Inventory" @click="onViewRoomInventory"  />
        <Button type="button" class="border-none" label="View Room Available" @click="onViewRoomAvailable"  />
    </div>
        

    </div>
</ComDialogContent>
</template>
<script setup>
    import {inject,ref, getApi, onMounted,postApi,getDoc,useDialog} from '@/plugin'
    import ComReservationStayPanel from './ComReservationStayPanel.vue';
    import ComRoomInventory from  "@/components/ComRoomInventory.vue"
    import ComRoomAvailable from  "@/components/ComRoomAvailable.vue"


    const property = JSON.parse(localStorage.getItem("edoor_property"))

    const rs = inject('$reservation_stay')
    const moment = inject('$moment')
    const gv = inject('$gv')
    const dialogRef = inject('dialogRef'); 
    const working_day = ref({})
    const loading = ref(false)
    const selectedStay = ref({})
    const rooms = ref([])
    const room_types = ref([])
    const dialog = useDialog();
 
    const onClose = (r) =>{ 
        dialogRef.value.close(r);
    }

    function onUpdateRate(v){
      if(v){
    
        if (selectedStay.value.room_type_id!=selectedStay.value.old_room_type_id) {
            const rt = room_types.value.find(r=>r.name ==selectedStay.value.room_type_id)

            selectedStay.value.rate = rt.rate.rate


        }
      }else {
        selectedStay.value.rate = selectedStay.value.old_rate
      }
    }
 
    const getRoomType = () => {
        getApi("reservation.check_room_type_availability", {
            property: property.name,
            start_date: moment(selectedStay.value.start_date).format("yyyy-MM-DD"),
            end_date: moment(selectedStay.value.end_date).format("yyyy-MM-DD"),
            rate_type: selectedStay.value.rate_type,
            business_source: selectedStay.value.business_source
        })
            .then((result) => {
                
                room_types.value = result.message;
             
              
            })
        }


    const onSelectRoomType = (room_type) => {

        const rt = room_types.value.find(r=>r.name == room_type.value)
 
        selectedStay.value.room_id = null
        selectedStay.value.room_type = rt.room_type

        if(selectedStay.value.is_override_rate){
            if (selectedStay.value.room_type_id!=selectedStay.value.old_room_type_id) {
                const rt = room_types.value.find(r=>r.name ==selectedStay.value.room_type_id)
                
                
                selectedStay.value.rate = rt.rate .rate

            }else {
                selectedStay.value.rate = selectedStay.value.old_rate
            }
        }else {
            selectedStay.value.rate = selectedStay.value.old_rate
        } 



    }
    
    function onSave(){ 
        if(!selectedStay.value.room_id){
            gv.toast('warn','Please select  room number.')
            return
        }
        loading.value = true
 
         postApi("reservation.assign_room",{data: selectedStay.value})
        .then((r)=>{
            loading.value = false
            window.socket.emit("ComIframeModal", window.property_name)
            window.postMessage({"action":"Dashboard"},"*")
            window.socket.emit("ReservationList", { property:window.property_name})
            window.socket.emit("ReservationStayList", { property:window.property_name})
            window.socket.emit("ReservationStayDetail", { reservation_stay:window.reservation_stay})
            window.socket.emit("ReservationDetail", rs.reservationStay.reservation)
            window.postMessage("Frontdesk",{"action":"Frontdesk"},"*")
            window.socket.emit("TodaySummary", window.property_name)
            window.socket.emit("ComGuestLedger", { property:window.property_name})
            window.socket.emit("GuestLedgerTransaction", { property:window.property_name})
            window.socket.emit("Reports", window.property_name)
            onClose(r)
        }).catch((err)=>{
            loading.value = false
        })
    }

    function getRoom(){
  
        getApi("reservation.check_room_availability", {
                property: property.name,
                start_date: selectedStay.value.start_date, 
                end_date:  selectedStay.value.end_date
            })
                .then((result) => {
                    
                    rooms.value = result.message;
                    
                })
    }
    
    function onViewRoomInventory(){
        const dialogRef = dialog.open(ComRoomInventory, {
        props: {
            header: 'Room Inventory',
            style: {
                width: '80vw',
            },
            modal: true,
            maximizable: true,
            closeOnEscape: true,
            position: "top"
        },
    });
    }
    function onViewRoomAvailable(){
        const dialogRef = dialog.open(ComRoomAvailable, {
        props: {
            header: 'Room Available',
            style: {
                width: '80vw',
            },
            modal: true,
            maximizable: true,
            closeOnEscape: true,
            position: "top"
        },
    });
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
                        selectedStay.value.old_room_type_id = selected.room_type_id
                        selectedStay.value.room_type = selected.room_type
                        selectedStay.value.room_id = selected.room_id
                        selectedStay.value.start_date = selected.arrival_date
                        selectedStay.value.end_date = selected.departure_date
                        selectedStay.value.room_nights = selected.room_nights
                        selectedStay.value.rate = selected.input_rate
                        selectedStay.value.old_rate = selected.input_rate
                        selectedStay.value.rate_type = r.rate_type
                        selectedStay.value.business_source= r.business_source
                        selectedStay.value.stay_room = selected.name
                        selectedStay.value.is_manual_rate = selected.is_manual_rate
                        selectedStay.value.reservation_stay = selected.parent
                         
                        getRoomType()
                        getRoom() 
                    }
                })
            }else{ 
                
                const selected = dialogRef.value.options.data.stay_room
       
                selectedStay.value.room_type_id = selected.room_type_id
                selectedStay.value.old_room_type_id = selected.room_type_id
                selectedStay.value.room_type = selected.room_type
                selectedStay.value.room_id = selected.room_id
                selectedStay.value.start_date = selected.arrival_date
                selectedStay.value.end_date = selected.departure_date
                selectedStay.value.room_nights = selected.room_nights
 
                selectedStay.value.rate = selected.input_rate
                selectedStay.value.old_rate = selected.input_rate
                selectedStay.value.rate_type = selected.rate_type
                selectedStay.value.business_source = selected.business_source
                selectedStay.value.stay_room = selected.name
                selectedStay.value.is_manual_rate = selected.is_manual_rate
                selectedStay.value.reservation_stay = selected.parent
                getRoomType()
                getRoom() 
            }

            
          
        })
        
                
    });
</script>
<style scoped>
    .box-input{
        padding: .6rem .65rem;
    }
</style>