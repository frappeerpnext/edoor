<template>
    <ComDialogContent @onOK="onSave" v-model:visible="visible" modal header="Edit Rate" :loading="isSaving" hideButtonClose>
       
        <div class="grid">
        <div class="col-12">
            <div v-if="current_date >= moment(stay?.arrival_date).toDate() && stay?.reservation_status == 'In-house'">
            <Message severity="info">
                {{ $t('Changes to room rates made to past or current dates will not automatically update guest folios. Please manually review room charges in guest folios to ensure accuracy.') }}
                
            </Message>
        </div>
        <div
            v-if="current_date >= moment(stay_reservation?.arrival_date).toDate() && stay_reservation?.reservation_status == 'In-house'">
            <Message severity="info">
                {{ $t('Changes to room rates made to past or current dates will not automatically update guest folios. Please manually review room charges in guest folios to ensure accuracy.') }}
                
            </Message>
        </div>
        
        <div class="grid justify-between" v-if="stay">
            <div>

          

 </div>
            <div class="col-12 xl:col-6 overflow-auto">
                <table>
                    <tbody>
                        <ComStayInfoNoBox label="Res Stay. No" isSlot :fill="false">
                            <button @click="onOpenLink(stay?.name)" class="p-0 link_line_action1">{{ stay?.name }}</button>
                        </ComStayInfoNoBox>
                        <ComStayInfoNoBox label="Business Source" :value="stay?.business_source" />
                        <tr>
                            <th class="w-auto border-1 p-2 text-start" style="background: rgb(243, 243, 243);">
                                <label class="font-normal white-space-nowrap"> {{ $t('Room') }} </label>
                            </th>
                            <td class="w-full border-1 p-2">
                                <span v-for="(i, index) in roomData" :key="index">
                                    <div class="inline font-semibold text-right" v-if="index < 3">
                                        <div class="rounded-xl px-2 me-1 bg-gray-edoor inline">
                                            <span v-tippy="i.room_type">{{ i.room_type_alias }} </span>
                                            <span v-if="i.room_number">/{{ i.room_number }}
                                            </span>
                                        </div>
                                    </div>
                                </span>
                                <span v-if="roomData.length > 3"
                                    v-tippy="getTooltip()"
                                    class="inline rounded-xl px-2 bg-purple-cs w-auto ms-1 cursor-pointer whitespace-nowrap">
                                    {{ roomData.length - 3 }} 
                                    {{ $t('Mores') }}
                                    
                                </span>
                            </td>
                        </tr>
                        <ComStayInfoNoBox label="Date" :value="moment(stay?.arrival_date).format('DD-MM-yyyy')" />
                    </tbody>
                </table>
            </div>
            <div class="col-12 xl:col-6">
                <table>
                    <tbody>
                        <ComStayInfoNoBox label="Guest" :value="stay?.guest_name + ' (' + stay?.guest + ')'" />
                        <ComStayInfoNoBox label="Pax(A/C)" :value="stay?.adult + '/' + stay?.child" />
                         
                        <ComStayInfoNoBox label="Phone Number" :value="stay?.guest_phone_number" />
                    </tbody>
                </table>
            </div>
        </div>
        
        <div class="grid justify-between" v-if="stay_reservation">
            <div class="col-12 lg:col-6">
                <table>
                    <tbody>
                        <ComStayInfoNoBox label="Res Stay. No" :value="stay_reservation?.name" />
                        <ComStayInfoNoBox label="Business Source" :value="stay_reservation?.business_source" />
                        <ComStayInfoNoBox label="Room">
                            <div class="flex">
                            <span v-for="(i, index) in roomData" :key="index">
                                    <div class="inline font-semibold text-right -ml-2" v-if="index < 3">
                                        <div class="rounded-xl px-2 me-1 bg-gray-edoor inline">
                                            <span v-tippy="i.room_type">{{ i.room_type_alias }} </span>
                                            <span v-if="i.room_number">/{{ i.room_number }}
                                            </span>
                                        </div>
                                    </div>
                                </span>
                                <span v-if="roomData.length > 3"
                                    v-tippy="getTooltip()"
                                    class="inline rounded-xl px-2 bg-purple-cs w-auto ms-1 cursor-pointer whitespace-nowrap">
                                    {{ roomData.length - 3 }} Mores
                                </span>
                            </div>
                        </ComStayInfoNoBox>
                        <ComStayInfoNoBox label="Date"
                            :value="moment(stay_reservation?.arrival_date).format('DD-MM-yyyy')" />
                    </tbody>
                </table>
            </div>
            <div class="col-12 lg:col-6">
                <table>
                    <tbody>
                        <ComStayInfoNoBox label="Guest"
                            :value="stay_reservation?.guest_name + ' (' + stay_reservation?.guest + ')'" />
                        <ComStayInfoNoBox label="Pax" :value="stay_reservation?.adult + '/' + stay_reservation?.child" />
                        <ComStayInfoNoBox label="Phone Number" :value="stay_reservation?.guest_phone_number" />
                    </tbody>
                </table>
            </div>
        </div>
        <hr class="my-1">   
    </div>
        <div :class="(doc.is_house_use +doc.is_complimentary )==0 || doc.tax_rule || doc.is_package?'col-8':'col-12'">
        <!--  -->
     
        <div class="grid">
            <div class="col-12 lg:col mt-2 ">
                <div class="grid">
                    <div class="col-12 lg:col-6">
                        <div>
                            <label> {{ $t('Rate Type') }} </label>
                            <ComSelect class="w-full" v-model="doc.rate_type" doctype="Rate Type"
                                @onSelected="onSelectRateType" :clear="false" />
                        </div>
                    </div>
                    <div class="col-12 lg:col-6">
                        <div class="relative">
                            <label>{{ $t('Room Rate') }}</label>
                            <ComInputCurrency classCss="w-full"  v-model="doc.input_rate"
                                :disabled="doc.is_manual_rate == 0" @update:modelValue="get_room_rate_breakdown()" />
                            <div v-tippy="$t('Use Manually Update Rate')" class="absolute right-2 top-2/4 mb-2">                                
                                <Checkbox :disabled="!doc.allow_user_to_edit_rate"  input-id="manual_rate" v-model="doc.is_manual_rate" :trueValue="1"
                                    :falseValue="0" :binary="true" @change="onUseManualRate" />
                            </div>
                        </div>
                    </div>
                    <div class="wp-number-cus col-12 pt-0 w-full grid pr-0">
 
        <div class="col-6 pr-1 ">
            
        <label>{{$t('Adults')}}</label>
        <InputNumber @update:modelValue="get_room_rate_breakdown()" v-model="doc.adult" inputId="stacked-buttons" showButtons :min="1" :max="100"
            class="child-adults-txt w-full" :disabled="!(doc.is_manual_change_pax)" />
        </div>
        <div class="col-6 pr-0 pl-3">
        <label>{{$t('Children')}}</label>
        <InputNumber v-model="doc.child" @update:modelValue="get_room_rate_breakdown()" inputId="stacked-buttons" showButtons :min="0" :max="100"
            class="child-adults-txt w-full" :disabled="!(doc.is_manual_change_pax)" />
        </div>
        <div class="relative mt-2 pt-0 col-12">
            <span class="absolute w-full"><Checkbox @update:modelValue="checkChangePax()"   class="w-full" v-model="doc.is_manual_change_pax" :binary="true" :trueValue="1"
                                :falseValue="0" /></span>
            <span class="pl-5">Manual Change Pax</span>
        </div> 
        </div>
                    <template v-if="doc.allow_discount==1">
                    <div class="col-12 lg:col-4">
                        <label>{{ $t('Discount Type') }}</label>
                        <ComSelect class="w-full min-w-full" v-model="doc.discount_type" optionLabel="label" optionValue="value" :options="discountType"
                            :clear="false" @update:modelValue="get_room_rate_breakdown()" />
                    </div>
                    <div class="col-12 lg:col-4">
                        <label>{{ $t('Discount') }}</label>
                        <InputNumber class="w-full" :input-class="'w-full'" v-model="doc.discount" :minFractionDigits="2"
                            :maxFractionDigits="10" @update:modelValue="get_room_rate_breakdown()" />
                    </div>
                    <div class="col-12 lg:col-4 text-right">
                        <label>{{ $t('Discount Amount') }}</label>
                        <div
                            class="w-full rounded-lg max-h-3rem h-edoor-35 leading-8 bg-gray-edoor-10 justify-end flex items-center px-3">
                            <CurrencyFormat :value="RoomRateCalculation.discount_amount" />
                        </div>
                    </div>
                    </template>
                    <div class="col-12 lg:col-6 text-right" v-if="doc.tax_rule">
                        <label class="font-bold" >{{ $t('Total Tax') }}</label>
                        <div
                            class="w-full rounded-lg max-h-3rem h-edoor-35 leading-8 bg-gray-edoor-10 justify-end flex items-center px-3">
                            <CurrencyFormat :value="RoomRateCalculation.total_tax" />
                        </div>
                    </div>
                    <div class="col-12 lg:col-6 text-right">
                        <label class="font-bold">{{ $t('Total Amount') }}</label>
                        <div
                            class="w-full rounded-lg max-h-3rem h-edoor-35 leading-8 bg-gray-edoor-10 justify-end flex items-center px-3">
                            <CurrencyFormat :value="RoomRateCalculation.total_amount" />
                        </div>
                    </div>
                    <div class="col-12 text-right"
                        v-if="tax_rule && tax_rule.tax_1_rate > 0 && tax_rule.tax_2_rate > 0 && tax_rule.tax_3_rate > 0">
                        <div class="grid justify-end">
                            <div class="col-6 lg:col-4">
                                <label>{{ $t('Rate Before Tax') }}</label>
                                <div
                                    class="w-full rounded-lg max-h-3rem h-edoor-35 leading-8 bg-gray-edoor-10 justify-end flex items-center px-3">
                                    <CurrencyFormat :value="rate" />
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="col-12">
                        <Textarea :placeholder="$t('Note')" class="w-full" v-model="doc.note" />
                    </div>
                    <div class="col-12" v-if="showCheckUpdateFutureStayRoomRate">
                        <Checkbox class="" v-model="updateFutureRoomRate" :binary="true" />
                        {{ $t('Update room rate to the future stay room rate') }}
                         ({{ futureRoomRates?.length - 1 }} {{ $t('Room Night(s)') }})
                    </div>
                </div>
            </div>
           

            <hr />

        </div>
        </div>
        
