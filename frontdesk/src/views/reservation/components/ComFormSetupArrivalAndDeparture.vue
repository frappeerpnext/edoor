<template >
    <ComDialogContent @onOK="onSave" hideButtonClose :loading="isSaving">
        <div class="grid">
            <div class="col-6">
                <div class="flex flex-wrap">
                    <div class="col-12">
                        <div class="flex items-center gap-2 ">
                            <Checkbox inputId="isarrivalmode" v-model="stay.require_pickup" :binary="true" :trueValue="1"
                                :falseValue="0" />
                            <label for="isarrivalmode" class="text-lg font-semibold cursor-pointer">Arrival Pickup</label>
                        </div>
                    </div>
                    <div class="col-12">
                        <label for="num"> Arrival Mode</label>
                        <ComSelect :clear="false" v-model="stay.arrival_mode" :default="true" placeholder="Arrival Mode"
                            doctype="Transportation Mode" class="auto__Com_Cus w-full" />
                    </div>
                    <div class="col-6">
                        <label for="arrival_pickup_time" class="block"> Pickup Time </label>
                        <Calendar id="arrival_pickup_time" class="w-full" placeholder="Pickup time"
                            v-model="stay.pickup_time" timeOnly />
                    </div>
                    <div class="col-6">
                        <label for="arrivel_num"> Arrival Flight Number</label>
                        <InputText v-model="stay.arrival_flight_number" id="arrivel_num" type="text"
                            class="p-inputtext-sm w-full" placeholder=" Arrival Flight Number" :maxlength="50" />
                    </div>
                    <div class="col-6">
                        <label for="num">Pickup Location</label>
                        <ComSelect :clear="false" v-model="stay.pickup_location" :default="true"
                            placeholder="Pickup Location" doctype="Transportation Company" class="auto__Com_Cus w-full" />
                    </div>
                    <div class="col-6">
                        <label for="arrival_driver">Pickup Driver</label>
                        <ComAutoComplete :clear="false" v-model="stay.driver" placeholder="Pickup Driver" doctype="Drivers"
                            class="auto__Com_Cus w-full" />
                    </div>
                    <div class="col-12">
                        <label for="arrival_none">Note</label>
                        <Textarea id="arrival_none" v-model="stay.pickup_none" placeholder=" Arrival Note" class="w-full"
                            rows="5" />
                    </div>


                </div>
            </div>
            <div class="col-6">
                <div class="flex flex-wrap">
                    <div class="col-12">
                        <div class="flex items-center gap-2">
                            <Checkbox inputId="isdeparturemode" v-model="stay.require_drop_off" :binary="true"
                                :trueValue="1" :falseValue="0" />
                            <label for="isdeparturemode" class="text-lg font-semibold cursor-pointer">Departure
                                Pickup</label>
                        </div>
                    </div>
                    <div class="col-12">
                        <label for="num"> Departure Mode</label>
                        <ComSelect :clear="false" v-model="stay.departure_mode" :default="true" placeholder="Arrival Mode"
                            doctype="Transportation Mode" class="auto__Com_Cus w-full" />
                    </div>
                    <div class="col-6">
                        <label for="departure_pickup_time" class="block"> Pickup Time </label>

                        <Calendar id="arrival_pickup_time" class="w-full" placeholder="Pickup time" v-model="stay.departure_time" timeOnly/>
                    </div>
                    <div class="col-6">
                        <label for="num">Departure Flight Number</label>
                        <InputText id="num" type="text" class="p-inputtext-sm w-full" placeholder="Departure Flight Number"
                            :maxlength="50" />
                    </div>
                    <div class="col-6">
                        <label for="num"> Pickup Location</label>
                        <ComSelect :clear="false" v-model="stay.drop_off_location" :default="true"
                            placeholder="Pickup Location" doctype="Transportation Company" class="auto__Com_Cus w-full" />
                    </div>
                    <div class="col-6">
                        <label for="num">Pickup Driver</label>
                        <ComAutoComplete :clear="false" v-model="stay.drop_off_driver" placeholder="Pickup Driver"
                            doctype="Drivers" class="auto__Com_Cus w-full" />
                    </div>
                    <div class="col-12">
                        <label for="arrival_none">Note</label>
                        <Textarea id="arrival_none" placeholder="Departure Note" class="w-full" v-model="stay.drop_off_none"
                            rows="5" />
                    </div>
                </div>
            </div>
        </div>
    </ComDialogContent>
</template>
<script setup>
import { ref, inject } from "@/plugin";
import ComReservationStayPanel from './ComReservationStayPanel.vue';
import { useToast } from "primevue/usetoast";
const rs = inject("$reservation_stay")
const gv = inject("$gv") 
const dialogRef = inject("dialogRef");
const toast = useToast();
const isSaving = ref(false) 
const frappe = inject("$frappe")
const db = frappe.db()
const stay = ref(JSON.parse(JSON.stringify(rs.reservationStay)))
function onSave() {
    isSaving.value = true;
    db.updateDoc("Reservation Stay", stay.value.name, stay.value)
        .then((doc) => {
            stay.value = JSON.parse(JSON.stringify(doc))
            rs.reservationStay = doc
            toast.add({ severity: 'success', summary: 'Update Transportation Mode', detail: "Update transportation mode successfully", life: 3000 })
            // dialogRef.value.close();
            isSaving.value = false;
        })
        .catch((error) => {
            gv.showErrorMessage(error)
            isSaving.value = false;
        })

}

</script>
<style ></style>