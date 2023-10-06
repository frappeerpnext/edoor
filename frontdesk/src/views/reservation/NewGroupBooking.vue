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
                                    placeholder="Reservation Date" dateFormat="dd-mm-yy" showIcon showButtonBar
                                    :selectOtherMonths="true" />
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
                        <div class="grid">
                            <div class="col-12 lg:col-5">
                                <div class="pt-2">
                                    <label>Group Code</label><br />
                                    <InputText v-model="doc.reservation.group_code" placeholder="Group Code"
                                        class="w-full" />
                                </div>
                            </div>
                            <div class="col-12 lg:col-5">
                                <div class="pt-2">
                                    <label>Group Name</label><br />
                                    <InputText v-model="doc.reservation.group_name" placeholder="Group Name"
                                        class="w-full" />

                                </div>
                            </div>
                            <div class=" col-12 lg:col-2">
                                <div class="pt-2 rounded-lg cursor-pointer" style="height: 44px;">
                                    <label class="white-space-nowrap overflow-hidden">Group Color</label>
                                    <div class="w-full h-full rounded-lg border-1" style="border-color: #a0bde0;"
                                        @click="toggleColor" :style="{ background: doc.reservation.group_color }"></div>
                                </div>
                                <OverlayPanel ref="opColor">
                                    <ComColorPicker v-model="doc.reservation.group_color" />
                                </OverlayPanel>
                            </div>
                        </div>
                        <div class="grid m-0">
                            <div class="arr_wfit col px-0">
                                <label>Arrival<span class="text-red-500">*</span></label><br />
                                <Calendar class="p-inputtext-sm depart-arr w-full border-round-xl"
                                    v-model="doc.reservation.arrival_date" placeholder="Arrival Date"
                                    @date-select="onDateSelect" dateFormat="dd-mm-yy" showIcon showButtonBar
                                    :selectOtherMonths="true" />
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
                                    :minDate="departureMinDate" showButtonBar showIcon :selectOtherMonths="true" />
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
                                        class="auto__Com_Cus w-full" :filters="{ property: property.name }" />
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
                        
                        <div class=" flex justify-end">
                            <div class="flex justify-end gap-3 pt-2">
                                <div>
                                    <div class="text-center">
                                        <label class="text-center">Adult (Per Room)</label><br>
                                    </div>
                                    <InputNumber
                                        v-tippy="'Please enter number of adult per room here. Total adult will be calculate  from each reservation stay room in this reservation. You can update number of adult later in Reservation Stay Detail'"
                                        v-model="doc.reservation.adult" inputId="stacked-buttons" showButtons :min="1"
                                        :max="100" class="child-adults-txt" />
                                </div>
                                <div>
                                    <div class="text-center">
                                        <label class="text-center">Child (Per Room)</label><br>
                                    </div>
                                    <InputNumber
                                        v-tippy="'Please enter number of child per room here. Total child will be calculate  from each reservation stay room in this reservation. You can update number of child later in Reservation Stay Detail'"
                                        v-model="doc.reservation.child" inputId="stacked-buttons" showButtons :min="0"
                                        :max="100" class="child-adults-txt" />
                                </div>
                            </div>
                        </div>
                        <div class="w-full flex justify-end mt-4 gap-3">
                            <div class="flex align-items-center">
                                <label
                                    v-tippy="'If you tick this check box, room charge will post to master folio of master room when check in and run night audit'"
                                    for="paidby" class="font-medium cursor-pointer me-2">Paid by Master Room</label>
                                <Checkbox
                                    v-tippy="'If you tick this check box, room charge will post to master folio of master room when check in and run night audit'"
                                    class="" inputId="paidby" v-model="doc.reservation.paid_by_master_room" :binary="true"
                                    :trueValue="1" :falseValue="0" />
                            </div>
                            <div class="flex align-items-center">
                                <label
                                    v-tippy="'If you tick this check box, transaction folio can post to city ledger when check in and run night audit'"
                                    for="paidcity" class="font-medium cursor-pointer me-2">Allow Post to City Ledger</label>
                                <Checkbox
                                    v-tippy="'If you tick this check box, transaction folio can post to city ledger when check in and run night audit'"
                                    class="" inputId="paidcity" v-model="doc.reservation.allow_post_to_city_ledger"
                                    :binary="true" :trueValue="1" :falseValue="0" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col">
                <div class="bg-card-info border-round-xl p-3 h-full">
                    <h1 class="text-lg line-height-4 font-bold mb-2">Guest Information</h1>
                    <div>
                        <div class="w-full n__re-custom">

                            <label>Return Guest</label>
                            <ComAutoComplete isIconSearch v-model="doc.reservation.guest" class="pb-2"
                                placeholder="Return Guest" doctype="Customer" @onSelected="onSelectedCustomer" />
                            <hr class="my-3" />
                            <div class="grid">
                                <div class="col-12 pt-2">
                                    <label>New Guest Name<span class="text-red-500">*</span></label><br />
                                    <InputText type="text" class="p-inputtext-sm w-full" placeholder="New Guest Name"
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
                                    <label>Expire Date</label><br />
                                    <Calendar class="p-inputtext-sm w-full" v-model="doc.guest_info.expired_date"
                                        placeholder="ID Expire Date" dateFormat="dd-mm-yy" showIcon
                                        :selectOtherMonths="true" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="grid pt-2" v-if="room_tax && (room_tax.tax_1_rate + room_tax.tax_2_rate + room_tax.tax_3_rate) > 0">
            <div class="col">
                <div class="bg-card-info border-round-xl p-3 h-full">
                    <div class="flex gap-2 align-items-center relative my-3" style="width: 12.7rem;">
                        <label for="include-tax" class="font-medium cursor-pointer">Rate Include Tax</label>
                        <span class="absolute right-0 w-full">
                            <Checkbox input-id="rate_tax" class="w-full flex justify-end"
                                v-model="doc.tax_rule.rate_include_tax" :binary="true" trueValue="Yes" falseValue="No" />
                        </span>
                    </div>
                    <div class="">
                        <div class="flex gap-3 flex-wrap">
                            <div class="flex gap-3 relative">
                                <label for="tax-1-rate"
                                    class="font-medium flex align-items-center h-full">{{ room_tax.tax_1_name }}
                                    {{ room_tax.tax_1_rate }}%</label>
                                <div class="p-inputtext-pt text-center border-1 border-white flex w-16rem">
                                    <span class="w-full">
                                        <Checkbox input-id="tax-1-rate" class="w-full" v-model="useTax.use_tax_1"
                                            @input="onUseTax1Change" :binary="true" />
                                    </span>
                                    <div class="white-space-nowrap">
                                        <CurrencyFormat :value="totalTax1Amount" />
                                    </div>
                                </div>
                            </div>
                            <div class="flex gap-3 relative">
                                <label for="tax-2-rate"
                                    class="font-medium flex align-items-center h-full">{{ room_tax.tax_2_name }}
                                    {{ room_tax.tax_2_rate }}%</label>
                                <div class="p-inputtext-pt text-center border-1 border-white flex w-16rem">
                                    <span class="w-full">
                                        <Checkbox input-id="tax-2-rate" class="w-full" v-model="useTax.use_tax_2"
                                            @input="onUseTax2Change" :binary="true" />
                                    </span>
                                    <div class="white-space-nowrap">
                                        <CurrencyFormat :value="totalTax2Amount" />
                                    </div>
                                </div>
                            </div>
                            <div class="flex gap-3 relative">
                                <label for="tax-3-rate"
                                    class="font-medium flex align-items-center h-full">{{ room_tax.tax_3_name }}
                                    {{ room_tax.tax_3_rate }}%</label>
                                <div class="p-inputtext-pt text-center border-1 border-white flex w-16rem">
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

        <div class="bg-card-info border-round-xl mt-2 p-3 add-room-reserv">
            <div class="n__re-custom">
                <div class="w-full flex justify-end mt-2">
                <label for="auto_assign_room" class="mr-3 cursor-pointer"
                    v-tippy="'When the checkbox is checked, the system will automatically assign a room to the reservation. The room that is automatically assigned will be one that is available for the entire stay.'">Automatically
                    assign room</label>
                <Checkbox
                    v-tippy="'When the checkbox is checked, the system will automatically assign a room to the reservation. The room that is automatically assigned will be one that is available for the entire stay.'"
                    inputId="auto_assign_room" v-model="doc.auto_assign_room" :binary="true" />

            </div>
            <hr class="my-3">
                <table class="w-full">
                    <thead>
                        <tr>
                            <th class="text-left pb-1">
                                <label>Room Type</label>
                            </th>
                            <th class="text-center pb-1">
                                <label class="px-2">Total Rooms</label>
                            </th>
                            <th class="text-center pb-1">
                                <label class="text-center px-2">Total Room Available</label>
                            </th>
                            <th class="text-right w-15rem pb-1">
                                <label class="text-right px-2">Rate</label>
                            </th>

                            <th class="text-right w-15rem pb-1">
                                <label class="text-right px-2">Tax</label>
                            </th>
                            <th class="text-right w-15rem pb-1">
                                <label class="text-right px-2">Amount</label>
                            </th>
                            <th class="pb-1">
                                <label class="text-center px-2">No. of Room</label>
                            </th>
                        </tr>
                    </thead>
                    <tbody>


                        <tr v-for="(  d, index  ) in   room_types" :key="index">

                            <td class="pr-2">
                                <div
                                    class="w-full box-input px-3 border-round-lg overflow-hidden text-overflow-ellipsis whitespace-nowrap border border-white p-inputtext-pt">
                                    {{ d.room_type }}
                                </div>
                            </td>
                            <td class="padding-list-booking-group text-center">
                                <div
                                    class="w-full box-input px-3 border-round-lg overflow-hidden text-overflow-ellipsis whitespace-nowrap border border-white p-inputtext-pt">
                                    {{ d.total_room }}
                                </div>
                            </td>
                            <td class="padding-list-booking-group w-12rem text-center">
                                <div :class="d.total_vacant_room < 0 ? 'text-red-500' : ''"
                                    class="w-full box-input px-3 border-round-lg overflow-hidden text-overflow-ellipsis whitespace-nowrap border border-white p-inputtext-pt">
                                    {{ d.total_vacant_room }}
                                </div>
                            </td>
                            <td class="padding-list-booking-group w-12rem text-center">
                                <div
                                    class="w-full box-input px-3 border-round-lg overflow-hidden text-overflow-ellipsis whitespace-nowrap border border-white p-inputtext-pt">
                                    <span @click="onOpenChangeRate($event, d)"
                                        class="text-right w-full color-purple-edoor text-md font-italic ">

                                        <div v-tooltip.top="(d.is_manual_rate) ? 'Manual Rate' : 'Rate Plan'"
                                            class="link_line_action flex justify-between">
                                            <div class="text-left inline">
                                                <span class="text-sm" v-if="d.is_manual_rate"> (Manual) </span>
                                                <span class="text-sm" v-else>(Plan)</span>
                                            </div>
                                            <CurrencyFormat :value="d.new_rate" />
                                        </div>
                                    </span>
                                </div>
                            </td>

                            <td class="padding-list-booking-group w-12rem text-right">
                                <div
                                    class="w-full box-input px-3 border-round-lg overflow-hidden text-overflow-ellipsis whitespace-nowrap border border-white p-inputtext-pt">
                                    <CurrencyFormat :value="roomRateTax(d)" />
                                </div>
                            </td>
                            <td class="padding-list-booking-group w-12rem text-right">
                                <div
                                    class="w-full box-input px-3 border-round-lg overflow-hidden text-overflow-ellipsis whitespace-nowrap border border-white p-inputtext-pt">
                                   
                                    <div v-if="doc.tax_rule.rate_include_tax == 'Yes'">
                                      
                                        <CurrencyFormat
                                            :value="((d.new_rate) * doc.reservation.room_night) * d.total_selected_room" />
                                    </div>
                                    <div v-else>
                          
                                        <CurrencyFormat
                                            :value="roomRateTax(d) + (d.new_rate * doc.reservation.room_night * d.total_selected_room)" />
                                    </div>
                                </div>
                            </td>
                            <td class="padding-list-booking-group w-12rem text-center">
                                <div class="relative ">
                                    <div :class="d.total_selected_room > d.total_vacant_room ? 'tip-over-booking' : 'hidden'" v-tippy="d.room_type+' OverBooking'">Overbooking</div>
                                <InputNumber :class="d.total_selected_room > d.total_vacant_room ? 'over-booking-box' : ''" v-model="d.total_selected_room" inputId="stacked-buttons" showButtons :min="0"
                                    :max="d.total_vacant_room + (setting.enable_over_booking==1?1000:0)" class="child-adults-txt" />
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>

            </div>
        </div>
        <div class="mt-3">
            <div>
                <label>Note</label><br />
                <Textarea v-model="doc.reservation.note" rows="5" placeholder="Note" cols="30"
                    class="w-full border-round-xl" />
            </div>
        </div>

        <OverlayPanel ref="op">
            <ComReservationStayChangeRate v-model="rate" @onClose="onClose" @onUseRatePlan="onUseRatePlan"
                @onChangeRate="onChangeRate" />
        </OverlayPanel>
        <template #footer-right>



            <Button class="border-none" @click="onSave(true)" v-if="!doc.auto_assign_room">Create Reservation & Assign
                Room</Button>
        </template>
    </ComDialogContent>