<div class="col-4" v-if="(doc.is_house_use +doc.is_complimentary )==0 ||  doc.tax_rule || doc.is_package">
    <div class="card">
        <Accordion :activeIndex="0">
            <AccordionTab header="Room Rate Breakdown">
                <div class="grid p-2">
                    
                    <div class="col-12 pb-0">
                <div class="grid justify-end ">
                    <div class="col-12">
                        <table>
                    <tbody>
                        <ComStayInfoNoBox label="Base Rate"
                            :value="RoomRateCalculation.room_charge_data?.rate" isCurrency="true" valueClass="text-end" />
                            <ComStayInfoNoBox v-if="RoomRateCalculation.room_charge_data?.discount_amount" label="Discount" :value="RoomRateCalculation.room_charge_data?.discount_amount" isCurrency="true" valueClass="text-end" />    
                            <ComStayInfoNoBox label="Rate Include Tax" valueClass="text-end">
                                <div class="flex gap-2"> 
                             <Checkbox  v-if="RoomRateCalculation.room_charge_data?.rate_include_tax"    v-model="doc.rate_include_tax" :binary="true"
                                    trueValue="Yes" falseValue="No" @update:modelValue="get_room_rate_breakdown()" /> 
                                </div>    
                              
                            </ComStayInfoNoBox>
                            <ComStayInfoNoBox v-if="tax_rule && tax_rule.tax_1_rate > 0" :label="($t(tax_rule.tax_1_name ?? '') || '') + ' ' + (tax_rule.tax_1_rate || 0) + '%'" valueClass="text-end">
                                <div class="flex gap-2"> 
                                    <CurrencyFormat :value="RoomRateCalculation.room_charge_data?.tax_1_amount || 0 " />
                                <Checkbox input-id="tax-1" v-model="use_tax.use_tax_1" @input="onUseTax1Change"
                                                                          :binary="true" />
                                </div>
                            </ComStayInfoNoBox>
                            <ComStayInfoNoBox v-if="tax_rule && tax_rule.tax_2_rate > 0" :label="($t(tax_rule.tax_2_name ?? '') || '') + ' ' + (tax_rule.tax_2_rate || 0) + '%'" valueClass="text-end">
                                <div class="flex gap-2"> 
                                    <CurrencyFormat :value="RoomRateCalculation.room_charge_data?.tax_2_amount || 0 " />
                                <Checkbox input-id="tax-2" @input="onUseTax2Change" v-model="use_tax.use_tax_2"
                                                            :binary="true" />
                                </div>
                            </ComStayInfoNoBox>
                            <ComStayInfoNoBox v-if="tax_rule && tax_rule.tax_3_rate > 0" :label="($t(tax_rule.tax_3_name ?? '') || '') + ' ' + (tax_rule.tax_3_rate || 0) + '%'" valueClass="text-end">
                                <div class="flex gap-2"> 
                                    <CurrencyFormat :value="RoomRateCalculation.room_charge_data?.tax_3_amount || 0 " />
                                <Checkbox input-id="tax-3" @input="onUseTax3Change" v-model="use_tax.use_tax_3"
                                                            :binary="true" />
                                </div>
                            </ComStayInfoNoBox>
                            <ComStayInfoNoBox  v-if="tax_rule || tax_rule.tax_1_rate > 0 || tax_rule.tax_2_rate > 0 || tax_rule.tax_3_rate > 0" 
                                label="Total Tax" 
                                :value="RoomRateCalculation.room_charge_data?.total_tax" isCurrency="true" valueClass="text-end" />  
                                <ComStayInfoNoBox   
                                label="Total Rate" 
                                :value="RoomRateCalculation.room_charge_data?.total_amount" isCurrency="true" valueClass="text-end" />        
                    </tbody>
                </table>
                   
                        
                    </div>
                </div>
            </div>
                </div>
              
            </AccordionTab>
            <AccordionTab v-if="doc.is_package" >
               <template #header>
