<template>
    <ComDialogContent dialogClass="max-h-screen-newres overflow-auto" @onOK="onSave" :loading="isSaving" hideButtonClose>
        <div class="ms_message_cs_edoor">
            <Message v-if="hasFutureResertion">
                {{ checkFutureReservationInfo.message }} <br />
                <Button class="border-none ml-auto mr-3" @click="onViewFutureReservation">View Reservation</Button>
            </Message>
        </div>
        <div class="n__re-custom grid">
            <div class="col-12 md:col">
                <div class="bg-card-info border-round-xl p-3 h-full">
                    <div class="">
                        <div class="grid">
                            <div class="col-12 md:col">
                                
                                <label>Reservation Date <span class="text-red-500">*</span></label><br />
                                <Calendar :disabled="doc.reservation.is_walk_in" :selectOtherMonths="true" class="p-inputtext-sm w-full"
                                    v-model="doc.reservation.reservation_date" placeholder="Reservation Date"
                                    dateFormat="dd-mm-yy" showIcon showButtonBar panelClass="no-btn-clear"
                                    :maxDate="moment(working_day.date_working_day).toDate()" />
                            </div>
                            <div class="col-6"> </div>
                        </div>
                        <div class="grid pt-2">
                            <div class="col-6">
                                <label>Reference No</label><br />
                                <InputText type="text" class="p-inputtext-sm w-full" placeholder="Reference Number"
                                    v-model="doc.reservation.reference_number" :maxlength="50"
                                    v-debounce="onChangeReference" />
                            </div>
                            <div class="col-6">
                                <label>Internal Ref. No</label><br />
                                <InputText type="text" class="p-inputtext-sm w-full" placeholder="Internal Ref. Number"
                                    v-model="doc.reservation.internal_reference_number" :maxlength="50" />
                            </div>
                        </div>
                        <div class="grid m-0">
                            <div class="col-12 md:col px-0">
                                <label>Arrival<span class="text-red-500">*</span></label><br />
                                <Calendar :disabled="doc.reservation.is_walk_in" :selectOtherMonths="true" class="p-inputtext-sm depart-arr w-full border-round-xl"
                                    v-model="doc.reservation.arrival_date" placeholder="Arrival Date"
                                    @date-select="onDateSelect" dateFormat="dd-mm-yy" showIcon showButtonBar
                                    panelClass="no-btn-clear" :minDate="minDate" />
                            </div>
                            <div class="night__wfit col-fixed px-0" style="width: 150px;">
                                <label class="hiddent">Night<span class="text-red-500">*</span></label><br />
                                <ComReservationInputNight v-model="doc.reservation.room_night"
                                    @onUpdate="onRoomNightChanged" />
                            </div>
                            <div class="col px-0">
                                <label>Departure<span class="text-red-500">*</span></label><br />

                                <Calendar :selectOtherMonths="true" class="p-inputtext-sm depart-arr w-full"
                                    v-model="doc.reservation.departure_date" placeholder="Departure Date"
                                    @date-select="onDateSelect" dateFormat="dd-mm-yy" :minDate="departureMinDate" showIcon
                                    showButtonBar panelClass="no-btn-clear" />
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
                                        class="auto__Com_Cus w-full" :filters="business_source_filter" />
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
                                    doc.reservation_stay.reduce((n, d) => n + d.adult, 0) }} /
                                    {{ doc.reservation_stay.reduce((n, d) => n + d.child, 0) }}
                                </div>
                            </div>
                        </div>
                        <div class="grid justify-end gap-3 mt-4">
                            <div class="flex align-items-center relative gap-2">
                                <label for="allowmaster" class="font-medium cursor-pointer ">Mark as Paid by Master
                                    Room</label>
                                <Checkbox
                                    v-tippy="'If you tick this check box, room charge will post to master folio of master room when check in and run night audit'"
                                    v-model="doc.reservation.paid_by_master_room" :binary="true" :trueValue="1"
                                    inputId="allowmaster" :falseValue="0" />
                            </div>
                            <div class="flex align-items-center relative gap-2">
                                <label for="allowcity" class="font-medium cursor-pointer">Allow Post to City Ledger</label>
                                <Checkbox
                                    v-tippy="'If you tick this check box, transaction folio can post to city ledger when check in and run night audit'"
                                    v-model="doc.reservation.allow_post_to_city_ledger" :binary="true" :trueValue="1"
                                    inputId="allowcity" :falseValue="0" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-12 md:col">
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
                                        v-model="doc.guest_info.customer_name_en" :maxlength="50"
                                        v-debounce="onNewGuestName" />
                                    <div class="ms_message_cs_edoor">
                                        <Message class="flex w-full justify-content-between"
                                            v-if="doc?.guest_info?.customerExist">
                                            <div class="flex w-full justify-content-between">
                                                <span>This guest is already exist. View guest detail | <a
                                                        class="p-0 link_line_action1"
                                                        @click="onViewGuestDetail(doc.guest_info.existingGuest)">{{
                                                            doc.guest_info.existingGuest }}</a></span>
                                            </div>
                                        </Message>
                                    </div>
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
                                        v-model="doc.guest_info.phone_number" :maxlength="50"
                                        v-debounce="onChangeGuestPhoneNumber" />
                                </div>
                                <div class="col-12 lg:col-6 xl:col-8 pt-1">
                                    <label>Email Address</label><br />
                                    <InputText type="text" class="p-inputtext-sm w-full" placeholder="Email Address"
                                        v-model="doc.guest_info.email_address" :maxlength="50"
                                        v-debounce="onChangeGuestEmail" />
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
                                    <Calendar :selectOtherMonths="true" class="p-inputtext-sm w-full"
                                        v-model="doc.guest_info.expired_date" placeholder="ID Expire Date"
                                        dateFormat="dd-mm-yy" showIcon />
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
                        <label for="rate_tax" class="font-medium cursor-pointer">Rate Include Tax</label>
                        <span class="absolute right-0 w-full">
                            <Checkbox input-id="rate_tax" class="w-full flex justify-end"
                                v-model="doc.tax_rule.rate_include_tax" :binary="true" trueValue="Yes" falseValue="No" />
                        </span>
                    </div>
                    <div class="">
                        <div class="flex gap-3 flex-wrap">
                            <div class="flex gap-3 relative">
                                <label for="tax-1-rate" class="font-medium flex align-items-center h-full">{{
                                    room_tax.tax_1_name }} {{ room_tax.tax_1_rate }}%</label>
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
                                <label for="tax-2-rate" class="font-medium flex align-items-center h-full">{{
                                    room_tax.tax_2_name }} {{ room_tax.tax_2_rate }}%</label>
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
                                <label for="tax-3-rate" class="font-medium flex align-items-center h-full">{{
                                    room_tax.tax_3_name }} {{ room_tax.tax_3_rate }}%</label>
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
            <div class="n__re-custom overflow-auto">
                <table class="w-full">
                    <thead>
                        <tr>
                            <th class="text-left">
                                <label>Room Type<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-left">
                                <label class="px-2">Room Name</label>
                            </th>
                            <th v-if="can_view_rate" class="text-right">
                                <label class="px-2">Rate</label>
                            </th>
                            <th v-if="can_view_rate" class="text-right">
                                <label class="text-center px-2">Total Tax</label>
                            </th>
                            <th>
                                <label class="text-center px-2">Adults</label>
                            </th>
                            <th>
                                <label class="text-center px-2">Children</label>
                            </th>
                            <th>
                                <label class="text-center px-2 white-space-nowrap">Total Nights</label>
                            </th>
                            <th v-if="can_view_rate" class="text-right">
                                <label class="px-2">Amount</label>
                            </th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(  d, index  ) in   doc.reservation_stay" :key="index">
                            <td class="pr-2 min-w-5rem">
                                <Dropdown v-model="d.room_type_id" :options="room_types" optionValue="name"
                                    @change="onSelectRoomType(d)" optionLabel="room_type" placeholder="Select Room Type"
                                    class="w-full">
                                    <template #option="slotProps">
                                        <div class="flex align-items-center">

                                            <div>{{ slotProps.option.room_type }} ({{ slotProps.option.total_vacant_room ||
                                                0 }})</div>
                                        </div>
                                    </template>
                                </Dropdown>
                            </td>
                            <td class="p-2 min-w-5rem">
                                <Dropdown v-model="d.room_id"
                                    :options="rooms.filter((r) => (r.room_type_id == d.room_type_id && (r.selected ?? 0) == 0) || (r.room_type_id == d.room_type_id && r.name == d.room_id))"
                                    optionValue="name" @change="OnSelectRoom" optionLabel="room_number"
                                    placeholder="Select Room" showClear filter class="w-full" />
                            </td>
                            <td v-if="can_view_rate" class="p-2 w-15rem text-right">
                                <div v-tippy="!doc.allow_user_to_edit_rate ? 'This Rate Type Not Allow to Change Rate' : ''"
                                    class="box-input-detail">
                                    <div :class="!doc.allow_user_to_edit_rate ? 'pointer-events-none opacity-90' : ''"
                                        @click="onOpenChangeRate($event, d)"
                                        class="text-right w-full color-purple-edoor text-md font-italic inline ">
                                        <div v-tippy="(d.is_manual_rate) ? 'Manual Rate' : 'Rate Plan'"
                                            class="link_line_action flex justify-between">
                                            <div>
                                                <span class="text-sm" v-if="d.is_manual_rate"> (Manual) </span>
                                                <span class="text-sm" v-else>(Plan)</span>
                                            </div>
                                            <CurrencyFormat :value="d.rate" />
                                        </div>
                                    </div>
                                </div>
                            </td>
                            <td v-if="can_view_rate" class="p-2 w-12rem text-right">
                                <div class="box-input-detail">
                                    <CurrencyFormat :value="roomRateTax(d)" />
                                </div>
                            </td>
                            <td class="p-2 w-4rem">
                                <InputNumber inputClass="w-4rem" v-model="d.adult" inputId="stacked-buttons" showButtons
                                    :min="1" :max="100" class="child-adults-txt" />
                            </td>
                            <td class="p-2 w-4rem">
                                <InputNumber inputClass="w-4rem" v-model="d.child" inputId="stacked-buttons" showButtons
                                    :min="0" :max="100" class="child-adults-txt" />
                            </td>

                            <td class="p-2 w-8rem">
                                <div class="box-input-detail text-center">
                                    {{ doc.reservation.room_night }}
                                </div>
                            </td>
                            <td v-if="can_view_rate" class="p-2 w-10rem">
                                <div class="p-inputtext-pt text-end border-1 border-white h-12 white-space-nowrap"
                                    v-if="doc.tax_rule.rate_include_tax == 'Yes'">

                                    <CurrencyFormat :value="(d.rate) * (doc.reservation.room_night ?? 0)" />
                                </div>
                                <div class="p-inputtext-pt text-end border-1 border-white h-12 white-space-nowrap" v-else>
                                    <CurrencyFormat
                                        :value="(roomRateTax(d)) + (d.rate * doc.reservation.room_night ?? 0)" />
                                </div>
                            </td>

                            <td v-if="doc.reservation_stay.length > 1" class="pl-2 text-end w-3rem">
                                <Button icon="pi pi-trash" @click="onDeleteStay(index)" class="tr-h__custom text-3xl h-12"
                                    aria-label="Filter" />
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="flex justify-between">
                <div>
                    <Button @click="onAddRoom" class="px-4 mt-2 conten-btn">
                        <img :src="IconAddRoom" class="btn-add_comNote__icon me-1" />
                        Add Room
                    </Button>
                </div>

            </div>

            <Message severity="warn" v-if="warningMessage" v-for="(m, index) in warningMessage" :key="index">
                <p v-html="m"></p>
            </Message>

            <Message v-if="doc.reservation_stay.filter(r => !r.room_id).length > 0">You have {{
                doc.reservation_stay.filter(r => !r.room_id).length }} unassign room(s). You can assign room later in
                reservation detail.</Message>
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
    </ComDialogContent>
