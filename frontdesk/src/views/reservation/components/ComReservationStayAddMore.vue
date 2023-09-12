<template>
    <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose>
        <div class="bg-card-info border-round-xl p-3 add-room-reserv">
      
            {{ data }}
            <label>Arrival Date <span class="text-red-500">*</span></label>

            <Calendar :selectOtherMonths="true" inputClass="w-7rem" showIcon v-model="data.arrival_date"
                :min-date="moment(edoor_working_day.date_working_day).toDate()" @update:modelValue="onStartDate($event)"
                dateFormat="dd-mm-yy" />
            <label>Departure Date<span class="text-red-500">*</span></label>
            <Calendar :selectOtherMonths="true" inputClass="w-7rem" showIcon v-model="data.departure_date"
                :min-date="new Date(moment(data.arrival_date).add(1, 'days'))" @update:modelValue="onEndDate($event)"
                dateFormat="dd-mm-yy" />
            <label>Nights</label>
            <InputNumber v-model="data.room_nights" @update:modelValue="onNight($event)" inputId="stacked-buttons"
                showButtons :min="1" class="nig_in-put" />

                
            <div class="n__re-custom">
                <table class="w-full">
                    <thead>
                        <tr>
                            <th class="text-left px-2">
                                <label>Room Type<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-left px-2">
                                <label class="px-2">Room Name</label>
                            </th>
                            <th>
                                <label class="text-center ">Adults</label>
                            </th>
                            <th>
                                <label class="text-center">Children</label>
                            </th>
                            <th class="text-right px-2">
                                <label>Rate</label>
                            </th>
                            <th class="text-right px-2">
                                <label>Amount</label>
                            </th>
                            <th class="w-0"></th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(d, index) in data.reservation_stays" :key="index">

                            <td class="px-2 w-15rem">
                                <Dropdown v-model="d.room_type_id" :options="room_types" optionValue="name"
                                @change="onSelectRoomType(d)" 
                                    optionLabel="room_type" placeholder="Select Room Type"
                                    class="w-full" />
                            </td>
                            <td class="px-2 w-10rem">
                                <Dropdown v-model="d.room_id"
                                    :options="rooms.filter((r) => (r.room_type_id == d.room_type_id && (r.selected ?? 0) == 0) || (r.room_type_id == d.room_type_id && r.name == d.room_id))"
                                    optionValue="name" @change="OnSelectRoom" optionLabel="room_number"
                                    placeholder="Select Room" showClear filter class="w-full" />
                            </td>

                            <td class="px-2 w-3rem">
                                <InputNumber v-model="d.adult" style="width: -webkit-fill-available;" inputClass="w-3rem"
                                    inputId="stacked-buttons" showButtons :min="1" :max="100" />
                            </td>
                            <td class="px-2 w-3rem">
                                <InputNumber v-model="d.child" style="width: -webkit-fill-available;" inputClass="w-3rem"
                                    inputId="stacked-buttons" showButtons :min="0" :max="100" />
                            </td>
                            <td class="p-2 text-right w-15rem">
                                <div class="p-inputtext-pt w-full float-right text-end border-1 border-white h-12 inline">
                                    <div v-tooltip.top="(d.is_manual_rate) ? 'Manual Rate' : 'Rate Plan'">

                                        <button @click="onOpenChangeRate($event, d)"
                                            class="text-right w-full color-purple-edoor text-md font-italic ">
                                            <div class="flex justify-between link_line_action">
                                                <div>
                                                    <span class="text-sm" v-if="d.is_manual_rate"> (Manual) </span>
                                                    <span class="text-sm" v-else>(Plan)</span>
                                                </div>
                                                <span>
                                                    <CurrencyFormat :value="d.rate" />
                                                </span>
                                            </div>
                                        </button>
                                    </div>
                                </div>
                            </td>
                            <td class="px-2 w-15rem">
                                <div class="p-inputtext-pt w-full float-right text-end border-1 border-white h-12">
                                    <CurrencyFormat :value="(d.room_nights ?? 0) * (d.rate ?? 0)" />
                                </div>
                            </td>

                            <td v-if="data.reservation_stays.length > 1" class="pl-2 text-end">
                                <Button icon="pi pi-trash" @click="onDeleteStay(index)" class="tr-h__custom text-3xl h-12"
                                    aria-label="Filter" />
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="mt-3 flex justify-end">
                <Button @click="onAddRoom" class="dialog_btn_transform conten-btn py-4">
                    <img :src="IconAddRoom" class="btn-add_comNote__icon me-1" />
                    Add Room
                </Button>
            </div>
        </div>
        <OverlayPanel ref="op">
            <ComReservationStayChangeRate v-model="rate" @onClose="onClose" @onUseRatePlan="onUseRatePlan"
                @onChangeRate="onChangeRate" />
        </OverlayPanel>
        {{ room_types }}
    </ComDialogContent>