Package Charge Breakdown
               </template> 
                <div class="col-12">
  <div class="grid p-y px-2">
    <div class="col-12" v-for="item in RoomRateCalculation.package_charge_data" :key="item.account_name" >
        <Fieldset  :key="item.account_name" v-if="item.quantity > 0" >
            <template #legend>
                <div class="flex align-items-center pl-2">
                    <span class="font-bold"> {{ item.account_name }} x {{ item.quantity }} </span>
                </div>
            </template>
            <div class="grid">
                <table class="w-full">
                    <tbody>
                        <ComStayInfoNoBox label="Base Rate"
                            :value="item.rate" isCurrency="true" valueClass="text-end" />
                            <ComStayInfoNoBox v-if="item.discount_amount > 0" label="Discount" :value="item.discount_amount" isCurrency="true" valueClass="text-end" />    
                          <ComStayInfoNoBox label="Rate Include Tax" valueClass="text-end">
                                <div class="flex gap-2"> 
                             <Checkbox  v-model="item.rate_include_tax" disabled :binary="true"
                                    trueValue="Yes" falseValue="No"  /> 
                                </div>    
                              
                            </ComStayInfoNoBox>
                              <ComStayInfoNoBox v-if="item.tax_1_rate > 0" :label="($t(item.tax_1_name ?? '') || '') + ' ' + (item.tax_1_rate || 0) + '%'" valueClass="text-end">
                                <div class="flex gap-2"> 
                                    <CurrencyFormat :value="item.tax_1_amount || 0 " />
                                <Checkbox v-model="isCheckedTrue" disabled :binary="true"
                                    />
                                </div>
                            </ComStayInfoNoBox>
                           <ComStayInfoNoBox v-if="item.tax_2_rate > 0" :label="($t(item.tax_2_name ?? '') || '') + ' ' + (item.tax_2_rate || 0) + '%'" valueClass="text-end">
                                <div class="flex gap-2"> 
                                    <CurrencyFormat :value="item.tax_2_amount || 0 " />
                                    <Checkbox v-model="isCheckedTrue" disabled :binary="true"
                                    />
                                </div>
                            </ComStayInfoNoBox>
                              <ComStayInfoNoBox v-if="item.tax_3_rate > 0" :label="($t(item.tax_3_name ?? '') || '') + ' ' + (item.tax_3_rate || 0) + '%'" valueClass="text-end">
                                <div class="flex gap-2"> 
                                    <CurrencyFormat :value="item.tax_3_amount || 0 " />
                                    <Checkbox v-model="isCheckedTrue" disabled :binary="true"
                                   />
                                </div>
                            </ComStayInfoNoBox>
                          <ComStayInfoNoBox  v-if="item.tax_1_rate > 0 || item.tax_2_rate > 0 || item.tax_3_rate > 0" 
                                label="Total Tax" 
                                :value="item.total_tax" isCurrency="true" valueClass="text-end" />  
                                 <ComStayInfoNoBox   
                                label="Total Rate" 
                                :value="item.total_amount" isCurrency="true" valueClass="text-end" />        
                    </tbody>
                </table>
            </div> 
        </Fieldset>
    </div>
                </div>
                </div>
            </AccordionTab>
        </Accordion>
    </div>
