<template lang="">
    <div class="col-12">
 
        <ComReservationStayPanel title="Charge Summary ">
            <template #content>
                <div class="flex mb-2 mt-2 gap-2 text-right">
                    <div class="col p-2 bg-gray-edoor-10 rounded-lg shadow-charge-total border border-gray-edoor-100">
                        <div class="text-500 uppercase text-sm">{{$t('Total Debit')}} </div>
                        <div class="text-xl line-height-2 font-semibold" >
                            <CurrencyFormat :value="rs?.reservation?.total_debit"></CurrencyFormat></div>
                    </div>
                    <div class="col p-2 bg-gray-edoor-10 rounded-lg shadow-charge-total border border-gray-edoor-100 h-full">
                        <div class="text-500 uppercase text-sm">{{$t('Total Credit')}}</div>
                        <div class="text-xl line-height-2 font-semibold" ><CurrencyFormat :value="rs?.reservation?.total_credit"></CurrencyFormat></div>
                    </div>
                    <div class="col p-2 bg-green-50 rounded-lg shadow-charge-total border border-green-edoor">
                        <div class="text-500 uppercase text-sm">{{$t('Balance')}}</div>
                        <div class="text-xl line-height-2 font-semibold">
                            <CurrencyFormat :value="rs?.reservation?.balance"></CurrencyFormat></div>
                        </div>
                </div>
               
                <div v-for="d in rs.reservationSummary" :key="items" class="flex gap-2 mt-2">
                    <ComBoxStayInformation isCurrency v-if="d.amount != 0" :title="d?.account_category" :value="d?.amount"  valueClass="grow text-right" titleClass="col-5" ></ComBoxStayInformation>
                </div>
            </template>
        </ComReservationStayPanel>
            </div>
        <div class="col-12">
            <ComReservationStayPanel title="Room Rate Summary">
                <template #content>
                <div class="">
                    <div class="flex gap-2">
                    <ComBoxStayInformation titleTooltip="Average Daily Rate" isCurrency title="ADR" titleClass="col-4" :value="rs?.reservation?.adr" valueClass="grow text-right" >
                    </ComBoxStayInformation>
                    <span class="m-auto col-1 text-center text-xl p-0"><i class="pi pi-times"></i></span>
                    <ComBoxStayInformation  :value="rs?.reservation?.room_nights" valueClass="col-2 surface-800 text-white text-center line-height-1 border-none" >
                      <span class="text-xs block font-light">{{$t('Nights')}}</span>
                    </ComBoxStayInformation>
                    </div>
                    <div class="flex mt-2 gap-2">
                        <ComBoxStayInformation  isCurrency title="Discount" :value="rs?.reservation?.room_rate_discount" valueClass="grow text-right" titleClass="col-4" ></ComBoxStayInformation>
                    </div>
                    <div class="flex mt-2 gap-2 relative">
                        <ComBoxStayInformation  isCurrency title="Total Tax" :value="rs?.reservation?.total_room_rate_tax" valueClass="grow text-right" titleClass="col-4" >
                        <Button v-if="rs?.reservation?.room_rate_tax_1_amount || rs?.reservation?.room_rate_tax_2_amount || rs?.reservation?.room_rate_tax_3_amount" @click="toggleTAX"  icon="pi pi-question text-xs" class="float-left -ms-1 surface-border tax-info-btn" severity="secondary" rounded outlined aria-label="Total Tax" />
                        </ComBoxStayInformation>
                        <OverlayPanel ref="opTax">
                        <div class="table-order-tax">
                        <table>
                            <tr v-for="(d, index) in taxData" :key="index" ><td class='p-2 text-right border-top-1'> {{d.tax_name}} - {{d.tax_rate}} % : </td><td class='p-2 border-top-1'> <CurrencyFormat :value="d.tax_amount"/> </td></tr>

                                
                                
                        </table>    
                        </div>
                        </OverlayPanel>
                    </div>
                    <div class="flex mt-2 gap-2">
                        <ComBoxStayInformation isCurrency title="Total Room Rate" :value="rs?.reservation?.total_room_rate" valueClass="grow text-right font-semibold" titleClass="col-4 font-semibold" ></ComBoxStayInformation>
                    </div>
                </div>
                <div v-for="items in rs.stay_summary" :key="items" class="flex gap-2 mt-2">
                    <ComBoxStayInformation isCurrency v-if="items.amount > 0" :title="items?.label" :value="items?.amount"  valueClass="grow text-right" titleClass="col-4" ></ComBoxStayInformation>
                </div>
            </template>
        </ComReservationStayPanel>
    </div>
</template>
<script setup>
import { inject, onMounted, getApi, ref } from '@/plugin';
import ComReservationStayPanel from './ComReservationStayPanel.vue'
import ComBoxStayInformation from './ComBoxStayInformation.vue'
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const emit = defineEmits('onViewReservation')
const rs = inject('$reservation');

const taxData = ref()
const opTax = ref();
const toggleTAX = (event) => {
    opTax.value.toggle(event);
}

onMounted(() => {
    setTimeout(() => {
        getApi("reservation.get_room_tax_summary", { reservation: rs.reservation.name })
            .then(result => {
                taxData.value = result.message
            })
    }, 3000);
})
</script>
<style scoped></style>