</template>
<script setup>
import { ref, inject, computed, onMounted, postApi, getApi, getDoc } from "@/plugin"
import ComReservationInputNight from './components/ComReservationInputNight.vue';

import ComReservationStayChangeRate from "./components/ComReservationStayChangeRate.vue"



import { useToast } from "primevue/usetoast";
const dialogRef = inject("dialogRef");
const toast = useToast();
const moment = inject("$moment")
const isSaving = ref(false)
const gv = inject("$gv")

const opColor = ref();
const toggleColor = (event) => {
    opColor.value.toggle(event);
}

const property = JSON.parse(localStorage.getItem("edoor_property"))
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const room_types = ref([])
const rooms = ref([])
const working_day = ref({})
const selectedStay = ref({})
const rate = ref(0)
const op = ref();
const group_color = ref("#" + generateRandomColor())
const room_tax = ref()

const onOpenChangeRate = (event, stay) => {

    selectedStay.value = stay
    rate.value = JSON.parse(JSON.stringify(stay)).new_rate
    op.value.toggle(event);
}



const doc = ref({
    reservation: {
        doctype: "Reservation",
        property: property.name,
        reservation_type: "GIT",
        arrival_time: '12:00:00',
        departure_time: '12:00:00',
        adult: 1,
        child: 0,
        reservation_status: 'Reserved',
        tax_rule: room_tax.value?.name,
        paid_by_master_room: 1,
        group_code: "",
        group_name: "",
        auto_assign_room: false,
        group_color: group_color.value,
        allow_post_to_city_ledger: 1
    },
    guest_info: {
        "doctype": "Customer",
        "gender": "Not Set"
    },
    reservation_stay: [{ rate: 0, adult: 1, child: 0, is_manual_rate: false, is_master: 0 },],
    tax_rule: {
        rate_include_tax: room_tax.value?.is_rate_include_tax ? "Yes" : "No",
        tax_1_rate: room_tax.value?.tax_1_rate || 0,
        tax_2_rate: room_tax.value?.tax_2_rate || 0,
        tax_3_rate: room_tax.value?.tax_3_rate || 0,
    }
})