</div>
</div>
    </ComDialogContent>
</template>
<script setup>
import { ref, inject, computed, onMounted, postApi, getApi } from "@/plugin"
import Checkbox from 'primevue/checkbox';
import InputNumber from 'primevue/inputnumber';
import Textarea from 'primevue/textarea';
import ComBoxStayInformation from './ComBoxStayInformation.vue';
import ComBoxBetwenConten from './ComBoxBetwenConten.vue';

import Message from "primevue/message";
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
// const socket = inject("$socket")
const gv = inject("$gv")
const visible = ref(false)
const rs = inject('$reservation')
const loading = ref(false)
const dialogRef = inject("dialogRef");
const moment = inject("$moment")
const isSaving = ref(false);
const selectedRoomRates = ref([])
const use_tax = ref({})
const current_date = moment(new Date).toDate()
const stay = ref({})
const stay_reservation = ref({})
const showCheckUpdateFutureStayRoomRate = ref(false)
const updateFutureRoomRate = ref(false)
const futureRoomRates = ref([])
const RoomRateCalculation = ref({})
const isCheckedTrue = ref(true);
const roomData = computed(() => {
    if (stay_reservation.value?.rooms_data) {
        return JSON.parse(stay_reservation.value?.rooms_data)
    }else if(stay.value?.rooms_data){
        return JSON.parse(stay.value?.rooms_data)
    }
    return []
})

