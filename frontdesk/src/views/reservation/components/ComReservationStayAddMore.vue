<template>
    <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose>
        <div class="bg-card-info border-round-xl p-3 add-room-reserv h-full">
        <div class="grid">
            <div class="col">
              <label>Arrival Date <span class="text-red-500">*</span></label>
            <Calendar :selectOtherMonths="true" class="w-full" inputClass="w-full" showIcon v-model="data.arrival_date"
                :min-date="moment(edoor_working_day.date_working_day).toDate()" @update:modelValue="onStartDate($event)"
                dateFormat="dd-mm-yy" />  
            </div>
            <div class="col-fixed px-0" style="width: 150px;">
                <div>
                    <label class="hidden">Room Night<span class="text-red-500">*</span></label><br />
                </div>
                    <ComReservationInputNight v-model="data.room_nights"
                                    @onUpdate="onNight($event)" />  
            </div>
            <div class="col">
            <label>Departure Date<span class="text-red-500">*</span></label>
            <Calendar :selectOtherMonths="true" class="w-full" inputClass="w-full" showIcon v-model="data.departure_date"
                :min-date="new Date(moment(data.arrival_date).add(1, 'days'))" @update:modelValue="onEndDate($event)"
                dateFormat="dd-mm-yy" />    
            </div>  
        </div>
        </div>
        <div v-if="room_tax && (room_tax.tax_1_rate + room_tax.tax_2_rate + room_tax.tax_3_rate) > 0" class="bg-card-info border-round-xl p-3 add-room-reserv h-full mt-3">
        <div class="grid" >
            <div class="col">
                <div class="bg-card-info border-round-xl  h-full">
                    <div class="flex gap-2 align-items-center relative my-3 " style="width: 12.7rem;">
                        <label for="include-tax" class="font-medium cursor-pointer">Rate Include Tax</label>
                        <span class="absolute right-0 w-full">
                            <Checkbox input-id="rate_tax" class="w-full flex justify-end "
                                v-model="data.rate_include_tax" :binary="true" trueValue="Yes" falseValue="No" />
                        </span>
                    </div>
                    <div class="">
                        <div class="flex gap-3 flex-wrap,">
                            <div class="flex gap-3 relative" >
                                <label for="tax-1-rate" class="font-medium flex align-items-center h-full">{{
                                    room_tax.tax_1_name }} {{ room_tax.tax_1_rate }}%</label>
                                <div class="p-inputtext-pt text-center border-1 border-white flex w-16rem border-round-lg">
                                    <span class="w-full">
                                        <Checkbox input-id="tax-1-rate" class="w-full" v-model="useTax.use_tax_1"
                                            @input="onUseTax1Change" :binary="true" />
                                    </span>
                                    <div class="white-space-nowrap">
                                        <CurrencyFormat :value="totalTax1Amount" />
                                    </div>
                                </div>
                            </div>
                            <div class="flex gap-10 relative,">
                                <label for="tax-2-rate" class="font-medium flex align-items-center h-full">{{
                                    room_tax.tax_2_name }}{{ room_tax.tax_2_rate }}%</label>
                                <div class="p-inputtext-pt text-center border-1 border-white flex w-16rem border-round-lg">
                                    <span class="w-full">
                                        <Checkbox input-id="tax-2-rate" class="w-full" v-model="useTax.use_tax_2"
                                            @input="onUseTax2Change" :binary="true" />
                                    </span>
                                    <div class="white-space-nowrap">
                                        <CurrencyFormat :value="totalTax2Amount" />
                                    </div>
                                </div>
                            </div>
                            <div class="flex gap-10 relative">
                                <label for="tax-3-rate" class="font-medium flex align-items-center h-full">{{
                                    room_tax.tax_3_name }}{{ room_tax.tax_3_rate }}%</label>
                                <div class="p-inputtext-pt text-center border-1 border-white flex w-16rem border-round-lg">
                                    <span class="w-full">
                                        <Checkbox input-id="tax-3-rate" class="w-full" v-model="useTax.use_tax_3"
                                            @input="onUseTax3Change" :binary="true" />
                                    </span>
                                    <div class="white-space-nowrap">
                                        <CurrencyFormat :value="totalTax3Amount" />
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        </div>
        <div class="bg-card-info border-round-xl p-3 add-room-reserv h-full mt-3">        
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
                                <label>Total Tax</label>
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
                                    class="w-full" >
                                    <template #option="slotProps">
                                        <div class="flex align-items-center">
                                           
                                            <div>{{ slotProps.option.room_type }} ({{ slotProps.option.total_vacant_room }})</div>
                                        </div>
                                    </template>
                                </Dropdown>
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
                                    <div  v-tippy ="(d.is_manual_rate) ? 'Manual Rate' : 'Rate Plan'">

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
                            <td class="p-2 w-12rem text-right">
                                <div class="box-input-detail">
                                    <CurrencyFormat :value="roomRateTax(d)" />
                                </div>
                            </td>
                            <td class="px-2 w-15rem">
                                <div class="p-inputtext-pt w-full float-right text-end border-1 border-white h-12" v-if="data.rate_include_tax == 'Yes'">
                                    <CurrencyFormat :value="(d.rate) * (data.room_nights ?? 0)" />
                                </div>
                                <div class="p-inputtext-pt text-end border-1 border-white h-12" v-else>
                                    <CurrencyFormat
                                        :value="(roomRateTax(d)) + (d.rate * data.room_nights ?? 0)" />
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
        <Message severity="warn"  v-if="warningMessage" v-for="(m, index) in warningMessage" :key="index" >
                <p v-html="m"></p>
            </Message>
        <OverlayPanel ref="op">
            <ComReservationStayChangeRate v-model="rate" @onClose="onClose" @onUseRatePlan="onUseRatePlan"
                @onChangeRate="onChangeRate" />
        </OverlayPanel>
       
    </ComDialogContent>
