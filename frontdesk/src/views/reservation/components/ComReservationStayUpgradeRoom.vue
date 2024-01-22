<template>
    <ComDialogContent @onClose="onClose" @onOK="onSave" :loading="loading">
    <div class="wp-number-cus">
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
                            <th v-if="can_view_rate" class="text-right px-2">
                                <label>Rate</label>
                            </th> 
                            <th class="px-2 w-8rem text-center">
                                <label>Nights</label>
                            </th>
                            <th v-if="can_view_rate" class="text-right ps-2">
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
                                <Calendar showButtonBar panelClass="no-btn-clear" class="w-14rem" selectOtherMonths showIcon v-model="lastStay.end_date" :min-date="new Date(moment(lastStay.start_date).add(1,'days'))" :max-date="lastStayMaxEndDate" dateFormat="dd-mm-yy"/>
                            </td>
                            <td class="px-2 text-left">
                                <div class="box-input-detail flex"><span  v-tippy="lastStay?.room_type ? lastStay.room_type : ''">{{ lastStay?.room_type_alias }}</span>/<span  v-tippy="lastStay?.room_number ? lastStay.room_number : ''">{{ lastStay?.room_number ? lastStay.room_number : 'Room No (Unassign)' }}</span></div>
                            </td>
                            <td v-if="can_view_rate" class="text-right px-2">
                                <span class="box-input-detail flex justify-end white-space-nowrap">
                                    <CurrencyFormat :value="lastStay.rate" />
                                </span>
                            </td> 
                            <td class="text-right px-2"> 
                                <span class="box-input-detail flex justify-center">{{moment(lastStay.end_date).diff(moment(lastStay.start_date), 'days')}}</span>
                            </td>
                            <td v-if="can_view_rate" class="text-right ps-2">
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
                            <th v-if="can_view_rate" class="text-right px-2">
                                <label>Rate<span class="text-red-500">*</span></label>
                            </th>
                             
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="pe-2 w-12rem"> 
                                <span class="p-inputtext-pt border-1 border-white h-12 w-full flex white-space-nowrap">{{gv.dateFormat(moment(lastStay.end_date))}}</span>
                            </td>
                            <td class="px-2 w-14rem">
                                <Calendar showButtonBar panelClass="no-btn-clear" showIcon selectOtherMonths v-model="newRoom.end_date"     :min-date="new Date(moment(newRoom.start_date).add(1,'days'))" @update:modelValue="onEndDate" dateFormat="dd-mm-yy" class="w-full"/>
                            </td>

                            <td class="px-2 w-16rem"> 
                                
                                <Dropdown v-model="newRoom.room_type_id" :options="room_types" optionValue="name"
                                @change="onSelectRoomType" optionLabel="room_type" placeholder="Select Room Type"
                                class="w-full"  >

                                <template #option="slotProps">
                                    <div class="flex align-items-center">
                                 <div>{{ slotProps.option.room_type }} ({{ slotProps.option.total_vacant_room }})</div>
                                  </div>
                                </template>
                            </Dropdown>

                            </td>
                            
                            <td class="px-2 w-8rem">
                                <Dropdown v-model="newRoom.room_id"
                                    :options="rooms.filter(r=>r.room_type_id==newRoom.room_type_id)"
                                    optionValue="name"   optionLabel="room_number"
                                    placeholder="Select Room" showClear filter class="w-full" />

                              
                            </td>
                            <td class="text-center px-2 w-5rem ">
                                <InputNumber v-model="newRoom.room_nights" @update:modelValue="onNight" inputId="stacked-buttons" showButtons :min="1" class="w-full nig_in-put"/> 
                            </td>
                            <td v-if="can_view_rate" class="text-right px-2 w-10rem">
                                <CurrencyFormat :value="(newRoom.rate || 0)" />
                            </td>
                            
                        </tr>
                    </tbody>
                </table>

                <Message v-if="newRoom.room_type_id != newRoom.old_room_type_id">
                    <Checkbox v-model="newRoom.is_override_rate"  @input="onUpdateRate"  :binary="true"     inputId="generate_rate" />
                    <label for="generate_rate" class="mr-3 cursor-pointer"  >Room type of this reservation stay is changed. Do you want to update rate?</label>
                </Message>

            </div>
            </template>
        </ComReservationStayPanel>
        

    </div>
    
