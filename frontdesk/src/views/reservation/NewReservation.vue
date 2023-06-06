<template>
    <ComDialogContent @onOK="onSave" :loading="isSaving" hideButtonClose>
        <div class="n__re-custom grid">
            <div class="col">
                <div class="bg-card-info border-round-xl p-3 h-full">
                    <div class="">
                        <div class="grid">
                            <div class="col">
                                <label>Reservation Date<span class="text-red-500">*</span></label><br />
                                <Calendar class="p-inputtext-sm w-full" v-model="doc.reservation.reservation_date"
                                    placeholder="Reservation Date" dateFormat="dd-mm-yy" showIcon showButtonBar />
                            </div>
                            <div class="col-6"> </div>
                        </div>
                        <div class="grid pt-2">
                            <div class="col-6">
                                <label>Reference No</label><br />
                                <InputText type="text" class="p-inputtext-sm w-full" placeholder="Reference Number"
                                    v-model="doc.reservation.reference_number" :maxlength="50" />
                            </div>
                            <div class="col-6">
                                <label>Internal Ref. No</label><br />
                                <InputText type="text" class="p-inputtext-sm w-full" placeholder="Internal Ref. Number"
                                    v-model="doc.reservation.internal_reference_number" :maxlength="50" />
                            </div>
                        </div>
                        <div class="grid m-0">
                            <div class="arr_wfit col px-0">
                                <label>Arrival<span class="text-red-500">*</span></label><br />
                                <Calendar class="p-inputtext-sm depart-arr w-full border-round-xl"
                                    v-model="doc.reservation.arrival_date" placeholder="Arrival Date"
                                    @date-select="onDateSelect" dateFormat="dd-mm-yy" showIcon showButtonBar />
                            </div>
                            <div class="night__wfit col-fixed px-0" style="width: 150px;">
                                <div>
                                    <label class="hidden">Room Night<span class="text-red-500">*</span></label><br />
                                </div>
                                <ComReservationInputNight v-model="doc.reservation.room_night"
                                    @onUpdate="onRoomNightChanged" />
                            </div>
                            <div class="arr_wfit col px-0">
                                <label>Departure<span class="text-red-500">*</span></label><br />
                                <Calendar class="p-inputtext-sm depart-arr w-full" v-model="doc.reservation.departure_date"
                                    placeholder="Departure Date" @date-select="onDateSelect" dateFormat="dd-mm-yy"
                                    :minDate="departureMinDate" showIcon />
                            </div>
                        </div>
                    </div>

                    <div class="">
                        <div class="grid">
                            <div class="col-12 lg:col-6">
                                <div class="pt-2">
                                    <label>Business Source<span class="text-red-500">*</span></label><br />
                                    <ComAutoComplete v-model="doc.reservation.business_source" placeholder="Business Source"
                                        @onSelected="onBusinessSourceChange" doctype="Business Source"
                                        class="auto__Com_Cus w-full" />
                                </div>
                            </div>
                            <div class="col-12 lg:col-6">
                                <div class="pt-2">
                                    <label>Rate Type<span class="text-red-500">*</span></label><br />
                                    <ComSelect :clear="false" v-model="doc.reservation.rate_type" :default="true"
                                        @onSelected="onRateTypeChange" placeholder="Rate Type" doctype="Rate Type"
                                        class="auto__Com_Cus w-full" />

                                </div>
                            </div>
                        </div>
                        <div class="pt-2 flex justify-end">
                            <div>
                                <div class="text-center">
                                    <label class="text-center">Total Pax</label><br>
                                </div>
                                <div class="p-inputtext-pt text-center border-1 border-white h-12 w-7rem">{{
                                    doc.reservation_stay.reduce((n, d) => n + d.adult, 0) }} / {{
        doc.reservation_stay.reduce((n, d) => n + d.child, 0) }}</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col">
                <div class="bg-card-info border-round-xl p-3 h-full">
                    <h1 class="text-lg line-height-4 font-bold mb-3">Guest Information</h1>
                    <div>
                        <div class="w-full n__re-custom">
                            <label>Return Guest</label>
                            <ComAutoComplete isIconSearch v-model="doc.reservation.guest" class="pb-2"
                                placeholder="Return Guest" doctype="Customer" @onSelected="onSelectedCustomer" />
                            <hr class="my-3" />
                            <div class="grid">
                                <div class="col-12 pt-2">
                                    <label>New Guest Name<span class="text-red-500">*</span></label><br />
                                    <InputText type="text" class="p-inputtext-sm h-12 w-full" placeholder="New Guest Name"
                                        v-model="doc.guest_info.customer_name_en" :maxlength="50" />
                                </div>
                                <div class="col-12 lg:col-6 xl:col-4 pt-2">
                                    <label>Guest Type<span class="text-red-500">*</span></label><br />
                                    <ComAutoComplete v-model="doc.guest_info.customer_group" class="w-full"
                                        placeholder="Guest Type" doctype="Customer Group" />
                                </div>
                                <div class="col-12 lg:col-6 xl:col-4 pt-2">
                                    <label>Gender</label><br />
                                    <Dropdown v-model="doc.guest_info.gender" :options="gender_list" placeholder="Gender"
                                        class="w-full" />
                                </div>
                                <div class="col-12 lg:col-6 xl:col-4 pt-2">
                                    <label>Country</label><br />
                                    <ComAutoComplete v-model="doc.guest_info.country" class="w-full" placeholder="Country"
                                        doctype="Country" />
                                </div>
                                <div class="col-12 lg:col-6 xl:col-4 pt-1">
                                    <label>Phone Number</label><br />
                                    <InputText type="text" class="p-inputtext-sm w-full" placeholder="Phone Number"
                                        v-model="doc.guest_info.phone_number" :maxlength="50" />
                                </div>
                                <div class="col-12 lg:col-6 xl:col-8 pt-1">
                                    <label>Email Address</label><br />
                                    <InputText type="text" class="p-inputtext-sm w-full" placeholder="Email Address"
                                        v-model="doc.guest_info.email_address" :maxlength="50" />
                                </div>
                                <div class="col-12 lg:col-6 xl:col-4 pt-1">
                                    <label>Identity Type</label><br />
                                    <ComAutoComplete v-model="doc.guest_info.identity_type" class="w-full"
                                        placeholder="Identity Type" doctype="Identity Type" />
                                </div>
                                <div class="col-12 lg:col-6 xl:col-4 pt-1">
                                    <label class="white-space-nowrap">ID/Passport Number</label><br />
                                    <InputText type="text" class="p-inputtext-sm w-full" placeholder="ID/Passport Number"
                                        v-model="doc.guest_info.id_card_number" :maxlength="50" />
                                </div>
                                <div class="col-12 lg:col-6 xl:col-4 pt-1">
                                    <label>ID Expire Date</label><br />
                                    <Calendar class="p-inputtext-sm w-full" v-model="doc.guest_info.expired_date"
                                        placeholder="ID Expire Date" dateFormat="dd-mm-yy" showIcon />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="bg-card-info border-round-xl mt-3 p-3 add-room-reserv">
            <div class="n__re-custom">
                <table class="w-full">
                    <thead>
                        <tr>
                            <th>
                                <div class="font-medium text-left">Room Type<span class="text-red-500">*</span></div>
                            </th>
                            <th>
                                <div class="font-medium text-left px-2">Room Name<span class="text-red-500">*</span></div>
                            </th>
                            <th>
                                <div class="font-medium text-right px-2">Rate<span class="text-red-500">*</span></div>
                            </th>
                            <th>
                                <div class="font-medium text-center px-2">Adults<span class="text-red-500">*</span></div>
                            </th>
                            <th>
                                <div class="font-medium text-center px-2">Children</div>
                            </th>
                            <th>
                                <div class="font-medium text-center px-2">Total Nights</div>
                            </th>
                            <th>
                                <div class="font-medium text-right px-2">Amount</div>
                            </th>

                        </tr>
                    </thead>
                    <tbody>


                        <tr v-for="(  d, index  ) in   doc.reservation_stay  " :key="index">
                            <td class="pr-2">
                                <Dropdown v-model="d.room_type_id" :options="room_types" optionValue="name"
                                    @change="onSelectRoomType(d)" optionLabel="room_type" placeholder="Select Room Type"
                                    class="w-full" />
                            </td>
                            <td class="p-2">
                                <Dropdown v-model="d.room_id"
                                    :options="rooms.filter((r) => (r.room_type_id == d.room_type_id && (r.selected ?? 0) == 0) || (r.room_type_id == d.room_type_id && r.name == d.room_id))"
                                    optionValue="name" @change="OnSelectRoom" optionLabel="room_number"
                                    placeholder="Select Room" showClear filter class="w-full" />
                            </td>
                            <td class="p-2 w-12rem text-right">
                          
                                    <span @click="onOpenChangeRate($event, d)" class="text-right w-full color-purple-edoor text-md font-italic "><span class="link_line_action"><CurrencyFormat :value="d.rate" /> </span></span>

                               
                               
                  
                            </td>
                            <td class="p-2 w-5rem">
                                <InputNumber v-model="d.adult" inputId="stacked-buttons" showButtons :min="1" :max="100"
                                    class="child-adults-txt" />
                            </td>
                            <td class="p-2 w-5rem">
                                <InputNumber v-model="d.child" inputId="stacked-buttons" showButtons :min="0" :max="100"
                                    class="child-adults-txt" />
                            </td>

                            <td class="p-2 w-8rem">
                                <div class="p-inputtext-pt text-center border-1 border-white h-12">{{
                                    doc.reservation.room_night
                                }}</div>
                            </td>
                            <td class="p-2 w-10rem">
                                <div class="p-inputtext-pt text-end border-1 border-white h-12">
                                    <CurrencyFormat :value="(doc.reservation.room_night ?? 0) * (d.rate ?? 0)" />
                                </div>
                            </td>
                            <td v-if="doc.reservation_stay.length > 1" class="pl-2 text-end"><Button icon="pi pi-trash"
                                    @click="onDeleteStay(index)" class="tr-h__custom text-3xl h-12" aria-label="Filter" />
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            
            <Button @click="onAddRoom" icon="pi pi-plus" class="px-4 border-round-xl border-none" label="Add Room" /><br />
           
        </div>
        <!-- <hr class="my-3"> -->
        <div class="mt-3">
            <div>

                <label>Note</label><br />
                <Textarea v-model="doc.reservation.note" rows="5" placeholder="Note" cols="30"
                    class="w-full border-round-xl" />
            </div>
        </div>
        <OverlayPanel ref="op">
            <h1>Change Rate</h1>
            <Message>If you change room rate here. <br/>This room will stop automatically get rate from rate plan. <br/>
            To use rate from Rate Plan, click on button Use Rate Plan
            </Message>
         
                <InputNumber v-model="rate"    :min="0" 
                                      />

            <Button @click="onChangeRate">Change Rate</Button>
            <Button @click="onUseRatePlan">Use Rate Plan</Button>
        </OverlayPanel>

    </ComDialogContent>