</template>
<script setup>
import ComReservationStayChangeRate from "./ComReservationStayChangeRate.vue"
import IconAddRoom from '@/assets/svg/icon-add-plus-sign-purple.svg';
import { ref, inject, postApi, onMounted, getApi } from "@/plugin"

const dialogRef = inject("dialogRef");
const property = JSON.parse(localStorage.getItem("edoor_property"))

const moment = inject("$moment")

const rs = inject("$reservation")
const isSaving = ref(false)
const gv = inject("$gv")

const socket = inject("$socket")
const room_types = ref([])
const rooms = ref([])
const data = ref({
    reservation_stays:[]
})
 
const edoor_working_day = JSON.parse(localStorage.getItem("edoor_working_day"))


const selectedStay = ref({})
const rate = ref(0)
const op = ref();

const doc = ref({
    adult: 1,
    child: 0,
    room_type_id: '',
    room_id: '',
    rate: 0,
    is_manual_rate: false
})
 

const onAddRoom = () => {
    const last_record = data.value.reservation_stays[data.value.reservation_stays.length - 1]
     
    data.value.reservation_stays.push(
        {
            adult: last_record.adult,
            child: last_record.child,
            room_type_id: last_record.room_type_id,
            rate: last_record.rate,
            is_manual_rate: last_record.is_manual_rate
        }
    )
}


const onSave = () => {
    if (data.value.reservation_stays.filter(r => r.room_type_id == "").length > 0) {
        gv.toast('warn', "Please select room type.")
        return
    }
    isSaving.value = true
    let save_data = JSON.parse(JSON.stringify(data.value.reservation_stays))
    save_data = save_data .map((r) => {
        return {
            ...r,
            departure_date: gv.dateApiFormat(r.departure_date),
            arrival_date: gv.dateApiFormat(r.arrival_date)
        }
    })
    postApi("reservation.stay_add_more_rooms", { reservation: rs.reservation.name, data: save_data }).then((r) => {

        if (r) {
            isSaving.value = false
            socket.emit("RefresheDoorDashboard", rs.reservation.property);
            dialogRef.value.close(r)
        }


    }).catch((er) => {
        isSaving.value = false
    })
}




const onDeleteStay = (index) => {
    data.value.reservation_stays.splice(index, 1);
}
const onOpenChangeRate = (event, selected) => {
    rate.value = selected.rate
    selectedStay.value = selected
    op.value.toggle(event);
}
const onChangeRate = () => {
    selectedStay.value.rate = rate.value
    selectedStay.value.is_manual_rate = true
    const index = data.value.reservation_stays.indexOf(selectedStay.value)
    op.value.hide();
}

const onUseRatePlan = () => {
    const index =  data.value.reservation_stays.value.indexOf(selectedStay.value)
    data.value.reservation_stays.value[index].is_manual_rate = false
    data.value.reservation_stays.value[index].rate =  data.value.reservation_stays.value[index].original_rate
    op.value.hide();
}
function onClose() {
    op.value.hide()
}
function onNight(newValue) {
    data.value.departure_date = moment(data.value.arrival_date).add(newValue, 'days').toDate()
}
function onEndDate(newValue) {
    data.value.room_nights = moment(data.value.departure_date).diff(moment(data.value.arrival_date), 'days')

    getRoomType()
    getRooms()
}
function onStartDate(newValue) {
    if (moment(newValue).isSame(data.value.departure_date) || moment(newValue).isAfter(data.value.departure_date)) {
        data.value.departure_date = moment(newValue).add(1, 'days').toDate()
    }
    data.value.room_nights = moment(data.value.departure_date).diff(moment(newValue), 'days')

    
    getRoomType()
    getRooms()

}