</ComDialogContent>
</template>
<script setup>
    import {inject,ref, getApi, onMounted,postApi,watch} from '@/plugin'
    import ComReservationStayPanel from './ComReservationStayPanel.vue';
 
    
    import Enumerable from 'linq'
    const rs = inject('$reservation_stay')
    const moment = inject('$moment')
    const gv = inject('$gv')
    const dialogRef = inject('dialogRef'); 
    const lastStay = ref(JSON.parse(JSON.stringify(Enumerable.from(rs.reservationStay.stays).orderByDescending("$.end_date").toArray()[0])))
    lastStay.value.end_date = new Date(lastStay.value.end_date)
    const lastStayMaxEndDate = new Date(lastStay.value.end_date)
    const working_day = ref({})
 
    const loading = ref(false)
 
    const room_types = ref([])
    const rooms = ref([])
    const can_view_rate = window.can_view_rate

    const newRoom = ref({
        room_nights: 1,
        end_date: '',
        start_date:'',
        rate: 0,
        room_type_id: lastStay.value?.room_type_id,
        room_id:''
    })

    watch(lastStay.value,(newValue)=>{
       
        onUpdateDateNewRoom(newValue)
        getRoomType()
        getRoom()
    })
 

    
    
    const getRoomType = () => {
        getApi("reservation.check_room_type_availability", {
            property: rs.reservationStay.property,
            start_date: moment(newRoom.value.start_date).format("yyyy-MM-DD"),
            end_date: moment(newRoom.value.end_date).format("yyyy-MM-DD"),
            rate_type: rs.reservationStay.rate_type,
            business_source: rs.reservationStay.business_source
        })
            .then((result) => {
                
                room_types.value = result.message;
             
              
            })
        }

        function getRoom(){
  
  getApi("reservation.check_room_availability", {
          property: window.property_name,
          start_date: newRoom.value.start_date, 
          end_date:  newRoom.value.end_date
      })
          .then((result) => {
              
              rooms.value = result.message;
              
          })
}

        function onUpdateRate(v){   
        if(v){
        
            if (newRoom.value.room_type_id!=newRoom.value.old_room_type_id) {
                const rt = room_types.value.find(r=>r.name ==newRoom.value.room_type_id)

                newRoom.value.rate = rt.rate.rate


            }
        }else {
            newRoom.value.rate = newRoom.value.old_rate
        }
        }
 

    function onUpdateDateNewRoom(newValue){
        newRoom.value.start_date = moment(newValue.end_date).toDate() 
        if(!newRoom.value.end_date || moment(newRoom.value.start_date).isSame(newRoom.value.end_date) || moment(newRoom.value.start_date).isAfter(newRoom.value.end_date)){
            newRoom.value.end_date = moment(newRoom.value.start_date).add(1,'days').toDate()
        }
        
        newRoom.value.room_nights = moment(newRoom.value.end_date).diff(moment(newRoom.value.start_date), 'days')
        newRoom.value.old_room_type_id = newValue.room_type_id
        newRoom.value.rate = newValue.input_rate
        newRoom.value.old_rate = newValue.input_rate
        newRoom.value.room_id = null
        newRoom.is_manual_rate = newValue.is_manual_rate
    }
    function onNight(newValue){
        newRoom.value.end_date = moment(newRoom.value.start_date).add(newValue,'days').toDate()
    }
    function onEndDate(newValue){
        newValue = moment.utc(moment(newValue).format("YYYY-MM-DD")).toDate()
        newRoom.value.end_date = newValue
        newRoom.value.room_nights = moment(newValue).diff(moment(newRoom.value.start_date),'days')
    }

    
    const onClose = () =>{
        dialogRef.value.close();
    }
 
 
  

    const onSelectRoomType = (room_type) => {

            const rt = room_types.value.find(r=>r.name == room_type.value)

            newRoom.value.room_id = null
            newRoom.value.room_type = rt.room_type

            if(newRoom.value.is_override_rate){
                if (newRoom.value.room_type_id!=newRoom.value.old_room_type_id) {
                    const rt = room_types.value.find(r=>r.name ==newRoom.value.room_type_id)
                    
                    
                    newRoom.value.rate = rt.rate .rate

                }else {
                    newRoom.value.rate = newRoom.value.old_rate
                }
            }else {
                newRoom.value.rate = newRoom.value.old_rate
            } 



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

        
        postApi('reservation.upgrade_room',{doc: data.reservationStay,regenerate_rate:newRoom.value.is_override_rate }).then((doc) => { 
            loading.value = false;
            window.postMessage({action:"ReservationList"},"*")
            window.postMessage({action:"ReservationStayList"},"*")
            window.postMessage({action:"ReservationStayDetail"},"*")
            window.postMessage({action:"ReservationDetail"},"*")
            window.postMessage({action:"GuestLedger"},"*")
            window.postMessage({action:"GuestLedgerTransaction"},"*")
            dialogRef.value.close(rs.reservationStay.name);
        }).catch((ex) => {
            loading.value = false;
        })

 
    }
    onMounted(() => {
        getApi("frontdesk.get_working_day", {
            property: window.property_name
        }).then((result) => {
            working_day.value = (result.message) 
            onUpdateDateNewRoom(lastStay.value)

            getRoomType()
            getRoom() 

        })
});
</script>
<style scoped>
    .box-input{
        padding: .6rem .65rem;
    }
</style>