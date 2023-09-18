<template>
    {{ data }}
    <ComDialogContent :hideButtonClose="true"  :hideButtonOK="true" :loading="loading">
        <ComReservationStayPanel title="Apply To">
            <template #content>
        <div class="gap-3">
            <div class="flex align-items-center">
                <RadioButton inputId="full" name="change_date_type" value="full_stay" v-model="data.change_date_type"/>
                <label for="full" class="ml-2">Full Stay</label>
            </div>
            <div class="flex align-items-center w-full mt-3">
                <div class="w-2">
                <RadioButton inputId="from"  name="change_date_type" value="selected_date" v-model="data.change_date_type" />
                <label  for="from"   class="ml-2 mr-3" >From</label>
                </div>
                <div class="flex align-items-center gap-3 w-full">
                    <Calendar v-model="data.arrival_date" :selectOtherMonths="true" class="p-inputtext-sm depart-arr w-full border-round-xl"
                        dateFormat="dd-mm-yy" showIcon showButtonBar :disabled="data.change_date_type=='full_stay'" />
                        <div> To </div>
                    <Calendar v-model="data.departure_date" :selectOtherMonths="true" class="p-inputtext-sm depart-arr w-full border-round-xl"
                    dateFormat="dd-mm-yy" showIcon showButtonBar :disabled="data.change_date_type=='full_stay'" /> 
                </div>
            </div>
        </div> 
        </template>
     </ComReservationStayPanel>
     <ComReservationStayPanel title="Rate type" class="mt-3">
        <template #content>
            <div class="grid items-center">
            <div class="col-5 pt-0">
            <label>Rate type</label>
            <ComSelect v-model="data.rate_type" class="w-full" placeholder="Please Select Rate Type" doctype="Rate Type"   />
            </div>
            <div class="col-6 pt-4">            
                <div class="py-2 gap-2 flex items-center w-full p-dropdown-label p-inputtext p-placeholder">
                <Checkbox v-model="data.is_overwrite_room_rate_and_rate_type" :binary="true" />
                <label>Overwrite Room Rate with Rate Type</label>
            </div>
            </div>
            <div class="pt-3">
                <Button class="border-none btn-ok_ss" v-if="!hideButtonOK" @click="onOK()" :label="titleButtonOK" :loading="loading">
                            <span class="flex align-items-center">
                                <img class="pi pi-check-circle mr-2"  :src="BtnOkIcon" style="height: 13px;"/>
                                Save
                            </span>
                        </Button> 
            </div>
            
            </div>

        </template>
    </ComReservationStayPanel>
    <ComReservationStayPanel title="Define New Rate" class="mt-3">
        <template #content>
            <div class="grid items-center">

            <div class="col-5 pt-0">
                <label>Rate </label>
                <InputText class="w-full" type="text" v-model="data.rate"/>
            </div>
            <div class="col-6 pt-4 ms-2">
                <div  class="py-2 gap-2 flex items-center w-full p-dropdown-label p-inputtext p-placeholder">
                    <Checkbox inputId="rateIncludeTax"  v-model="data.is_rate_include_tax" :binary="true" />
                    <label for="rateIncludeTax">Rate Include Tax</label>
                </div>
            </div>
            <div class="pt-3">
                <Button class="border-none btn-ok_ss" v-if="!hideButtonOK" @click="onOK()" :label="titleButtonOK" :loading="loading">
                            <span class="flex align-items-center">
                                <img class="pi pi-check-circle mr-2"  :src="BtnOkIcon" style="height: 13px;"/>
                                Save
                            </span>
                        </Button>  
            </div>
            </div>
        </template>    
    </ComReservationStayPanel>
    <ComReservationStayPanel title="Tax Exempt" class="mt-3">
        <template #content>
            <div class="grid items-center justify-content-between">
                <div class="col-11 py-0">
                    <label for="rateIncludeTaxRule">tax rule</label>
                    <ComAutoComplete inputId="rateIncludeTaxRule" class="w-full" v-model="data.tax_rule" placeholder="Please select tax rule" doctype="Tax Rule"/>
                </div>
                <div class="pt-4">
                    <Button class="border-none btn-ok_ss" v-if="!hideButtonOK" @click="onOK()" :label="titleButtonOK" :loading="loading">
                        <span class="flex align-items-center">
                            <img class="pi pi-check-circle mr-2"  :src="BtnOkIcon" style="height: 13px;"/>
                                Save
                        </span>
                    </Button> 
                </div>
            </div>
        </template>
    </ComReservationStayPanel>
    </ComDialogContent>
</template>
<script setup>
import { ref,onMounted,inject } from '@/plugin';
import Enumerable from 'linq'
import BtnOkIcon from '@/assets/svg/icon-save.svg' 
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
const loading = ref(false)
const data = ref({change_date_type:'full_stay'})
const dialogRef=inject("dialogRef")
const change_rate = ref([])
onMounted(()=>{
    change_rate.value=dialogRef.value.data
    data.value.arrival_date = Enumerable.from(change_rate.value).select(x => new Date(x.arrival_date)).min();
    data.value.departure_date = Enumerable.from(change_rate.value).select(x => new Date(x.departure_date)).max();
})
</script>