</template>
<script setup>
import { ref, inject, computed, onMounted, postApi, getApi, getDoc, useDialog, getDocList } from "@/plugin"
import ComReservationInputNight from './components/ComReservationInputNight.vue';
import IconAddRoom from '@/assets/svg/icon-add-plus-sign-purple.svg';
import ComReservationStayChangeRate from "./components/ComReservationStayChangeRate.vue"
import ComIFrameModal from '@/components/ComIFrameModal.vue';

const dialog = useDialog();
const dialogRef = inject("dialogRef");
const moment = inject("$moment")
const isSaving = ref(false)
const gv = inject("$gv")

const property = JSON.parse(localStorage.getItem("edoor_property"))
const room_types = ref([])
const rooms = ref([])
const working_day = ref({})
const selectedStay = ref({})
const rate = ref(0)
const op = ref();
const can_view_rate = window.can_view_rate
const room_tax = ref()
const minDate = ref()
const hasFutureResertion = ref(false)
const checkFutureReservationInfo = ref({})





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
        reservation_status: 'Reserved',
        tax_rule: room_tax.value?.name,
        paid_by_master_room: 0,
        group_code: "",
        group_name: "",
        allow_post_to_city_ledger: 1,
        is_walk_in: dialogRef.value.data?.is_walk_in || 0,
       
    },
    guest_info: {
        "doctype": "Customer",
        "gender": "Not Set"
    },
    reservation_stay: [{ rate: 0, adult: 1, child: 0, is_manual_rate: false, is_master: 0 },],
    tax_rule: {
        rate_include_tax: "No",
        tax_1_rate: 0,
        tax_2_rate: 0,
        tax_3_rate: 0,
    }
})