</template>
<script setup>
import Calendar from 'primevue/calendar';
import OverlayPanel from 'primevue/overlaypanel';
import Message from 'primevue/message';
import ComReservationInputNight from './components/ComReservationInputNight.vue';
import { ref, inject, computed, onMounted } from "@/plugin"
import { useToast } from "primevue/usetoast";
const dialogRef = inject("dialogRef");
const toast = useToast();
const frappe = inject('$frappe')
const db = frappe.db();
const call = frappe.call();
const moment = inject("$moment")
const socket = inject("$socket")
const isSaving = ref(false)
const gv = inject("$gv")

const property = JSON.parse(localStorage.getItem("edoor_property"))
const room_types = ref([])
const rooms = ref([])
const working_day = ref({})
const selectedStay = ref({})
const rate = ref(0)
const op = ref();
const onOpenChangeRate = (event, stay) => {
    selectedStay.value = stay
    rate.value = JSON.parse(JSON.stringify(stay)).rate
    op.value.toggle(event);
}


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

const gender_list = ["Not Set", "Male", "Female"]

const total_pax = computed(() => {
    return doc.value.reservation.adult + doc.value.reservation.child;
})

const departureMinDate = computed(() => {
    return moment(doc.value.reservation.arrival_date).add(1, "days").toDate();
})

