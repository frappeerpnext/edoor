<template>
    <ComOverlayPanelContent style="width: 40rem;" :loading="loading" @onSave="onSave" @onCancel="onClose">
        <div :class="loading ? 'pointer-events-none opacity-90' : ''">
            <h1>Group Change Stay</h1>
            <Message>Group change stay is affect only active reservation. </Message>
            <div class="grid py-2 wp-number-cus">
                <div class="col-6">
                    <label>Arrival Date</label>
                    <Calendar panelClass="no-btn-clear" :selectOtherMonths="true" showIcon v-model="data.arrival_date"
                        showButtonBar :min-date="new Date(moment(data.min_date))" @update:modelValue="onStartDate"
                        dateFormat="dd-mm-yy" class="w-full" />
                </div>
                <div class="col-6">
                    <label>Departure Date</label>
                    <Calendar panelClass="no-btn-clear" showButtonBar selectOtherMonths showIcon
                        v-model="data.departure_date" :selectOtherMonths="true"
                        :min-date="new Date(moment(data.arrival_date).add(1, 'days'))" @update:modelValue="onEndDate"
                        dateFormat="dd-mm-yy" class="w-full" />
                </div>

                <div class="col-6">
                    <label>Nights</label>
                    <InputNumber v-model="data.room_nights" @update:modelValue="onNight($event)" inputId="stacked-buttons"
                        showButtons :min="1" class="w-full nig_in-put" />
                </div>
                <div class="col-12">
                    <div class="flex flex-wrap gap-3 mt-2 ">
                        <div class="flex align-items-center ">
                            <RadioButton inputId="stay_rate" name="generate_new_stay_rate_by" value="stay_rate"
                                v-model="data.generate_new_stay_rate_by" />
                            <label for="stay_rate" class="ml-2">Generate New Stay Rate from Last First/Last Stay
                                Rate</label>
                        </div>
                        <div class="flex align-items-center">
                            <RadioButton inputId="rate_plan" name="generate_new_stay_rate_by" value="rate_plan"
                                v-model="data.generate_new_stay_rate_by" />
                            <label for="rate_plan" class="ml-2">Generate New Stay Rate from Rate Type</label>
                        </div>
                    </div>
                </div>
            </div>
            <div>
                <label>Note</label><br />
                <Textarea rows="2" autoResize placeholder="Note" cols="30" class="w-full border-round-xl"
                    v-model="data.note" />
            </div>
        </div>
    </ComOverlayPanelContent>
</template>
<script setup>
import { ref, inject, postApi, useToast } from "@/plugin"

const rs = inject("$reservation")
const moment = inject("$moment")
const loading = ref(false)
const emit = defineEmits("onClose")
const toast = useToast();

const workingDay = JSON.parse(localStorage.getItem("edoor_working_day"))
const data = ref({

    min_date: workingDay.date_working_day,
    can_arrival: (moment(workingDay.date_working_day).isAfter(rs.reservation.arrival_date) ? true : false),
    arrival_date: moment(rs.reservation.arrival_date).toDate(),
    departure_date: moment(rs.reservation.departure_date).toDate(),
    arrival_time: moment(rs.reservation.arrival_date + " " + rs.reservation.arrival_time).toDate(),
    departure_time: moment(rs.reservation.departure_date + " " + rs.reservation.departure_time).toDate(),
    generate_new_stay_rate_by: "stay_rate"
})
data.value.room_nights = moment(data.value.departure_date).diff(moment(data.value.arrival_date), 'days')

function onClose() {
    emit('onClose')
}
function onNight(newValue) {
    data.value.departure_date = moment(data.value.arrival_date).add(newValue, 'days').toDate()
}
function onEndDate(newValue) {
    newValue = moment.utc(moment(newValue).format("YYYY-MM-DD")).toDate()
    data.value.departure_date = newValue
    data.value.room_nights = moment(data.value.departure_date).diff(moment(data.value.arrival_date), 'days')
}
function onStartDate(newValue) {
    if (moment(newValue).isSame(data.value.departure_date) || moment(newValue).isAfter(data.value.departure_date)) {
        data.value.departure_date = moment(newValue).add(1, 'days').toDate()
    }
    data.value.room_nights = moment(data.value.departure_date).diff(moment(newValue), 'days')
}
function onSave() {
    loading.value = true
    const active_reservations = rs.roomList.filter(r => r.is_active_reservation == 1 && r.allow_user_to_edit_information == 1)

    if (active_reservations.length == 0) {
        toast.add({ severity: 'warn', summary: "Change Stay", detail: "There is no active reservation to change stay", life: 5000 })
        loading.value = false
        return
    }
    postApi("group_operation.group_change_stay", {
        data: {
            stays: active_reservations.map(r => r.name),
            arrival: moment(data.value.arrival_date).format("YYYY-MM-DD"),
            departure: moment(data.value.departure_date).format("YYYY-MM-DD"),
            note: data.value.note,
            generate_new_stay_rate_by: data.value.generate_new_stay_rate_by,
            property: window.property_name,
            reservation: rs.reservation.name
        }
    }, '', false).then((result) => {
        if (result.message.length < active_reservations.length) {
            toast.add({ severity: 'success', summary: "Update Successfully", detail: '', life: 5000 })
        }
        result.message.forEach(x => {
            toast.add({ severity: 'warn', summary: "Reservation Stay #" + x.reservation_stay, detail: x.message, life: 7000 })
        });
        loading.value = false

        emit("onClose")
        window.socket.emit("ReservationList", { property: window.property_name })
        window.socket.emit("Reports", window.property_name)
        window.socket.emit("ComIframeModal", window.property_name)
        window.postMessage({"action":"Dashboard"},"*")
        window.socket.emit("ReservationStayList", { property: window.property_name })
        window.postMessage({"action":"Frontdesk"},"*")
        window.socket.emit("ReservationStayDetail", { reservation_stay: active_reservations.map(r => r.name) })
        window.socket.emit("ReservationDetail", rs.reservation.name);

    }).catch((err) => {
        loading.value = false
    })


}
</script>