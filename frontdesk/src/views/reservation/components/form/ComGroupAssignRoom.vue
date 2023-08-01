<template >
    <h1>Group Assign Room</h1>
  

    <div v-if="data?.length == 0">No Reservation Stay to Assign Room</div>
    <table v-else>
        <tr>
            <td>Stay Date</td>
            <td>End Date</td>
            <td>Guest</td>
            <td>Rate Type</td>
            <td>Book Room Type</td>
            <td>Selected Room Type</td>
            <td>Room</td>
            <td>Room Night(s)</td>
            <td>Rate</td>
        </tr>
        <tr v-for="(d, index) in data" :key="index">
            <td>
                {{ moment(d.start_date).format("DD-MM-YYYY") }}
            </td>
            <td>
                {{ moment(d.end_date).format("DD-MM-YYYY") }}
            </td>
            <td>
                {{ d.guest }} - {{ d.guest_name }}
            </td>
            <td>
                {{ d.rate_type }}
            </td>

            <td>
                {{d.room_type}}

            </td>
            <td class="pr-2">
 
                <Dropdown v-model="d.new_room_type_id" :options="get_room_types(d)" optionValue="name"
                   @change="onSelectRoomType(d)" optionLabel="room_type" placeholder="Select Room Type" />

                <Message v-if="d.room_type_id!=d.new_room_type_id">
                    <Checkbox  v-model="d.is_generate_rate" :binary="true" />
                    <label  class="mr-3 cursor-pointer">Room type of this reservation stay is changed. Do you want to regenerate rate</label>
                </Message>
            </td>
            <td class="p-2">
                <Dropdown v-model="d.room_id" :options="get_rooms(d)" optionValue="name" @change="OnSelectRoom"
                    optionLabel="room_number" placeholder="Select Room" showClear filter />
 
            </td>

            <td>
                {{ d.room_nights }}
            </td>
            <td>
                <CurrencyFormat :value="d.rate"></CurrencyFormat>
            </td>


        </tr>
    </table>
    <Button @click="onSave()">Save</Button>
</template>
<script setup>
import { ref, getApi, inject, onMounted, computed } from "@/plugin"
import Message from "primevue/message";
const loading = ref(false)
const dialogRef = inject("dialogRef");
const data = ref([])
const moment = inject("$moment")
const reservation = ref({})
const room_data = ref([])

function get_room_types(d) {

    return room_data.value.find(r => r.start_date == d.start_date && r.end_date == d.end_date).room_types;//.filter(r=>r.total_vacant_room>0)
}

const get_rooms = ref((d) => {

    if (room_data.value) {
        let rooms = []
       
        const roomNumbersToExclude = data.value.filter(r => r.room_id).map(r => r.room_id)
        
        

        rooms = room_data.value.find(r => r.start_date == d.start_date && r.end_date == d.end_date).rooms
        rooms = rooms.filter(r => (r.room_type_id == d.new_room_type_id && !roomNumbersToExclude.includes(r.name)) || (r.name == d.room_id && r.room_type_id==d.new_room_type_id))


        return rooms

    } else {
        return []
    }

});



const onSelectRoomType = (d) => {
   if(d.room_type_id!=d.new_room_type_id){
    d.room_id=null

   }else {
    d.is_generate_rate = false
   }
}



onMounted(() => {
    loading.value = true

    reservation.value = dialogRef.value.data.reservation
    getApi("reservation.get_reservation_stay_for_assign_room",
        {
            "reservation": dialogRef.value.data.reservation.name
        }).then((result) => {
            data.value = result.message.data
            room_data.value = result.message.rooms


            loading.value = false
        }).catch((err) => {
            loading.value = false
        })

})





</script>