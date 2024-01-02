<template>
    <ComDialogContent :hideButtonClose="true"  @onOK="onSave" :loading="loading">
        <div class="grid bg-card-info border-round-xl p-3 add-room-reserv h-full my-2">
        <div class="col">
            <label>Arrival Date<span class="text-red-500">*</span></label><br />
            <Calendar panelClass="no-btn-clear" :selectOtherMonths="true" class="p-inputtext-sm depart-arr w-full border-round-xl"
            v-model="data.arrival_date"
                placeholder="Arrival Date" @date-select="onDateSelect" dateFormat="dd-mm-yy" showIcon showButtonBar />
        </div>
        <div class="night__wfit col-fixed px-0" style="width: 150px;">
            <div>
                <label class="hidden">Room Night<span class="text-red-500">*</span></label><br />
            </div>
            <ComReservationInputNight v-model="data.room_night"
                @onUpdate="onRoomNightChanged" />
        </div>
        <div class="arr_wfit col">
            <label>Departure<span class="text-red-500">*</span></label><br />
            <Calendar panelClass="no-btn-clear" :selectOtherMonths="true" class="p-inputtext-sm depart-arr w-full" placeholder="Departure Date"
            v-model="data.departure_date"
                @date-select="onDateSelect" dateFormat="dd-mm-yy" :minDate="departureMinDate" showIcon showButtonBar />
        </div>    
   <div class="col-12">
        <div class="flex flex-wrap gap-3 justify-end mt-3 ">
            <div class="flex align-items-center ">
                <RadioButton inputId="stay_rate" name="generate_new_stay_rate_by" value="stay_rate"  v-model="data.generate_new_stay_rate_by"/>
                <label for="stay_rate" class="ml-2">Generate New Stay Rate from Last First/Last Stay Rate</label>
            </div>
            <div class="flex align-items-center">
                <RadioButton inputId="rate_plan" name="generate_new_stay_rate_by" value="rate_plan"  v-model="data.generate_new_stay_rate_by"/>
                <label for="rate_plan" class="ml-2">Generate New Stay Rate from Rate Type</label>
            </div>
            
        </div>
    </div>
     </div>
        <div class="mt-3">
            <div>
                <label>Note</label><br />
                <Textarea rows="5" placeholder="Note" cols="30" class="w-full border-round-xl"  v-model="data.note"/>
                
            </div>
        </div>
    </ComDialogContent>
</template>
<script setup>
import { inject, ref, onMounted ,postApi,computed,useToast} from '@/plugin'
import ComReservationInputNight from '../ComReservationInputNight.vue';
const toast = useToast();
const dialogRef = inject("dialogRef");
const stays = ref([])
const loading = ref(false)
import Enumerable from 'linq'
const data = ref({generate_new_stay_rate_by:"stay_rate"})
const moment = inject("$moment")
const rs = inject("$reservation")
const working_day = window.working_day
const onRoomNightChanged = (event) => {
    data.value.departure_date = moment(data.value.arrival_date).add(event, "Days").toDate()
}

function onSave(){
    loading.value = true
    postApi("group_operation.group_change_stay", { 
        data:{ 
            stays:stays.value.filter(r => r.name).map(r => r.name),
            arrival:moment(data.value.arrival_date).format("YYYY-MM-DD"),
            departure:moment(data.value.departure_date).format("YYYY-MM-DD"),
            note:data.value.note,
            generate_new_stay_rate_by:data.value.generate_new_stay_rate_by,
            property:window.property_name,
            reservation: rs.reservation.name
        }
    }).then((result) => {   
        loading.value = false
        result.message.forEach(x => {
            toast.add({ severity: 'warn', summary:"Reservation Stay #" +  x.reservation_stay, detail: x.message, life: 7000 }) 
        });
        dialogRef.value.close(rs.selecteds = [])
        window.socket.emit("ReservationList", { property:window.property_name})
        window.socket.emit("ReservationDetail", window.reservation)
    }).catch((err) => {
        loading.value = false
    })
}

const departureMinDate = computed(() => {
    return moment(data.value.arrival_date).add(1, "days").toDate();
})
const onDateSelect = (date) => {

    let arrival_date = moment(data.value.arrival_date).format("YYYY-MM-DD")
    arrival_date = moment(arrival_date).toDate()

    let departure_date = moment(data.value.departure_date).format("YYYY-MM-DD")
    departure_date = moment(departure_date).toDate()

    if (arrival_date >= departure_date) {
        data.value.departure_date = moment(data.value.arrival_date).add(1, 'days').toDate()
        
    }
    data.value.room_night = moment(data.value.departure_date).diff(moment(data.value.arrival_date), 'days')
}
onMounted(() => {
    stays.value = dialogRef.value.data
    data.value.arrival_date = Enumerable.from(stays.value).select(x => new Date(x.arrival_date)).min();
    data.value.departure_date = Enumerable.from(stays.value).select(x => new Date(x.departure_date)).max();
    // data.value.room_nights =  moment(data.value.departure_date).diff(moment(data.value.arrival_date), 'days');
    onDateSelect()
})

</script>