const getRoomType = () => {

    getApi("reservation.check_room_type_availability", {
        property: property.name,
        start_date: moment(data.value.arrival_date).format("yyyy-MM-DD"),
        end_date: moment(data.value.departure_date).format("yyyy-MM-DD"),
        rate_type: rs.reservation.rate_type,
        business_source: rs.reservation.business_source
    })
        .then((result) => {
            room_types.value = result.message;
            // updateRate()
        })
}

const getRooms = () => {

    getApi("reservation.check_room_availability", {
        property: property.name,
        start_date: moment(data.value.arrival_date).format("yyyy-MM-DD"),
        end_date: moment(data.value.departure_date).format("yyyy-MM-DD")
    })
        .then((result) => {
            rooms.value = result.message;
            OnSelectRoom()
        })
}

const onSelectRoomType = (stay) => {
     
    stay.room_id = null
    OnSelectRoom()
    updateRate()
}


const updateRate = () => {
    data.value.reservation_stays.filter(r => (r.is_manual_rate || false) == false).forEach(s => {
        const room_type = room_types.value.find(r => r.name == s.room_type_id)


        if (room_type) {

            s.rate = room_type.rate

        }

    });
}

const OnSelectRoom = () => {
    rooms.value.forEach(r => {
        r.selected = 0
    });

    data.value.reservation_stays.forEach(r => {
        let room = rooms.value.find(x => x.name == r.room_id)
        if (room) {
            room.selected = 1
        }
    });

}

function get_rate_type_info(){
    getApi("utils.get_rate_type_info", { name: rs.reservation.rate_type }).then((result) => {
        
            // doc.value.reservation.tax_rule = (result.message?.tax_rule?.name || "")
            // const tax_rule = result.message.tax_rule
            // doc.value.tax_rule = {
            //     rate_include_tax: tax_rule?.is_rate_include_tax ? "Yes" : "No",
            //     tax_1_rate: tax_rule?.tax_1_rate || 0,
            //     tax_2_rate: tax_rule?.tax_2_rate || 0,
            //     tax_3_rate: tax_rule?.tax_3_rate || 0,
            // }
            // room_tax.value = tax_rule
            // doc.value.reservation.rate_type = rate_type.value

            //     //check if stay have not manully rate update
            // if (doc.value.reservation_stay.filter(r => (r.is_manual_rate || false) == false).length > 0) {
            //     getRoomType()
            // }

        })
}

onMounted(() => {
    if (rs.reservation) {
        const arrival_date = ref(moment(rs.reservation.arrival_date).toDate())

        if (moment(arrival_date.value).isSame(edoor_working_day.date_working_day) || moment(arrival_date.value).isBefore(edoor_working_day.date_working_day)) {
            arrival_date.value = moment(edoor_working_day.date_working_day).toDate()
        }
        const departure_date = ref(moment(rs.reservation.departure_date).toDate())
        if (moment(departure_date.value).isSame(arrival_date.value) || moment(departure_date.value).isBefore(arrival_date.value)) {
            departure_date.value = moment(arrival_date.value).add(1, 'days').toDate()
        }
        data.value.arrival_date = arrival_date.value
        data.value.departure_date = departure_date.value
        data.value.room_nights = moment(departure_date.value).diff(moment(arrival_date.value), 'days')
        data.value.reservation_stays.push(doc.value)
         
        getRoomType()
        getRooms()

    }
   

})
</script>
<style>.ch__rate_nres input {
    text-align: right !important;
    font-size: 1.1rem;
    height: 3rem;
}

.p-button.p-component .p-button-icon {
    font-weight: 600;
    font-size: 1.25rem;
}</style>