const gender_list = ["Not Set", "Male", "Female"]

const useTax = computed(() => {
    return {
        use_tax_1: (room_tax.value?.tax_1_rate || 0) > 0,
        use_tax_2: (room_tax.value?.tax_2_rate || 0) > 0,
        use_tax_3: (room_tax.value?.tax_3_rate || 0) > 0
    }

})

const roomRateTax = ref((d) => {

    const tax_1_amount = getTax1Amount((d.new_rate * d.total_selected_room) * doc.value.reservation.room_night)
    const tax_2_amount = getTax2Amount((d.new_rate * d.total_selected_room) * doc.value.reservation.room_night)
    const tax_3_amount = getTax3Amount((d.new_rate * d.total_selected_room) * doc.value.reservation.room_night)
    return tax_1_amount + tax_2_amount + tax_3_amount
});
const rateTax = ref((d) => {
    if (room_tax.value) {
        if (doc.value.tax_rule.rate_include_tax == 'Yes') {
            return gv.getRateBeforeTax((d.new_rate || 0), room_tax.value, doc.value.tax_rule.tax_1_rate, doc.value.tax_rule.tax_2_rate, doc.value.tax_rule.tax_3_rate)
        } else {
            return d.new_rate
        }
    } else {
        return 0
    }
})

function getTax1Amount(rate) {

    if (room_tax.value) {
        if (room_tax.value.calculate_tax_1_after_discount == 0 || doc.value.tax_rule.rate_include_tax == 'Yes') {

            rate = gv.getRateBeforeTax((rate || 0), room_tax.value, doc.value.tax_rule.tax_1_rate, doc.value.tax_rule.tax_2_rate, doc.value.tax_rule.tax_3_rate)

        } else {
            rate = rate

        }


        return (rate || 0) * (doc.value.tax_rule.tax_1_rate / 100 || 0)
    } else {

        return 0
    }
}
function getTax2Amount(rate) {

    if (room_tax.value) {
        if (room_tax.value.calculate_tax_1_after_discount == 0 || doc.value.tax_rule.rate_include_tax == 'Yes') {
            rate = rate = gv.getRateBeforeTax((rate || 0), room_tax.value, doc.value.tax_rule.tax_1_rate, doc.value.tax_rule.tax_2_rate, doc.value.tax_rule.tax_3_rate)

        } else {
            rate = rate

        }
        if (room_tax.value.calculate_tax_2_after_adding_tax_1 == 0 || (rate * (doc.value.tax_rule.tax_1_rate / 100)) == 0) {
            rate = rate
        } else { rate = rate + (rate * (doc.value.tax_rule.tax_1_rate / 100)) }
        console.log("tax 2 rate amount ", rate)
        console.log("tax 2 rate ", doc.value.tax_rule.tax_2_rate)
        console.log((rate || 0) * (doc.value.tax_rule.tax_2_rate / 100 || 0))
        return (rate || 0) * (doc.value.tax_rule.tax_2_rate / 100 || 0)
    } else {
        return 0
    }
}
function getTax3Amount(rate) {
    if (room_tax.value) {
        if (room_tax.value.calculate_tax_1_after_discount == 0 || doc.value.tax_rule.rate_include_tax == 'Yes') {
            rate = rate = gv.getRateBeforeTax((rate || 0), room_tax.value, doc.value.tax_rule.tax_1_rate, doc.value.tax_rule.tax_2_rate, doc.value.tax_rule.tax_3_rate)

        } else {
            rate = rate

        }
        if (room_tax.value.calculate_tax_2_after_adding_tax_1 == 0 || (rate * (doc.value.tax_rule.tax_1_rate / 100)) == 0) {
            rate = rate
        } else { rate = rate + (rate * (doc.value.tax_rule.tax_1_rate / 100)) }
        if (room_tax.value.calculate_tax_3_after_adding_tax_2 == 0 || (rate * (doc.value.tax_rule.tax_2_rate / 100)) == 0) {
            rate = rate
        } else { rate = rate + (rate * (doc.value.tax_rule.tax_2_rate / 100)) }
        return (rate || 0) * (doc.value.tax_rule.tax_3_rate / 100 || 0)
    } else {
        return 0
    }
}

