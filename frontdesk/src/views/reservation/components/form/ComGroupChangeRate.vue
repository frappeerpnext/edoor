<template>
    <ComDialogContent :hideButtonClose="true"  :hideButtonOK="true" :loading="loading">
        <div>Apply To</div>
        <div class="gap-3">
            <div class="flex align-items-center">
                <RadioButton inputId="" name="" value=""/>
                <label for="" class="ml-2">Full Stay</label>
            </div>
            <div class="flex align-items-center">
                <RadioButton inputId="" name="" value=""/>
                <label for="" class="ml-2">From</label>
                <div class="flex">
                    <Calendar v-model="data.arrival_date" :selectOtherMonths="true" class="p-inputtext-sm depart-arr w-full border-round-xl"
                        dateFormat="dd-mm-yy" showIcon showButtonBar />
                        <div> To </div>
                    <Calendar v-model="data.departure_date" :selectOtherMonths="true" class="p-inputtext-sm depart-arr w-full border-round-xl"
                    dateFormat="dd-mm-yy" showIcon showButtonBar /> 
                </div>
            </div>
        </div>  
        <div>Rate type</div>
        <div class="flex">
            <label>Rate type</label>
            <ComSelect data.room_type placeholder="Gerneral" doctype="Room Type"/>
            <div>
                <Checkbox v-model="data.Checkbox" :binary="true" />
                <label>Overwrite Room Rate with Rate Type</label>
            </div>
            <Button>Save</Button>
        </div>
        <div>
            <div>define New Rate</div>
            <div class="flex">
                <label>Rate: </label>
                <InputText type="text"/>
                <div>
                    <Checkbox v-model="data.rate_include_tax" :binary="true" />
                    <label>Rate Include Tax</label>
                    <Button>Save</Button>
                </div>
            </div>
            
        </div>
        <div>
            <div>Tax Exempt</div>
            <div class="flex">
                <div class="flex">
                
                    <div>
                        <Checkbox v-model="data" :binary="true" />
                        <label>Tax 1(10.00%)</label>
                    </div>
                    <div>
                        <Checkbox v-model="data" :binary="true" />
                        <label>Service Charge(2.00%)</label>
                    </div>
                </div>
                <div class="flex">
                    <div>
                        <Checkbox v-model="data" :binary="true" />
                        <label>ACC. Tax(0.00%)</label>
                    </div>
                    <div>
                        <Checkbox v-model="data" :binary="true" />
                        <label>vat(0.00%)</label>
                    </div>
                </div>
                <Button>Save</Button>
            </div>
            
        </div>
    </ComDialogContent>
</template>
<script setup>
import { ref } from '@/plugin';
const loading = ref(false)
const data = ref({})
</script>