const onDateSelect = (date) => {


    doc.value.reservation.room_night = moment(doc.value.reservation.departure_date).diff(moment(doc.value.reservation.arrival_date), 'days')
    getRoomType()
    getRooms()
}


const getRoomType = () => {

    call.get("edoor.api.reservation.check_room_type_availability", {
        property: property.name,
        start_date: moment(doc.value.reservation.reservation_date).format("yyyy-MM-DD"),
        end_date: moment(doc.value.reservation.departure_date).format("yyyy-MM-DD"),
        rate_type: doc.value.reservation.rate_type,
        business_source: doc.value.reservation.business_source

    })
        .then((result) => {
            room_types.value = result.message;
            updateRate()
        }).catch((error) => {
            gv.showErrorMessage(error)
        })
}

const getRooms = () => {

    call.get("edoor.api.reservation.check_room_availability", {
        property: property.name,
        start_date: moment(doc.value.reservation.arrival_date).format("yyyy-MM-DD"),
        end_date: moment(doc.value.reservation.departure_date).format("yyyy-MM-DD")
    })
        .then((result) => {

            rooms.value = result.message;

        })
}

function onSelectedCustomer(event) {

    db.getDoc('Customer', event.value)
        .then((d) => doc.value.guest_info = d)
        .catch((error) => console.error(error));
}

const onRoomNightChanged = (event) => {

    doc.value.reservation.departure_date = moment(doc.value.reservation.arrival_date).add(event, "Days").toDate()
    getRoomType()
    getRooms()
}