const totalTax1Amount = computed(() => {
    let amount = 0
    room_types.value.filter(x => x.total_selected_room > 0).forEach(r => {
        console.log(r.new_rate, "===", r.total_selected_room)
        amount = amount + (getTax1Amount(r.new_rate * r.total_selected_room))
    });
    return amount * doc.value.reservation.room_night
})
const totalTax2Amount = computed(() => {
    let amount = 0
    room_types.value.filter(x => x.total_selected_room > 0).forEach(r => {
        amount = amount + (getTax2Amount(r.new_rate * r.total_selected_room))
    });
    return amount * doc.value.reservation.room_night
})
const totalTax3Amount = computed(() => {
    let amount = 0
    room_types.value.filter(x => x.total_selected_room > 0).forEach(r => {
        amount = amount + (getTax3Amount(r.new_rate * r.total_selected_room))
    });
    return amount * doc.value.reservation.room_night
})



const total_pax = computed(() => {
    return doc.value.reservation.adult + doc.value.reservation.child;
})

const departureMinDate = computed(() => {
    return moment(doc.value.reservation.arrival_date).add(1, "days").toDate();
})

const onDateSelect = (date) => {
    let arrival_date = moment(doc.value.reservation.arrival_date).format("YYYY-MM-DD")
    arrival_date = moment(arrival_date).toDate()

    let departure_date = moment(doc.value.reservation.departure_date).format("YYYY-MM-DD")
    departure_date = moment(departure_date).toDate()


    if (arrival_date >= departure_date) {
        doc.value.reservation.departure_date = moment(doc.value.reservation.arrival_date).add(1, 'days').toDate()

    }
    doc.value.reservation.room_night = moment(doc.value.reservation.departure_date).diff(moment(doc.value.reservation.arrival_date), 'days')
    getRoomType()
}

