<template >
    <ComDialogContent :hideButtonOK="data?.length == 0 ? true : false" :hideButtonClose="data?.length == 0 ? true : false"  @onClose="onClose" @onOK="onSave" :loading="loading">
    <ComReservationStayPanel title="Group Assign Room">
        <template #content> 
    <div v-if="data?.length == 0">No Reservation Stay to Assign Room</div>
    <div v-else class="w-full overflow-auto">
    <table class="w-full" >
        <tr class="font-medium">
            <td>Stay Date</td>
            <td>Guest</td>
            <td>Rate Type</td>
            <td>Room Type</td>
            <td>Room Name</td>
            <td class="text-center">Nights</td>
            <td class="text-right">Rate</td>
        </tr>
        <template  v-for="(d, index) in data" :key="index">
            <tr>
            <td>
                <div class="box-input px-3 border-round-lg overflow-hidden text-overflow-ellipsis whitespace-nowrap border border-white p-inputtext-pt" >
                <span  v-tippy="'Arrival date'"> {{ moment(d.start_date).format("DD-MM-YYYY") }}</span> &#8594;
                <span  v-tippy="'Departure date'">{{ moment(d.end_date).format("DD-MM-YYYY") }}</span>
                </div>
                
            </td>
            <td>
                <div class="box-input  px-3 border-round-lg overflow-hidden text-overflow-ellipsis whitespace-nowrap border border-white p-inputtext-pt">
                {{ d.guest }} - {{ d.guest_name }}
                </div>
            </td>
            <td>
                <div class="box-input  px-3 border-round-lg overflow-hidden text-overflow-ellipsis whitespace-nowrap border border-white p-inputtext-pt">
                    {{ d.rate_type }}
                </div>
            </td>
            <td class="pr-2 select-room-type-style"  >

                <Dropdown class="w-full" v-model="d.new_room_type_id" :options="get_room_types(d)" optionValue="name"
                    @change="onSelectRoomType(d)" optionLabel="room_type" placeholder="Select Room Type" >
                 <template #option="slotProps">
                                        <div class="flex align-items-center">
                                            <div>{{ slotProps.option.room_type }} ({{ slotProps.option.total_vacant_room }})</div>
                                        </div>
                                    </template>
                                </Dropdown>

           
            </td>
            <td class="p-2 select-room-number-style">
                <Dropdown class="w-full" v-model="d.room_id" :options="get_rooms(d)" optionValue="name" 
                    optionLabel="room_number" placeholder="Select Room" showClear filter />

            </td>

            <td class="text-center w-5rem">
                <div class="w-full box-input px-3 border-round-lg overflow-hidden text-overflow-ellipsis whitespace-nowrap border border-white p-inputtext-pt">
                {{ d.room_nights }}
                </div>
            </td>
            <td class="text-right w-10rem">
                <div class="w-full box-input px-3 border-round-lg overflow-hidden text-overflow-ellipsis whitespace-nowrap border border-white p-inputtext-pt">
                <CurrencyFormat :value="d.rate"></CurrencyFormat>
                    {{ d.input_rate }}
                </div>
            </td>


        </tr>
        <tr v-if="d.room_type_id != d.new_room_type_id" >
            <td colspan="7">
                <Message >
                    <Checkbox v-model="d.is_generate_rate" :binary="true" :trueValue="1" :falseValue="0"  @input="onUpdateRate(d)" />
 
                    <label class="mr-3 cursor-pointer">Room type of this reservation stay is changed. Do you want to
                        regenerate rate</label>
                </Message>
            </td>
        </tr>
           
                
        </template>
      
    </table>
</div>
</template>
</ComReservationStayPanel>  

   
</ComDialogContent>
</template>
<script setup>
import { ref, getApi, inject, onMounted, postApi, computed } from "@/plugin"
import Message from "primevue/message";
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';

const loading = ref(false)
const dialogRef = inject("dialogRef");
const data = ref([])

const moment = inject("$moment")
const reservation = ref({})
const room_data = ref([])


function onUpdateRate(d) {
    if (d.is_generate_rate == 1 && d.room_type_id != d.new_room_type_id) {
      
        const data = room_data.value.filter(r => r.start_date == d.start_date)
 
        if (data.length > 0) {
          
            if (data[0].room_types.length > 0) {

                
                const room_type = data[0].room_types.find(r => r.name == d.new_room_type_id)

                if (room_type) {
                    d.rate = room_type.rate.rate
                }
            }
        }
    } else {
        d.rate = d.old_rate
    }

}

function get_room_types(d) {
   
    return room_data.value.find(r => r.start_date == d.start_date && r.end_date == d.end_date).room_types;//.filter(r=>r.total_vacant_room>0)
}

const get_rooms = ref((d) => {

    if (room_data.value) {
        let rooms = []
        const roomNumbersToExclude = data.value.filter(r => r.room_id).map(r => r.room_id)
        rooms = room_data.value.find(r => r.start_date == d.start_date && r.end_date == d.end_date).rooms
        rooms = rooms.filter(r => (r.room_type_id == d.new_room_type_id && !roomNumbersToExclude.includes(r.name)) || (r.name == d.room_id && r.room_type_id == d.new_room_type_id))


        return rooms

    } else {
        return []
    }

});

const onClose = (d) =>{ 
        dialogRef.value.close(d);
    }


const onSelectRoomType = (d) => {
    
    if (d.room_type_id != d.new_room_type_id) {
        d.room_id = null
        d.room_number = null
    } else {
        d.is_generate_rate = false
    }

    onUpdateRate(d)
}



function onSave() {
    loading.value = true
    postApi("reservation.bulk_assign_room", {
        reservation:reservation.value.name,
        reservation_stays: data.value.filter(r=>r.room_id)
        
    }).then((result) => {
        loading.value = false
        window.postMessage({"action":"Dashboard"},"*")
        window.postMessage({"action":"Frontdesk"},"*")
        window.postMessage({"action":"ReservationDetail"},"*")
        window.postMessage({action:"ReservationList"},"*")
        window.postMessage({action:"ReservationStayList"},"*")
        window.postMessage({action:"GuestLedger"},"*")
        window.postMessage({action:"Reports"},"*")
        dialogRef.value.close("open_reservation_detail")
        data.value.map(r=>r.reservation_stay).forEach(r => {
            window.postMessage({action:"ReservationStayDetail"},"*")
        });
        window.postMessage({action:"FolioTransactionList"},"*")

    }).catch((err) => {
        loading.value = false
    })
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
            data.value.forEach(r => {
                r.room_id = null,
                r.old_rate = r.rate
            });


            loading.value = false
        }).catch((err) => {
            loading.value = false
        })
        if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
})





</script>
<style scoped>
td{
    padding:0 0.5rem;
}
.p-inputtext-pt{
    background-color: #ebf0f6 !important;
}
</style>