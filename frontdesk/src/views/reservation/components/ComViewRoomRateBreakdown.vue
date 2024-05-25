<template>
     <ComDialogContent hideButtonOK dialogClass="max-h-screen-newres overflow-auto"  :loading="isSaving" hideButtonClose>
<div class="grid p-2 overflow-auto">       
                    <div class="col-12 pb-0">
                <div class="grid justify-end ">
                    <div class="col">
                        <ComReservationStayPanel title="Room Rate" >  
                            <template #content>  
                        <table>
                    <tbody>
                        
                        <ComStayInfoNoBox label="Base Rate"
                            :value="data?.room_rate_data?.room_charge_data.rate" isCurrency="true" valueClass="text-end" />
                            <ComStayInfoNoBox label="Discount" :value="data?.room_rate_data?.room_charge_data.discount_amount" isCurrency="true" valueClass="text-end" />    
                            <ComStayInfoNoBox v-if="data?.room_rate_data?.room_charge_data.rate_include_tax" label="Rate Include Tax" valueClass="text-end">
                                <div class="flex gap-2"> 
                             <Checkbox      v-model="data.room_rate_data.room_charge_data.rate_include_tax" :binary="true"
                                    trueValue="Yes" falseValue="No" disabled /> 
                                </div>    
                              
                           </ComStayInfoNoBox>
                             <ComStayInfoNoBox v-if="data?.room_rate_data?.room_charge_data.tax_1_rate > 0" :label="($t(data?.room_rate_data?.room_charge_data.tax_1_name ?? '') || '') + ' ' + (data?.room_rate_data?.room_charge_data.tax_1_rate || 0) + '%'" valueClass="text-end">
                                <div class="flex gap-2"> 
                                    <CurrencyFormat :value="data?.room_rate_data?.room_charge_data.tax_1_amount || 0 " />
                                <Checkbox input-id="tax-1" v-model="isCheckedTrue" :binary="true" disabled />
                                </div>
                            </ComStayInfoNoBox>
                             <ComStayInfoNoBox v-if="data?.room_rate_data?.room_charge_data.tax_2_rate > 0" :label="($t(data?.room_rate_data?.room_charge_data.tax_2_name ?? '') || '') + ' ' + (data?.room_rate_data?.room_charge_data.tax_2_rate || 0) + '%'" valueClass="text-end">
                                <div class="flex gap-2"> 
                                    <CurrencyFormat :value="data?.room_rate_data?.room_charge_data.tax_2_amount || 0 " />
                                <Checkbox input-id="tax-2" v-model="isCheckedTrue" @input="onUseTax2Change" 
                                                            :binary="true" disabled />
                                </div>
                            </ComStayInfoNoBox>
                        <ComStayInfoNoBox v-if="data?.room_rate_data?.room_charge_data.tax_3_rate > 0" :label="($t(data?.room_rate_data?.room_charge_data.tax_3_name ?? '') || '') + ' ' + (data?.room_rate_data?.room_charge_data.tax_3_rate || 0) + '%'" valueClass="text-end">
                                <div class="flex gap-2"> 
                                    <CurrencyFormat :value="data?.room_rate_data?.room_charge_data.tax_3_amount || 0 " />
                                <Checkbox input-id="tax-3"  v-model="isCheckedTrue" :binary="true" disabled />
                                </div>
                            </ComStayInfoNoBox>
                               <ComStayInfoNoBox  v-if=" data?.room_rate_data?.room_charge_data.tax_1_rate > 0 || data?.room_rate_data?.room_charge_data.tax_2_rate > 0 || data?.room_rate_data?.room_charge_data.tax_3_rate > 0" 
                                label="Total Tax" 
                                :value="data?.room_rate_data?.room_charge_data.total_tax" isCurrency="true" valueClass="text-end" />  
                                <ComStayInfoNoBox   
                                label="Total Rate" 
                                :value="data?.room_rate_data?.room_charge_data.total_amount" isCurrency="true" valueClass="text-end" />        
                    </tbody>
                </table>
<div>
    
</div>


            </template>
                    </ComReservationStayPanel>  
                    </div>
                    <div class="col-12">
                    <ComReservationStayPanel title="Package" > 
                        <template #content>     
                        <div class="grid ">
                            <template v-for="item in data?.room_rate_data.package_charge_data" :key="item.account_name" >
                            <div class="col"  v-if="item.quantity  > 0" >
                                <Fieldset  >
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
                                    <ComStayInfoNoBox label="Discount" :value="item.discount_amount" isCurrency="true" valueClass="text-end" />    
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
                        </template>
                        </div>
                        </template>
                    </ComReservationStayPanel>
                </div>
                    <!--  -->
                </div>
            </div>
                </div>
            </ComDialogContent>            
</template>
<script setup>
import {inject,ref,onMounted} from "@/plugin"
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
const isCheckedTrue = ref(true);
const data = ref()
const dialogRef = inject("dialogRef");
onMounted(()=>{
    data.value = dialogRef.value.data.data
})
</script>
<style scoped>
::v-deep .top-label-style{
    display: block !important;
}
::v-deep .p-fieldset .p-fieldset-legend{
    background-color: #f4f5fa;
}

::v-deep .p-fieldset  .p-fieldset-content , .p-fieldset{
    background-color: #f4f5fa;
}

</style>