const getRoomType = () => {
    getApi("reservation.check_room_type_availability", {
        property: property.name,
        start_date: moment(doc.value.reservation.arrival_date).format("yyyy-MM-DD"),
        end_date: moment(doc.value.reservation.departure_date).format("yyyy-MM-DD"),
        rate_type: doc.value.reservation.rate_type,
        business_source: doc.value.reservation.business_source
    })
        .then((result) => {
            console.log(result)
            result.message.forEach((r) => {
               
                let rt = room_types.value?.find((t) => t.name == r.name)

                if (rt) {
                   
                   
                    rt.total_room = r.total_room
                    rt.total_vacant_room = r.total_vacant_room
                    rt.rate = r.rate.rate
                    rt.new_rate = r.rate.rate

                } else {
  
                    r.total_selected_room = 0
                    r.rate = r.rate.rate
                    r.new_rate = r.new_rate.rate
                    room_types.value.push(r)

                }
            })

            updateRate()
        }).catch((error) => {
            gv.showErrorMessage(error)
        })
}


function onSelectedCustomer(event) {
    if (event.value) {
        getDoc('Customer', event.value)
            .then((d) => {

                doc.value.guest_info = d
                doc.value.guest_info.expired_date = moment(d.expired_date).toDate()

            })
    } else {
        doc.value.guest_info = {
            "doctype": "Customer",
            "gender": "Not Set"
        }
    }

}