function checkChangePax(){
    console.log(selectedRoomRates.value[0])
    if (doc.value.is_manual_change_pax) {
        if(stay.value){
           doc.value.adult = stay.value.adult
           doc.value.child = stay.value.child  
        }else{
            doc.value.adult = selectedRoomRates.value[0].adult
            doc.value.child = selectedRoomRates.value[0].child 
        }
       
        get_room_rate_breakdown()
    }
}
const discountType = ref([
    { label: $t('Percent'), value: 'Percent' },
    { label: $t('Amount'), value: 'Amount' },
]);
function getTooltip() {
    var html = ''
    var index = 0
    roomData.value.forEach(e => {
        index = index + 1
        if (index > 3) {
            html = html + ` ${e.room_type}/${e.room_number ? e.room_number : ''}<br/>`
        }

    });
    return `${html}`

}
let arrival_date = moment(stay_reservation?.value.arrival_date).format("YYYY-MM-DD")
arrival_date = moment(arrival_date).toDate()

const tax_rule = computed(() => {
    if (doc.value?.tax_rule_data) {
        return JSON.parse(doc.value?.tax_rule_data)
    }
    return []
})
function onUseTax1Change(value) {

    doc.value.tax_1_rate = use_tax.value.use_tax_1 ? 0 : tax_rule.value.tax_1_rate
    get_room_rate_breakdown()

}
function onUseTax2Change(value) {

    doc.value.tax_2_rate = use_tax.value.use_tax_2 ? 0 : tax_rule.value.tax_2_rate
    get_room_rate_breakdown()

}
function onUseTax3Change(value) {

    doc.value.tax_3_rate = use_tax.value.use_tax_3 ? 0 : tax_rule.value.tax_3_rate
    get_room_rate_breakdown()
}