const business_source_filter =ref({ property: property.name })
if (doc.value.reservation.is_walk_in==1){
    doc.value.reservation.business_source = window.setting.property?.default_walk_in_business_source
    business_source_filter.value.is_walk_in_business_source = 1
    doc.value.reservation.allow_post_to_city_ledger= 0
} else {
    business_source_filter.value.is_walk_in_business_source = 0

}


const gender_list = ["Not Set", "Male", "Female"]

const useTax = computed(() => {
    return {
        use_tax_1: (room_tax.value?.tax_1_rate || 0) > 0,
        use_tax_2: (room_tax.value?.tax_2_rate || 0) > 0,
        use_tax_3: (room_tax.value?.tax_3_rate || 0) > 0
    }
})


const roomRateTax = ref((d) => {
    const tax_1_amount = getTax1Amount(d.rate * doc.value.reservation.room_night)
    const tax_2_amount = getTax2Amount(d.rate * doc.value.reservation.room_night)
    const tax_3_amount = getTax3Amount(d.rate * doc.value.reservation.room_night)
    return tax_1_amount + tax_2_amount + tax_3_amount
});


function getTax1Amount(rate) {
    if (room_tax.value) {
        if (room_tax.value?.calculate_tax_1_after_discount == 0 || doc.value?.tax_rule.rate_include_tax == 'Yes') {
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
        if (room_tax.value?.calculate_tax_1_after_discount == 0 || doc.value.tax_rule.rate_include_tax == 'Yes') {
            rate = rate = gv.getRateBeforeTax((rate || 0), room_tax.value, doc.value.tax_rule.tax_1_rate, doc.value.tax_rule.tax_2_rate, doc.value.tax_rule.tax_3_rate)

        } else {
            rate = rate

        }
        if (room_tax.value?.calculate_tax_2_after_adding_tax_1 == 0 || (rate * (doc.value.tax_rule.tax_1_rate / 100)) == 0) {
            rate = rate
        } else { rate = rate + (rate * (doc.value.tax_rule.tax_1_rate / 100)) }
        return (rate || 0) * (doc.value.tax_rule.tax_2_rate / 100 || 0)
    } else {
        return 0
    }
}
function getTax3Amount(rate) {
    if (room_tax.value) {
        if (room_tax.value?.calculate_tax_1_after_discount == 0 || doc.value.tax_rule.rate_include_tax == 'Yes') {
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
    doc.value.reservation_stay.forEach(r => {
        amount = amount + getTax1Amount(r.rate)
    });
    return amount * doc.value.reservation.room_night
})
const totalTax2Amount = computed(() => {
    let amount = 0
    doc.value.reservation_stay.forEach(r => {
        amount = amount + getTax2Amount(r.rate)
    });
    return amount * doc.value.reservation.room_night
})
const totalTax3Amount = computed(() => {
    let amount = 0
    doc.value.reservation_stay.forEach(r => {
        amount = amount + getTax3Amount(r.rate)
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
    getRooms()


}


const warningMessage = computed(() => {
    const messages = []
    const room_type = [...new Set(doc.value.reservation_stay.filter(x => x.room_type_id).map(item => item.room_type_id))]
    if (room_type) {
        room_type.forEach(r => {
            const rt = room_types.value.find(y => y.name == r)

            if (rt && doc.value.reservation_stay.filter(x => x.room_type_id == r).length > (rt?.total_vacant_room || 0)) {

                messages.push("You have over booking on room type <strong>" + rt?.room_type + "</strong>. Total Over: <strong>" + Math.abs((rt?.total_vacant_room || 0) - doc.value.reservation_stay.filter(x => x.room_type_id == r).length)) + "</strong>"
            }
        })
    }

    return messages
})


const getRoomType = () => {

    getApi("reservation.check_room_type_availability", {
        property: property.name,
        start_date: moment(doc.value.reservation.arrival_date).format("yyyy-MM-DD"),
        end_date: moment(doc.value.reservation.departure_date).format("yyyy-MM-DD"),
        rate_type: doc.value.reservation.rate_type,
        business_source: doc.value.reservation.business_source
    })
        .then((result) => {
            room_types.value = result.message;
            updateRate()
        })
}

const getRooms = () => {

    getApi("reservation.check_room_availability", {
        property: property.name,
        start_date: moment(doc.value.reservation.arrival_date).format("yyyy-MM-DD"),
        end_date: moment(doc.value.reservation.departure_date).format("yyyy-MM-DD")
    })
        .then((result) => {
            rooms.value = result.message;
            OnSelectRoom()
        })
}

function onSelectedCustomer(event) {
    if (event.value) {
        getDoc('Customer', event.value)
            .then((d) => {
                doc.value.guest_info = d
                doc.value.guest_info.expired_date = moment(doc.value.guest_info.expired_dat).toDate()
            })

        //check future reservation
        getApi("reservation.check_reservation_exist_in_future", { property: window.property_name, fieldname: "guest", value: event.value }).then(r => {
            hasFutureResertion.value = r.message
            checkFutureReservationInfo.value = {
                message: `This guest id ${event.value} is already exist in the system`,
                fieldname: "guest",
                value: event.value,
            }

        })

    } else {
        doc.value.guest_info = {
            "doctype": "Customer",
            "gender": "Not Set"
        }

        hasFutureResertion.value = false
    }



}

const onRoomNightChanged = (event) => {
    doc.value.reservation.departure_date = moment(doc.value.reservation.arrival_date).add(event, "Days").toDate()
    getRoomType()
    getRooms()
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


const onAddRoom = () => {
    doc.value.reservation_stay.push(
        {
            adult: doc.value.reservation_stay[doc.value.reservation_stay.length - 1].adult,
            child: doc.value.reservation_stay[doc.value.reservation_stay.length - 1].child,
            room_type_id: doc.value.reservation_stay[doc.value.reservation_stay.length - 1].room_type_id,
            rate: doc.value.reservation_stay[doc.value.reservation_stay.length - 1].rate,
            room_id: "",
            is_manual_rate: false,
            is_master: 0

        }
    )
}

function onChangeReference(v) {
    if (v) {
        getApi("reservation.check_reservation_exist_in_future", { property: window.property_name, fieldname: "reference_number", value: v }).then(r => {
            hasFutureResertion.value = r.message
            if (r.message) {
                checkFutureReservationInfo.value = {
                    message: `This reference number ${v} is already exist in the system`,
                    fieldname: "reference_number",
                    value: v,
                }
            }
        })
    } else {
        hasFutureResertion.value = false
    }
}

function onChangeGuestPhoneNumber(v) {
    if (v) {
        getApi("reservation.check_reservation_exist_in_future", { property: window.property_name, fieldname: "guest_phone_number", value: v }).then(r => {
            hasFutureResertion.value = r.message
            if (r.message) {
                checkFutureReservationInfo.value = {
                    message: `This phone number ${v} is already exist in the system`,
                    fieldname: "guest_phone_number",
                    value: v,
                }
            }
        })
    } else {
        hasFutureResertion.value = false
    }
}


function onChangeGuestEmail(v) {
    if (v) {
        getApi("reservation.check_reservation_exist_in_future", { property: window.property_name, fieldname: "guest_email", value: v }).then(r => {
            hasFutureResertion.value = r.message
            if (r.message) {
                checkFutureReservationInfo.value = {
                    message: `This email ${v} is already exist in the system`,
                    fieldname: "guest_email",
                    value: v,
                }
            }
        })
    } else {
        hasFutureResertion.value = false
    }
}



function onNewGuestName(v) {
    if (v) {
        getApi("reservation.check_reservation_exist_in_future", { property: window.property_name, fieldname: "guest_name", value: v }).then(r => {
            hasFutureResertion.value = r.message
            if (r.message) {
                checkFutureReservationInfo.value = {
                    message: `This guest name ${v} is already exist in the system`,
                    fieldname: "guest_name",
                    value: v,
                }
            }
        })

        getDocList("Customer", { filters: [["customer_name_en", "=", v]] }).then(data => {
            doc.value.guest_info.customerExist = data.length > 0
            if (data.length > 0) {
                doc.value.guest_info.existingGuest = data[0]["name"]
            }
        })

    } else {
        hasFutureResertion.value = false
    }
}

const onViewGuestDetail = (name) => {
    window.postMessage('view_guest_detail|' + name, '*');
}

function onViewFutureReservation() {
    const dialogRef = dialog.open(ComIFrameModal, {
        data: {
            "doctype": "Business%20Branch",
            name: window.property_name,
            report_name: gv.getCustomPrintFormat("eDoor Existed Reservation"),
            view: "ui",
            extra_params: [{ key: "fieldname", value: checkFutureReservationInfo.value.fieldname }, { key: "value", value: checkFutureReservationInfo.value.value }],
            fullheight: true
        },
        props: {
            header: `View reservation by reference: ${doc.value.reservation.reference_number}`,
            style: {
                width: '90vw',
            },
            position: "top",
            modal: true,
            maximizable: true,
            closeOnEscape: false
        }
    });
}

const onSave = () => {


    const data = JSON.parse(JSON.stringify(doc.value))
    if (data.reservation.reservation_date) data.reservation.reservation_date = moment(data.reservation.reservation_date).format("yyyy-MM-DD")
    if (data.reservation.arrival_date) data.reservation.arrival_date = moment(data.reservation.arrival_date).format("yyyy-MM-DD")
    if (data.reservation.departure_date) data.reservation.departure_date = moment(data.reservation.departure_date).format("yyyy-MM-DD")

    if (data.guest_info.expired_date) data.guest_info.expired_date = moment(data.guest_info.expired_date).format("yyyy-MM-DD")

    data.reservation.tax_1_rate = doc.value.tax_rule.tax_1_rate
    data.reservation.tax_2_rate = doc.value.tax_rule.tax_2_rate
    data.reservation.tax_3_rate = doc.value.tax_rule.tax_3_rate
    data.reservation.rate_include_tax = doc.value.tax_rule.rate_include_tax
    data.reservation_stay = data.reservation_stay.filter(r => r.room_type_id)
    isSaving.value = true
    postApi('reservation.add_new_reservation', {
        doc: data
    },
        "Add new reservation successfully"
    ).then((result) => {
        isSaving.value = false
        
        if(data.reservation.arrival_date==window.current_working_date || data.reservation.departure_date==window.current_working_date  ){
            window.postMessage({"action":"Dashboard"},"*")
        }
        
        

        
        window.postMessage({action:"ReservationList"},"*")
        window.postMessage({action:"ReservationStayList"},"*")

        window.postMessage({"action":"Frontdesk"},"*")


        dialogRef.value.close(result.message);
    })
        .catch((error) => {

            isSaving.value = false
        });
}

onMounted(() => {
    doc.value.guest_info.expired_date = moment().toDate()

    getApi("frontdesk.get_working_day", {
        property: property.name

    }).then((result) => {
        working_day.value = (result.message)
        minDate.value = window.setting.allow_user_to_add_back_date_transaction == 1 ? moment().add(-50, 'years').toDate() : moment(working_day.value.date_working_day).toDate()

        doc.value.reservation.reservation_date = moment(working_day.value.date_working_day).toDate()

        if (!dialogRef) {
            doc.value.reservation.arrival_date = moment(working_day.value.date_working_day).toDate()
            doc.value.reservation.departure_date = moment(working_day.value.date_working_day).add(1, 'days').toDate()

            getRoomType()
            getRooms()
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
            s.rate = room_type.rate.rate

        }

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
        getApi("utils.get_rate_type_info", { name: rate_type })
            .then((result) => {

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
                doc.value.reservation.rate_type = rate_type
                doc.value.allow_user_to_edit_rate = result.message.allow_user_to_edit_rate
                //check if stay have not manully rate update
                if (doc.value.reservation_stay.filter(r => (r.is_manual_rate || false) == false).length > 0) {
                    getRoomType()
                }

            })
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
function onClose() {
    op.value.hide()
}
</script>
<style>
.ch__rate_nres input {
    text-align: right !important;
    font-size: 1.1rem;
    height: 3rem;
}

.p-button.p-component .p-button-icon {
    font-weight: 600;
    font-size: 1.25rem;
}
</style>