const onRoomNightChanged = (event) => {

    doc.value.reservation.departure_date = moment(doc.value.reservation.arrival_date).add(event, "Days").toDate()
    getRoomType()

}

const onUseTax1Change = (value) => {
    doc.value.tax_rule.tax_1_rate = value ? room_tax.value.tax_1_rate : 0
}
const onUseTax2Change = (value) => {
    doc.value.tax_rule.tax_2_rate = value ? room_tax.value.tax_2_rate : 0
}
const onUseTax3Change = (value) => {
    doc.value.tax_rule.tax_3_rate = value ? room_tax.value.tax_3_rate : 0
}




const onSave = (assign_room = false) => {

    isSaving.value = true



    doc.value.reservation_stay = []
    room_types.value.filter(r => r.total_selected_room > 0).forEach((r) => {

        for (let i = 0; i <= r.total_selected_room - 1; i++) {
            doc.value.reservation_stay.push(
                { "rate": r.new_rate, "adult": doc.value.reservation.adult, "child": doc.value.reservation.child, "is_manual_rate": r.is_manual_rate || false, "is_master": 0, "room_type_id": r.name, "room_id": "" }
            )
        }
    });

    const data = JSON.parse(JSON.stringify(doc.value))



    if (data.reservation.reservation_date) data.reservation.reservation_date = moment(data.reservation.reservation_date).format("yyyy-MM-DD")
    if (data.reservation.arrival_date) data.reservation.arrival_date = moment(data.reservation.arrival_date).format("yyyy-MM-DD")
    if (data.reservation.departure_date) data.reservation.departure_date = moment(data.reservation.departure_date).format("yyyy-MM-DD")
    if (
        data.guest_info.expired_date) data.guest_info.expired_date = moment(data.guest_info.expired_date).format("yyyy-MM-DD")

    data.reservation.tax_1_rate = doc.value.tax_rule.tax_1_rate
    data.reservation.tax_2_rate = doc.value.tax_rule.tax_2_rate
    data.reservation.tax_3_rate = doc.value.tax_rule.tax_3_rate
    data.reservation.rate_include_tax = doc.value.tax_rule.rate_include_tax


    postApi('reservation.add_new_reservation', {
        doc: data
    }
    ).then((result) => {

        isSaving.value = false
        window.socket.emit("RefresheDoorDashboard", property.name);
        window.socket.emit("RefreshData", { property:property.name, action: "refresh_res_list" })
        dialogRef.value.close({ reservation: result.message, assign_room: assign_room });
    })
        .catch((error) => {

            isSaving.value = false
        });
}