const doc = ref({
    discount_type: 'Percent',
});


// use new rate calcuate from server

function get_room_rate_breakdown(){
    if (loading.value==true){
        return 
    }
   
    loading.value = true
    
    const room_rate_data = {
        rate_type:doc.value.rate_type,
        tax_rule:doc.value.tax_rule,
        rate_include_tax:doc.value.rate_include_tax,
        tax_1_rate:doc.value.tax_1_rate,
        tax_2_rate:doc.value.tax_2_rate,
        tax_3_rate:doc.value.tax_3_rate,
        input_rate:doc.value.input_rate,
        discount_type:doc.value.discount_type,
        discount:doc.value.discount,
        adult:doc.value.adult,
        child:doc.value.child,
        is_package:doc.value.is_package,
        package_charge_data:doc.value.package_charge_data
    }
    postApi("generate_room_rate.get_room_rate_calculation", { room_rate_data: room_rate_data},"",false)
            .then(result => {
                RoomRateCalculation.value = result.message
                loading.value = false
            }).catch(err=>{
                loading.value = false
            })
}


// end use new rate calujclation from server

function onSelectRateType(selected) {
 
    if (doc.value.is_manual_rate == 0 && selected) {
 
        postApi('reservation.get_room_rate', {
            property: doc.value.property,
            rate_type: selected,
            room_type: doc.value.room_type_id,
            business_source: doc.value.business_source,
            date: doc.value.date,
            include_tax_rule: true

        }, "", false)
            .then((result) => {
                doc.value.input_rate = result.message.rate
                const tax_rule_data = result.message.tax_rule || ""
                doc.value.tax_1_rate = tax_rule_data?.tax_1_rate || 0
                doc.value.tax_2_rate = tax_rule_data?.tax_2_rate || 0
                doc.value.tax_3_rate = tax_rule_data?.tax_3_rate || 0
                doc.value.tax_rule = tax_rule_data?.name || ""
                // doc.value.rate_include_tax = tax_rule_data?.name || ""
                
                use_tax.value.use_tax_1 = doc.value.tax_1_rate>0
                use_tax.value.use_tax_2 = doc.value.tax_2_rate>0
                use_tax.value.use_tax_3 = doc.value.tax_3_rate>0

                doc.value.tax_rule_data = JSON.stringify(tax_rule_data)
                doc.value.allow_discount = result.message.allow_discount || 0
                doc.value.allow_user_to_edit_rate = result.message.allow_user_to_edit_rate

                if(doc.value.allow_discount==0){
                    doc.value.discount = 0
                }
               

                // TODO get package check with posting rule

                doc.value.is_package = result.message.is_package 
                doc.value.package_charge_data = result.message.package_charge_data
                if (!doc.value.package_charge_data){
                    doc.value.package_charge_data = '[]'
                    doc.value.is_package = 0
                }

                doc.value.is_house_use = result.message.is_house_use
                doc.value.is_complimentary = result.message.is_complimentary

                if (doc.value.is_house_use || doc.value.is_complimentary){
                    doc.value.discount = 0
                }
               
                
                get_room_rate_breakdown()

            })
    } else {
       
        getApi("utils.get_rate_type_info", { name: selected })
            .then(result => {
                const tax_rule_data = result.message.tax_rule
                doc.value.tax_1_rate = tax_rule_data?.tax_1_rate || 0
                doc.value.tax_2_rate = tax_rule_data?.tax_2_rate || 0
                doc.value.tax_3_rate = tax_rule_data?.tax_3_rate || 0
                doc.value.tax_rule = tax_rule_data?.name || ""
                doc.value.tax_rule_data = JSON.stringify(tax_rule_data)
                doc.value.allow_discount = result.message.allow_discount || 0
                if(doc.value.allow_discount==0){
                    doc.value.discount = 0
                }
                doc.value.allow_user_to_edit_rate = result.message.allow_user_to_edit_rate
                if (result.message.is_complimentary==1 || result.message.is_house_use==1){
                    doc.value.input_rate = 0
                    doc.value.is_manual_rate = 0
                }
                

                doc.value.is_package = result.message.is_package 
                doc.value.package_charge_data = result.message.package_charge_data
                if (!doc.value.package_charge_data){
                    doc.value.package_charge_data = '[]'
                    doc.value.is_package = 0
                }

                doc.value.is_house_use = result.message.is_house_use
                doc.value.is_complimentary = result.message.is_complimentary

                if (doc.value.is_house_use || doc.value.is_complimentary){
                    doc.value.discount = 0
                }

                get_room_rate_breakdown()


            })
    }
   
            
}

