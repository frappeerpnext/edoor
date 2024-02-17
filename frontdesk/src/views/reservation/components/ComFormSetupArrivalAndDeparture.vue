<template >
    <ComDialogContent @onOK="onSave" @onClose="onClose" :loading="isSaving">
        <div class="grid">
            <div class="col-12 lg:col-6">
                <div class="flex flex-wrap">
                    <div class="col-12">
                        <div class="flex items-center gap-2 ">
                            <Checkbox inputId="isarrivalmode" v-model="stay.require_pickup" :binary="true" :trueValue="1"
                                :falseValue="0" />
                            <label for="isarrivalmode" class="text-lg font-semibold cursor-pointer">Request Pickup</label>
                        </div>
                    </div>
                    <div class="flex flex-wrap " v-bind:class="{ 'pointer-events-none opacity-60': !stay.require_pickup }">
                        <div class="col-12">
                            <label for="num">Pickup Mode</label>
                            <ComSelect :clear="false" v-model="stay.arrival_mode" :default="true" placeholder="Arrival Mode"
                                doctype="Transportation Mode" class="auto__Com_Cus w-full" />
                        </div>
                        <div class="col-6">
                            <ComInputTime v-model="stay.pickup_time" label="Pickup Time" placeholder="Pickup Time" />
                        </div>
                        <div class="col-6">
                            <label for="arrivel_num">Arrival Flight Number</label>
                            <InputText v-model="stay.arrival_flight_number" id="arrivel_num" type="text"
                                class="p-inputtext-sm w-full" placeholder="Arrival Flight Number" :maxlength="50" />
                        </div>
                        <div class="col-6">
                            <label for="num">Pickup Location</label>
                            <ComSelect :clear="false" v-model="stay.pickup_location" :default="true"
                                placeholder="Pickup Location" doctype="Transportation Company"
                                class="auto__Com_Cus w-full" />
                        </div>
                        <div class="col-6">
                            <label for="arrival_driver">Pickup Driver</label>
                            <ComAutoComplete :clear="false" v-model="stay.pickup_driver" isAddNew @onAddNew="onAddDriver('pickup')"
                                placeholder="Pickup Driver" doctype="Drivers" class="auto__Com_Cus w-full" />
                        </div>
                        <div class="col-12">
                            <label for="arrival_none">Note</label>
                            <Textarea id="arrival_none" v-model="stay.pickup_note" placeholder=" Arrival Note"
                                class="w-full" rows="5" />
                        </div>
                    </div>

                </div>
            </div>
            <div class="col-12 lg:col-6">
                <div class="flex flex-wrap">
                    <div class="col-12">
                        <div class="flex items-center gap-2">
                            <Checkbox inputId="isdeparturemode" v-model="stay.require_drop_off" :binary="true"
                                :trueValue="1" :falseValue="0" />
                            <label for="isdeparturemode" class="text-lg font-semibold cursor-pointer">Request Drop
                                Off</label>
                        </div>
                    </div>
                    <div class="flex flex-wrap "
                        v-bind:class="{ 'pointer-events-none opacity-60': !stay.require_drop_off }">
                        <div class="col-12">
                            <label for="num">Drop Off Mode</label>
                            <ComSelect :clear="false" v-model="stay.departure_mode" :default="true"
                                placeholder="Arrival Mode" doctype="Transportation Mode" class="auto__Com_Cus w-full" />
                        </div>
                        <div class="col-6">
                            <ComInputTime v-model="stay.drop_off_time" label="Drop Off Time" placeholder="Drop Off Time" />
                        </div>
                        <div class="col-6">
                            <label for="departure_flight_number">Departure Flight Number</label>
                            <InputText id="departure_flight_number" type="text" v-model="stay.departure_flight_number"
                                class="p-inputtext-sm w-full" placeholder="Departure Flight Number" :maxlength="50" />
                        </div>
                        <div class="col-6">
                            <label>Drop Off Location</label>
                            <ComSelect :clear="false" v-model="stay.drop_off_location" :default="true"
                                placeholder="Drop Off Location" doctype="Transportation Company"
                                class="auto__Com_Cus w-full" />
                        </div>
                        <div class="col-6">
                            <label>Drop Off Driver</label>
                            <ComAutoComplete :clear="false" v-model="stay.drop_off_driver" isAddNew @onAddNew="onAddDriver('dropoff')"
                                placeholder="Drop Off Driver" doctype="Drivers" class="auto__Com_Cus w-full" />
                        </div>
                        <div class="col-12">
                            <label for="arrival_none">Note</label>
                            <Textarea id="arrival_none" v-model="stay.drop_off_note" placeholder="Departure Note"
                                class="w-full" rows="5" />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </ComDialogContent>
</template>
<script setup>
import { ref, inject, useDialog,postApi, onMounted, useToast } from "@/plugin";

import ComAddDriver from "../../other/driver/ComAddDriver.vue";

const dialogRef = inject("dialogRef");
const isSaving = ref(false)
const stay = ref({})
const stays = ref()
const rs = inject('$reservation_stay');
const dialog = useDialog()
const toast = useToast()
 
function onSave() { 
    isSaving.value = true;
    postApi("reservation.update_pickup_and_drop_off",{
        stays:stays.value,
        data:stay.value
    })
        .then((doc) => {
            isSaving.value = false
            if (rs?.reservationStay?.name && doc?.message){
                rs.reservationStay = JSON.parse(JSON.stringify(doc.message))
            }
            dialogRef.value.close("refresh");
            window.postMessage({"action":"Dashboard"},"*")
            window.postMessage({action:"ReservationStayDetail"},"*")
            window.postMessage({action:"ReservationDetail"},"*")
            window.postMessage({action:"TodaySummary"},"*")
            window.postMessage({action:"Reports"},"*")
        })
        .catch((error) => {
            isSaving.value = false;
        })
}
function onAddDriver(type) {
    dialog.open(ComAddDriver, {
        props: {
            header: `Add Driver`,
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            const data = options.data;
            if(type=='pickup')
                stay.value.pickup_driver = data.name
            else
                stay.value.drop_off_driver = data.name
        }
    })
}

const onClose = () => {
    dialogRef.value.close()
}

onMounted(()=>{
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    stays.value = dialogRef.value.data?.stays
    postApi(
        "reservation.get_pickup_and_drop_off_data",
        {
            stays:dialogRef.value.data?.stays
        },
        "",
        false
    ).then((result)=>{
        stay.value = result.message
    })
    
})


</script>
<style ></style>