const onAddRoom = () => {
    doc.value.reservation_stay.push(
        {
            // room_type_id: "RT-0005",
            // room_type: null,
            // room_id: "RM-0039",
            // room_number: null,

            adult: doc.value.reservation_stay[doc.value.reservation_stay.length - 1].adult,
            child: doc.value.reservation_stay[doc.value.reservation_stay.length - 1].child,
            room_type_id: doc.value.reservation_stay[doc.value.reservation_stay.length - 1].room_type_id,
            rate: doc.value.reservation_stay[doc.value.reservation_stay.length - 1].rate

        }
    )
}


const onSave = () => {
    isSaving.value = true
    const data = JSON.parse(JSON.stringify(doc.value))
    if (data.reservation.reservation_date) data.reservation.reservation_date = moment(data.reservation.reservation_date).format("yyyy-MM-DD")
    if (data.reservation.arrival_date) data.reservation.arrival_date = moment(data.reservation.arrival_date).format("yyyy-MM-DD")
    if (data.reservation.departure_date) data.reservation.departure_date = moment(data.reservation.departure_date).format("yyyy-MM-DD")
    if (data.guest_info.expired_date) data.guest_info.expired_date = moment(data.guest_info.expired_date).format("yyyy-MM-DD")


    call.get('edoor.api.reservation.add_new_fit_reservation', {
        doc: data
    })
        .then((result) => {

            toast.add({ severity: 'success', summary: 'Add New Reservation', detail: "Add new reservation successfully", life: 3000 })
            socket.emit("RefresheDoorDashboard", property.name);
            dialogRef.value.close(result.message);
            isSaving.value = false


        })
        .catch((error) => {

            const errors = error.exception.split(":")
            toast.add({ severity: 'error', summary: errors[0], detail: error.exception.replace(errors[0] + ":", ""), life: 3000 })
            isSaving.value = false
        });
}

onMounted(() => {
    call.get("edoor.api.frontdesk.get_working_day", {
        property: property.name
    }).then((result) => {
        working_day.value = (result.message)
        doc.value.reservation.reservation_date = moment(working_day.value.date_working_day).toDate()

        if (!dialogRef) {
            doc.value.reservation.arrival_date = moment(working_day.value.date_working_day).toDate()
            doc.value.reservation.departure_date = moment(working_day.value.date_working_day).add(1, 'days').toDate()

            getRoomType()
            getRooms()
        } else {
            console.log(dialogRef.value.data)
            if (dialogRef.value.data?.arrival_date) {
                doc.value.reservation.arrival_date = dialogRef.value.data.arrival_date
                doc.value.reservation.departure_date = dialogRef.value.data.departure_date
                doc.value.reservation_stay[0].room_type_id = dialogRef.value.data.room_type_id
                doc.value.reservation_stay[0].room_id = dialogRef.value.data.room_id
            } else {
                doc.value.reservation.arrival_date = moment(working_day.value.date_working_day).toDate()
                doc.value.reservation.departure_date = moment(working_day.value.date_working_day).add(1, 'days').toDate()

            }

            getRoomType()
            getRooms()
        }


        doc.value.reservation.room_night = moment(doc.value.reservation.departure_date).diff(moment(doc.value.reservation.arrival_date), 'days')

    })
});

const OnSelectRoom = () => {
    rooms.value.forEach(r => {
        r.selected = 0
    });

    doc.value.reservation_stay.forEach(r => {
        let room = rooms.value.find(x => x.name == r.room_id)
        if (room) {
            room.selected = 1
        }
    });

}
const onSelectRoomType = (stay) => {

    stay.room_id = null
    OnSelectRoom()
    updateRate()
}

const onDeleteStay = (index) => {
    doc.value.reservation_stay.splice(index, 1);
}

const updateRate = () => {
    doc.value.reservation_stay.filter(r => (r.is_manual_rate || false) == false).forEach(s => {
        const room_type = room_types.value.find(r => r.name == s.room_type_id)


        if (room_type) {

            s.rate = room_type.rate

        }

    });
}

const onBusinessSourceChange = (source) => {
  
    if (source) {
        doc.value.reservation.business_source = source.value
    }else {
        doc.value.reservation.business_source =null
    }

    //check if stay have not manully rate update
    if (doc.value.reservation_stay.filter(r => r.is_manual_rate == false).length > 0) {
        getRoomType()
    }

}
const onRateTypeChange = (rate_type) => {
    if (rate_type) {
        doc.value.reservation.rate_type = rate_type.value
    }

    //check if stay have not manully rate update
    if (doc.value.reservation_stay.filter(r => (r.is_manual_rate || false) == false).length > 0) {
        getRoomType()
    }
}

const onChangeRate = () => {
 
    selectedStay.value.rate = rate.value
    selectedStay.value.is_manual_rate = true
    op.value.hide();
}

const onUseRatePlan = () => {

    selectedStay.value.is_manual_rate = false;
    updateRate()
    op.value.hide();
}



</script>