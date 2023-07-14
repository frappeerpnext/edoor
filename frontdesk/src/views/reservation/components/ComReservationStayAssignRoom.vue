<template>
    <ComDialogContent @onClose="onClose" @onOK="onSave" :loading="loading">
    <div class="">
        <ComReservationStayPanel title="Assign Room">
            <template #content> 
            <div class="n__re-custom">
                <table class="w-full">
                    <thead>
                        <tr>
                            <th class="text-left pe-2 w-12rem">
                                <label>Start Date</label>
                            </th>
                            <th class="text-left px-2 w-14rem">
                                <label>End Date</label>
                            </th>
                            <th class="text-left px-2">
                                <label>Room Type<span class="text-red-500">*</span></label>
                            </th>
                            <th class="text-left px-2">
                                <label>Room Name</label>
                            </th>
                            <th class="text-center px-2 w-5rem">
                                <label class="text-center">Nights</label>
                            </th>
                            <th class="text-right px-2">
                                <label>Rate</label>
                            </th>
                            <th class="text-right ps-2">
                                <label>Amount</label>
                            </th>

                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td class="pe-2 w-12rem">
                                <span class="p-inputtext-pt border-1 border-white h-12 w-full flex white-space-nowrap">{{gv.dateFormat(moment(selectedStay.start_date))}}</span>
                            </td>
                            <td class="px-2 w-14rem"> 
                                <span class="p-inputtext-pt border-1 border-white h-12 w-full flex white-space-nowrap">{{gv.dateFormat(moment(selectedStay.end_date))}}</span>
                            </td>
                            <td class="px-2 w-16rem">  
                                <ComSelectRoomTypeAvailability 
                                    v-model="selectedStay.room_type_id"
                                    @onSelected="onSelectRoomType"
                                    :rate-type="rs.reservationStay.rate_type"
                                    :businessSource="rs.reservationStay.business_source"
                                    :start-date="selectedStay.start_date"
                                    :end-date="selectedStay.end_date"/>
                            </td>
                            <td class="px-2 w-8rem"> 
                                <ComSelectRoomAvailability 
                                    v-model="selectedStay.room_id"
                                    :start-date="selectedStay.start_date"
                                    :end-date="selectedStay.end_date"
                                    :roomType="selectedStay.room_type_id" />
                            </td>
                            <td class="text-center px-2 w-5rem"> 
                                <span class="p-inputtext-pt border-1 border-white h-12 w-full flex white-space-nowrap text-center justify-center">{{ selectedStay.room_nights }}</span>
                            </td>
                            <td class="text-right px-2 w-10rem">
                                <span class="white-space-nowrap">
                                    <span @click="onOpenChangeRate($event)" class="text-right w-full color-purple-edoor text-md font-italic ">
                                        <span class="link_line_action">
                                            <CurrencyFormat :value="selectedStay.rate" />
                                        </span>
                                    </span>
                                </span>
                            </td>
                            <td class="text-right ps-2 w-10rem">
                                <span class="p-inputtext-pt border-1 border-white h-12 w-full flex justify-end">
                                    <CurrencyFormat :value="(selectedStay.room_nights   ?? 0) * (selectedStay.rate ?? 0)" />
                                </span>
                            </td>
                        </tr>
                    </tbody>
                    <tbody>
                        <tr>
                            <td colspan="7">
                                <div class="text-right pt-2">
                                    <div>
                                        <Checkbox class="mr-1" v-model="isOverrideRate" :binary="true" inputId="disabled" />
                                        <label for="disabled"> Override Room Rate</label>
                                    </div>
                                </div>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            </template>
        </ComReservationStayPanel>
        <OverlayPanel ref="op">
            <ComReservationStayChangeRate v-model="rate" @onClose="onCloseRate" @onUseRatePlan="onUseRatePlan" @onChangeRate="onChangeRate"/>
        </OverlayPanel>

    </div>
</ComDialogContent>
</template>
<script setup>
    import {inject,ref, getApi, onMounted,postApi} from '@/plugin'
    import ComReservationStayPanel from './ComReservationStayPanel.vue';
    import ComReservationStayChangeRate from './ComReservationStayChangeRate.vue'
    const property = JSON.parse(localStorage.getItem("edoor_property"))
    const rs = inject('$reservation_stay')
    const moment = inject('$moment')
    const gv = inject('$gv')
    const dialogRef = inject('dialogRef'); 
    const working_day = ref({})
    const op = ref()
    const loading = ref(false)
    const isOverrideRate = ref(false)
    const selectedStay = ref({})
    
    const rate = ref(0)
    const onUseRatePlan = () => {
        selectedStay.value.is_manual_rate = false;
        op.value.hide();
    }
    const onClose = (r) =>{ 
        dialogRef.value.close(r);
    }
    function onCloseRate(){
        op.value.hide()
    }
    const onChangeRate = () => {
        selectedStay.value.rate = rate.value
        selectedStay.value.is_manual_rate = true
        op.value.hide();
    }

    const onOpenChangeRate = (event) => {
        rate.value = JSON.parse(JSON.stringify(selectedStay.value)).rate
        op.value.toggle(event);
    }

    const onSelectRoomType = (r) => {
        selectedStay.value.rate = r.rate
        rate.value = r.rate
    }
    function onSave(){ 
        if(!selectedStay.value.room_type_id){
            gv.toast('warn','Please select room type.')
            return
        }
        loading.value = true
        const dataSave = {
            reservation_stay: rs.reservationStay.name, 
            room_stay: selectedStay.value.name,
            room_type_id: selectedStay.value.room_type_id,
            room_id: selectedStay.value.room_id,
            is_manual_rate: selectedStay.value.is_manual_rate,
            is_override_rate: isOverrideRate.value,
            rate: selectedStay.value.rate
        }
        postApi("reservation.assign_room",{data: dataSave}).then((r)=>{
            loading.value = false
            onClose(r)
        }).catch(()=>{
            loading.value = false
        })
    }
    onMounted(() => {
        getApi("frontdesk.get_working_day", {
            property: property.name
        }).then((result) => {
            working_day.value = (result.message)
            selectedStay.value = dialogRef.value.options.data.stay_room
        })
});
</script>
<style scoped>
    .box-input{
        padding: .6rem .65rem;
    }
</style>