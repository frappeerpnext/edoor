<template>
    {{ data }}
    <ComDialogContent :hideButtonClose="true"  :hideButtonOK="true" :loading="loading">
        <div>Apply To</div>
        <div class="gap-3">
            <div class="flex align-items-center">
                <RadioButton inputId="full" name="change_date_type" value="full_stay" v-model="data.change_date_type"/>
                <label for="full" class="ml-2">Full Stay</label>
            </div>
            
            <div class="flex align-items-center">
                <RadioButton inputId="from"  name="change_date_type" value="selected_date" v-model="data.change_date_type" />
                <label  for="from"   class="ml-2" >From</label>
                <div class="flex">
                    <Calendar v-model="data.arrival_date" :selectOtherMonths="true" class="p-inputtext-sm depart-arr w-full border-round-xl"
                        dateFormat="dd-mm-yy" showIcon showButtonBar :disabled="data.change_date_type=='full_stay'" />
                        <div> To </div>
                    <Calendar v-model="data.departure_date" :selectOtherMonths="true" class="p-inputtext-sm depart-arr w-full border-round-xl"
                    dateFormat="dd-mm-yy" showIcon showButtonBar :disabled="data.change_date_type=='full_stay'" /> 
                </div>
            </div>
        </div>  
        <div>Rate type</div>
        <div class="flex">
            <label>Rate type</label>
            <ComSelect v-model="data.rate_type" placeholder="Please select room type" doctype="Rate Type"   />
            <div>
                <Checkbox v-model="data.is_overwrite_room_rate_and_rate_type" :binary="true" />
                <label>Overwrite Room Rate with Rate Type</label>
            </div>
            <Button>Save</Button>
        </div>
        <div>
            <div>define New Rate</div>
            <div class="flex">
                <label>Rate: </label>
                <InputText type="text" v-model="data.rate"/>
                <div>
                    <Checkbox inputId="rateIncludeTax"  v-model="data.is_rate_include_tax" :binary="true" />
                    <label for="rateIncludeTax">Rate Include Tax</label>
                    <Button>Save</Button>
                </div>
            </div>
            
        </div>
        <div class="flex">
            <div>Tax Exempt</div>
                <ComAutoComplete v-model="data.tax_rule" placeholder="Please select tax rule" doctype="Tax Rule"/>
                <Button>Save</Button>
        </div>
    </ComDialogContent>
</template>
<script setup>
import { ref,onMounted,inject } from '@/plugin';
import Enumerable from 'linq'
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