function onUseManualRate() {
    
    if (doc.value.is_manual_rate == 0) {
       
        postApi('reservation.get_room_rate', {
            property: doc.value.property,
            rate_type: doc.value.rate_type,
            room_type: doc.value.room_type_id,
            business_source: doc.value.business_source,
            date: doc.value.date
        }, "", false)
            .then((result) => {
                doc.value.input_rate = result.message.rate
                get_room_rate_breakdown()
            })
    }


}

function onSave() {

    //prepare room rate name send to api
    let room_rate_names = []
    let reservation_stay_names = []

    if (futureRoomRates.value && futureRoomRates.value.length > 0) {

        if (updateFutureRoomRate.value == true) {
            room_rate_names = futureRoomRates.value.map(d => d["name"])
            reservation_stay_names = Array.from(new Set(futureRoomRates.value.map(d => d["reservation_stay"])))
        }

    } else {
        room_rate_names = selectedRoomRates.value.map(d => d["name"])
        reservation_stay_names = Array.from(new Set(selectedRoomRates.value.map(d => d["reservation_stay"])))
    }


    isSaving.value = true;
    if (!doc.value.tax_rule_data){
        doc.tax_rule_data = null
    }
    postApi('reservation.update_room_rate', {
        room_rate_names: room_rate_names,
        data: doc.value,
        reservation_stays: reservation_stay_names
    }, "Edit room rate successfully")
        .then((doc) => {
            isSaving.value = false
            window.postMessage({action:"ReservationList"},"*")
            window.postMessage({action:"ReservationStayList"},"*")
            window.postMessage({action:"GuestLedger"},"*")
            window.postMessage({action:"GuestLedgerTransaction"},"*")
            window.postMessage({action:"Reports"},"*")
            rs.getRoomRate(window.reservation)
            dialogRef.value.close(doc.message)
        })
        .catch((error) => {
            isSaving.value = false;

        });

}
onMounted(() => {
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    stay.value = dialogRef.value.data.reservation_stay
    stay_reservation.value = dialogRef.value.data.reservation

    showCheckUpdateFutureStayRoomRate.value = dialogRef.value.data.show_check_update_future_stay_room_rate

    if (dialogRef.value.data.selected_room_rate) {

        doc.value = JSON.parse(JSON.stringify(dialogRef.value.data.selected_room_rate))

        //this condition below is true only if user edit rate from run night audit
 
        futureRoomRates.value = dialogRef.value.data.future_room_rates;

    } else if (dialogRef.value.data.selected_room_rates?.length > 0) {
 
        selectedRoomRates.value = dialogRef.value.data.selected_room_rates
       
        doc.value = JSON.parse(JSON.stringify(dialogRef.value.data.selected_room_rates[0]))
 

    }

    use_tax.value = {
        use_tax_1: doc.value.tax_1_rate > 0,
        use_tax_3: doc.value.tax_3_rate > 0,
        use_tax_2: doc.value.tax_2_rate > 0
    }

    //check if account code allow discount
    getApi("utils.get_rate_type_info", { name: doc.value.rate_type })
            .then(result => {
                doc.value.allow_discount = result.message.allow_discount || 0
                doc.value.allow_user_to_edit_rate = result.message.allow_user_to_edit_rate || 0
 
            })

    get_room_rate_breakdown()

});

function onOpenLink(data) {
    window.postMessage("view_reservation_stay_detail" + "|" + data, '*')
}

</script>
<style scoped>.h-edoor-35 {
    height: 36.5px;
}
::v-deep .top-label-style{
    display: block !important;
}
::v-deep .p-fieldset .p-fieldset-legend{
    background-color: white;
}
</style>