</template>
<script setup>
import ComReservationStayChangeRate from "./ComReservationStayChangeRate.vue"
import IconAddRoom from '@/assets/svg/icon-add-plus-sign-purple.svg';
import { ref, inject, postApi, onMounted, getApi, computed} from "@/plugin"
import ComReservationInputNight from '@/views/reservation/components/ComReservationInputNight.vue';

const dialogRef = inject("dialogRef");
const property = JSON.parse(localStorage.getItem("edoor_property"))

const moment = inject("$moment")

const rs = inject("$reservation")
const isSaving = ref(false)
const gv = inject("$gv")
const room_types = ref([])
const rooms = ref([])
const data = ref({
    reservation_stays:[]
})
const room_tax = ref()
const edoor_working_day = JSON.parse(localStorage.getItem("edoor_working_day"))



const warningMessage = computed(()=>{
    const messages = []
    const room_type =  [...new Set( data.value.reservation_stays.filter(x=>x.room_type_id).map(item => item.room_type_id))] 
    if (room_type){
        room_type.forEach(r => {
            const rt = room_types.value.find(rt=>rt.name==r)
           
            if(data.value.reservation_stays.filter(x=>x.room_type_id==r).length>rt.total_vacant_room){
                messages.push("You have over booking on room type <strong>" + rt.room_type + "</strong>. Total Over: <strong>" + Math.abs(rt.total_vacant_room -  data.value.reservation_stays.filter(x=>x.room_type_id==r).length)) + "</strong>"
            }
        })
    
    }
    
    return messages
})


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
 
const useTax = computed(() => {
    return {
        use_tax_1: (room_tax.value.tax_1_rate || 0) > 0,
        use_tax_2: (room_tax.value.tax_2_rate || 0) > 0,
        use_tax_3: (room_tax.value.tax_3_rate || 0) > 0
    }
})
const onUseTax1Change = (value) => {
    data.value.tax_1_rate = value ? room_tax.value.tax_1_rate : 0
}
const onUseTax2Change = (value) => {
    data.value.tax_2_rate = value ? room_tax.value.tax_2_rate : 0
}
const onUseTax3Change = (value) => {
    data.value.tax_3_rate = value ? room_tax.value.tax_3_rate : 0
}

const roomRateTax = ref((d) => {
    const tax_1_amount = getTax1Amount(d.rate * data.value.room_nights)
    const tax_2_amount = getTax2Amount(d.rate * data.value.room_nights)
    const tax_3_amount = getTax3Amount(d.rate * data.value.room_nights)
    return tax_1_amount + tax_2_amount + tax_3_amount
});