function generateRandomColor() {
    // Generate a random number between 0 and 16777215.
    var randomNumber = Math.floor(Math.random() * 16777215);

    // Convert the random number to a hexadecimal (hex) value.
    var hexColor = randomNumber.toString(16);

    // Pad the hex value with zeros to make it 6 characters long.
    hexColor = "000000" + hexColor;

    // Return the hex value.
    return hexColor.slice(-6);
}


onMounted(() => {

    doc.value.guest_info.expired_date = moment().toDate()
    getApi("frontdesk.get_working_day", {
        property: property.name

    }).then((result) => {
        working_day.value = (result.message)
        doc.value.reservation.reservation_date = moment(working_day.value.date_working_day).toDate()

        if (!dialogRef) {
            doc.value.reservation.arrival_date = moment(working_day.value.date_working_day).toDate()
            doc.value.reservation.departure_date = moment(working_day.value.date_working_day).add(1, 'days').toDate()

            getRoomType()

        } else {
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

        }


        doc.value.reservation.room_night = moment(doc.value.reservation.departure_date).diff(moment(doc.value.reservation.arrival_date), 'days')

    })
});



const onDeleteStay = (index) => {
    doc.value.reservation_stay.splice(index, 1);
}

const updateRate = () => {


    room_types.value.filter(r => (r.is_manual_rate || false) == false).forEach(s => {
        s.new_rate = s.rate
    });
}

const onBusinessSourceChange = (source) => {

    if (source) {
        doc.value.reservation.business_source = source.value
    } else {
        doc.value.reservation.business_source = null
    }

    //check if stay have not manully rate update
    if (doc.value.reservation_stay.filter(r => r.is_manual_rate == false).length > 0) {
        getRoomType()
    }

}
const onRateTypeChange = (rate_type) => {
    if (rate_type) {
        getApi("utils.get_rate_type_info", { name: rate_type.value }).then((result) => {
            //check if rate type change then resert room revenue code and tax

            doc.value.reservation.tax_rule = (result.message?.tax_rule?.name || "")
            const tax_rule = result.message.tax_rule
            doc.value.tax_rule = {
                rate_include_tax: tax_rule?.is_rate_include_tax ? "Yes" : "No",
                tax_1_rate: tax_rule?.tax_1_rate || 0,
                tax_2_rate: tax_rule?.tax_2_rate || 0,
                tax_3_rate: tax_rule?.tax_3_rate || 0,
            }
            room_tax.value = tax_rule
            doc.value.reservation.rate_type = rate_type.value

        })

        doc.value.reservation.rate_type = rate_type.value
    }

    //check if stay have not manully rate update
    if (doc.value.reservation_stay.filter(r => (r.is_manual_rate || false) == false).length > 0) {
        getRoomType()
    }
}

const onChangeRate = () => {

    selectedStay.value.new_rate = rate.value
    selectedStay.value.is_manual_rate = true
    op.value.hide();
}

const onUseRatePlan = () => {

    selectedStay.value.is_manual_rate = false;
    updateRate()
    op.value.hide();
}
function onClose() {
    op.value.hide()
}
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