function getTax1Amount(rate) {
    if (room_tax.value) {
        if (room_tax.value?.calculate_tax_1_after_discount == 0 || data.value.rate_include_tax == 'Yes') {
            rate = gv.getRateBeforeTax((rate || 0), room_tax.value, data.value.tax_1_rate, data.value.tax_2_rate, data.value.tax_3_rate)

        } else {
            rate = rate

        }
        return (rate || 0) * (data.value.tax_1_rate / 100 || 0)
    } else {
        return 0
    }
}
function getTax2Amount(rate) {

    if (room_tax.value) {
        if (room_tax.value?.calculate_tax_1_after_discount == 0 || data.value.rate_include_tax == 'Yes') {
            rate = gv.getRateBeforeTax((rate || 0), room_tax.value, data.value.tax_1_rate, data.value.tax_2_rate, data.value.tax_3_rate)

        } else {
            rate = rate

        }
        if (room_tax.value?.calculate_tax_2_after_adding_tax_1 == 0 || (rate * (data.value.tax_1_rate / 100)) == 0) {
            rate = rate
        } else { rate = rate + (rate * (data.value.tax_1_rate / 100)) }
        return (rate || 0) * (data.value.tax_2_rate / 100 || 0)
    } else {
        return 0
    }
}
function getTax3Amount(rate) {
    if (room_tax.value) {
        if (room_tax.value?.calculate_tax_1_after_discount == 0 || data.value.rate_include_tax == 'Yes') {
            rate = gv.getRateBeforeTax((rate || 0), room_tax.value, data.value.tax_1_rate, data.value.tax_2_rate, data.value.tax_3_rate)

        } else {
            rate = rate

        }
        if (room_tax.value.calculate_tax_2_after_adding_tax_1 == 0 || (rate * (data.value.tax_1_rate / 100)) == 0) {
            rate = rate
        } else { rate = rate + (rate * (data.value.tax_1_rate / 100)) }
        if (room_tax.value.calculate_tax_3_after_adding_tax_2 == 0 || (rate * (data.value.tax_2_rate / 100)) == 0) {
            rate = rate
        } else { rate = rate + (rate * (data.value.tax_2_rate / 100)) }
        return (rate || 0) * (data.value.tax_3_rate / 100 || 0)
    } else {
        return 0
    }
}

const totalTax1Amount = computed(() => {
    let amount = 0
    data.value.reservation_stays.forEach(r => {
        amount = amount + getTax1Amount(r.rate)
    });
    return amount * data.value.room_nights
})
const totalTax2Amount = computed(() => {
    let amount = 0
    data.value.reservation_stays.forEach(r => {
        amount = amount + getTax2Amount(r.rate)
    });
    return amount * data.value.room_nights
})
const totalTax3Amount = computed(() => {
    let amount = 0
    data.value.reservation_stays.forEach(r => {
        amount = amount + getTax3Amount(r.rate)
    });
    return amount * data.value.room_nights
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
    let save_data = JSON.parse(JSON.stringify(data.value))
    save_data.arrival_date = moment(save_data.arrival_date).format("yyyy-MM-DD")
    save_data.departure_date = moment(save_data.departure_date).format("yyyy-MM-DD")
    
    postApi("reservation.stay_add_more_rooms", { reservation: rs.reservation.name, data: save_data }).then((r) => {

        if (r) {
            isSaving.value = false
            window.socket.emit("Dashboard", rs.reservation.property);
            window.socket.emit("ReservationList", { property:window.property_name})
            // window.socket.emit("ReservationDetail", window.reservation)
            dialogRef.value.close(r)
        }


    }).catch((er) => {
        console.log(er)
        isSaving.value = false
    })
}




const onDeleteStay = (index) => {

     if(data.value.reservation_stays[index]?.room_id){
        let room = rooms.value.find(r=>r.name == data.value.reservation_stays[index]?.room_id)
        room.selected = 0
    }
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
    const index =  data.value.reservation_stays.indexOf(selectedStay.value)
    data.value.reservation_stays[index].is_manual_rate = false
    // data.value.reservation_stays[index].rate =  data.value.reservation_stays.value[index].original_rate
    updateRate()
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
            s.rate = room_type.rate.rate
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
        }else {
            r.room_id = null
        }
    });

}

function get_rate_type_info(){
    
    getApi("utils.get_rate_type_info", { name: rs.reservation.rate_type }).then((result) => {
            
            data.value.tax_rule = (result.message?.tax_rule?.name || "")
            const tax_rule = result.message.tax_rule
            data.value.rate_include_tax= tax_rule?.is_rate_include_tax ? "Yes" : "No"
            data.value.tax_1_rate =  tax_rule?.tax_1_rate || 0
            data.value.tax_2_rate =  tax_rule?.tax_2_rate || 0
            data.value.tax_3_rate = tax_rule?.tax_3_rate || 0
            room_tax.value = tax_rule
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
        get_rate_type_info();

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