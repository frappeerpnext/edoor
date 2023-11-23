<template>
    <ComDialogContent :hideButtonClose="true" :hideButtonOK="true" :loading="loading">
        <Message>Change rate is affect only current and future stay date</Message>
       
        <ComReservationStayPanel title="Apply To">
            <template #content>
                <div class="gap-3">
                    <div class="flex align-items-center">
                        <RadioButton inputId="full" name="change_date_type" value="full_stay"
                            v-model="data.change_date_type" />
                        <label for="full" class="ml-2">Full Stay</label>
                    </div>
                    <div class="flex align-items-center w-full mt-3">
                        <div class="w-2">
                            <RadioButton inputId="from" name="change_date_type" value="selected_date"
                                v-model="data.change_date_type" />
                            <label for="from" class="ml-2 mr-3">From</label>
                        </div>
                        <div class="flex align-items-center gap-3 w-full">
                            <Calendar v-model="data.arrival_date" :selectOtherMonths="true"
                            :minDate="data.min_date"
                            :maxDate="data.max_date"
                                class="p-inputtext-sm depart-arr w-full border-round-xl" dateFormat="dd-mm-yy" showIcon
                                showButtonBar :disabled="data.change_date_type == 'full_stay'" />
                            <div> To </div>
                            <Calendar v-model="data.departure_date" :selectOtherMonths="true"
                            :minDate="data.min_date"
                            :maxDate="data.max_date"
                            
                                class="p-inputtext-sm depart-arr w-full border-round-xl" dateFormat="dd-mm-yy" showIcon
                                showButtonBar :disabled="data.change_date_type == 'full_stay'" />
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
                        <ComSelect v-model="data.rate_type" class="w-full" placeholder="Please Select Rate Type"
                            @onSelected="onRateTypeChange" doctype="Rate Type" />
                    </div>
                    <div class="col pt-4">
                        <div class="py-2 gap-2 flex items-center w-full p-dropdown-label p-inputtext p-placeholder">
                            <Checkbox inputId="rate_type_input" v-model="data.is_override_rate" :binary="true" :trueValue="1" :falseValue="0" />
                            <label class="cursor-pointer" for="rate_type_input" >Overwrite Room Rate with Rate Type</label>
                        </div>
                    </div>
                </div>
                
                <div class="grid" v-if="rate_type_data?.tax_rule"><hr class="my-2">
                    <div class="col-12">
                        <div class="py-2 gap-2 flex items-center w-3 p-dropdown-label  ms-2">
                            
                            <Checkbox :disabled="!rate_type_data.allow_user_to_change_tax" inputId="rate_include_tax" v-model="rate_type_data.is_rate_include_tax" :binary="true" :trueValue="1"
                            :falseValue="0" />
                        <label class="cursor-pointer" for="rate_include_tax" >include Rate Tax</label>
                        </div>
                        
                    </div>
                    
                    <div class="col-4 pt-0" v-if="rate_type_data.tax_rule.tax_1_rate">
                        <div class="py-2 gap-2 flex items-center w-full p-dropdown-label p-inputtext p-placeholder">
                        <Checkbox :disabled="!rate_type_data.allow_user_to_change_tax" inputId="rate_rule_1" v-model="rate_type_data.tax_1_rate" :binary="true"
                            :trueValue="rate_type_data.tax_rule.tax_1_rate" :falseValue="0" />
                        <label class="cursor-pointer" for="rate_rule_1"> {{ rate_type_data.tax_rule.tax_1_name }} {{ rate_type_data.tax_rule.tax_1_rate }}%</label>
</div>
                    </div>
                    <div class="col-4 pt-0" v-if="rate_type_data.tax_rule.tax_2_rate">
                        <div class="py-2 gap-2 flex items-center w-full p-dropdown-label p-inputtext p-placeholder">
                        <Checkbox :disabled="!rate_type_data.allow_user_to_change_tax" inputId="rate_role_2" v-model="rate_type_data.tax_2_rate" :binary="true"
                            :trueValue="rate_type_data.tax_rule.tax_2_rate" :falseValue="0" />
                        <label class="cursor-pointer" for="rate_role_2" > {{ rate_type_data.tax_rule.tax_2_name }} {{ rate_type_data.tax_rule.tax_2_rate }}%</label>
</div>
                    </div>
                    <div class="col-4 pt-0" v-if="rate_type_data.tax_rule.tax_3_rate">
                        <div class="py-2 gap-2 flex items-center w-full p-dropdown-label p-inputtext p-placeholder">
                        <Checkbox :disabled="!rate_type_data.allow_user_to_change_tax" inputId="rate_role_3" v-model="rate_type_data.tax_3_rate" :binary="true"
                            :trueValue="rate_type_data.tax_rule.tax_3_rate" :falseValue="0" />
                        <label class="cursor-pointer" for="rate_role_3" > {{ rate_type_data.tax_rule.tax_3_name }} {{ rate_type_data.tax_rule.tax_3_rate }}%</label>
</div>
                    </div>
                </div>
                <hr class="my-2">
                <div class="mx-2 pt-1 flex justify-content-end">
                        <Button class="border-none btn-ok_ss" @click="onChangeRateType">
                            <span class="flex align-items-center">
                                <img class="pi pi-check-circle mr-2" :src="BtnOkIcon" style="height: 13px;" />
                                Save
                            </span>
                        </Button>
                    </div>

            </template>
        </ComReservationStayPanel>
        <ComReservationStayPanel title="Define New Rate" class="mt-3">
            <template #content>
                <div class="grid items-center">
                    <div class="col-5 pt-0">
                        <label for="input_amount">Rate </label>
                        <ComInputCurrency classCss="w-full"  v-model="data.new_rate" id="input_amount" />
                    </div>
                    <div class="col-7 pt-4">
                        <div class="py-2 gap-2 flex items-center w-full p-dropdown-label p-inputtext p-placeholder">
                            <Checkbox inputId="rateIncludeTax" v-model="data.is_rate_include_tax" :binary="true" :trueValue="1" :falseValue="0" />
                            <label class="cursor-pointer" for="rateIncludeTax">Rate Include Tax</label>
                        </div>
                    
                    </div>
                    
                    
                </div>
                <hr class="my-2">
                <div class="mx-2 pt-2 flex justify-content-end">
                        <Button class="border-none btn-ok_ss" @click="onChangeNewRate">
                            <span class="flex align-items-center ">
                                <img class="pi pi-check-circle mr-2" :src="BtnOkIcon" style="height: 13px;" />
                                Save
                            </span>
                        </Button>
                    </div>
            </template>
        </ComReservationStayPanel>
        
        <ComReservationStayPanel title="Group Discount" class="mt-3">
            <template #content>
                <Message>Discount is affect to any rate type that allow discount</Message>
                <div class="grid items-center">
                    <div class="col-5 pt-0">
                        <label for="dis_type">Discount Type</label>
                                <div class="w-full">
                                    <ComSelect class="w-full min-w-full" id="dis_type" 
                                        v-model="data.discount_type" :options="['Percent', 'Amount']" :clear="false" />
                                </div>
                            
                    </div>
                    <div class="col pt-0">
                        <label for="minmaxfraction">Discount</label>
                                <div class="w-full">
                                    <InputNumber class="w-full" inputClass="w-full" 
                                        v-model="data.discount" inputId="minmaxfraction" id="discount" :minFractionDigits="2"
                                        :maxFractionDigits="10" v-if="data.discount_type=='Percent'" />
                                        <ComInputCurrency classCss="w-full"  v-model="data.discount_amount"  v-else />
                                </div>
                    </div>
                 
                    
                </div>
                <hr class="my-2">
                <div class="mx-2 pt-1 flex justify-content-end">
                        <Button class="border-none btn-ok_ss" @click="onGroupDiscount">
                            <span class="flex align-items-center">
                                <img class="pi pi-check-circle mr-2" :src="BtnOkIcon" style="height: 13px;" />
                                Save
                            </span>
                        </Button>
                    </div>
            </template>
        </ComReservationStayPanel>
        <ComReservationStayPanel title="Group Change Tax" class="mt-3" v-if="tax_rules.length>0">
            <template #content>
 
                <div class="grid items-center justify-content-between">
                    <div class="grid w-full" v-for="(t, index) in tax_rules" :key="index">
                        <div class="col-12 -mb-2 ms-2">
                        <span class="text-lg font-medium">{{ t.name }}</span>
                        </div>
                        <div class="col-3">
                            <div class="py-2 gap-2 flex items-center w-full p-dropdown-label p-inputtext p-placeholder">
                            <Checkbox :disabled="t.allow_user_to_change_tax==0" inputId="rateIncludeTax_change_tax" v-model="t.is_rate_include_tax" :binary="true" :trueValue="1" :falseValue = "0"  />
                            <label class="cursor-pointer" for="rateIncludeTax_change_tax" >Rate Include Tax</label>
                            </div>
                        </div>
                        
                        <div class="col-3" v-if="t.tax_1_rate>0">
                            <div class="py-2 gap-2 flex items-center w-full p-dropdown-label p-inputtext p-placeholder">
                            <Checkbox :disabled="t.allow_user_to_change_tax==0" inputId="rateIncludeTax_change_tax1" v-model="t.use_tax_1_rate" :binary="true" :trueValue="t.tax_1_rate" :falseValue = "0"  />
                            <label class="cursor-pointer" for="rateIncludeTax_change_tax1" >{{ t.tax_1_name }} ({{ t.tax_1_rate }}%)</label>
                        </div>
                    </div>
                        
                        <div class="col-3" v-if="t.tax_2_rate>0">
                            <div class="py-2 gap-2 flex items-center w-full p-dropdown-label p-inputtext p-placeholder">
                            <Checkbox :disabled="t.allow_user_to_change_tax==0" inputId="rateIncludeTax_change_tax2" v-model="t.use_tax_2_rate" :binary="true" :trueValue="t.tax_2_rate" :falseValue = "0"  />
                            <label class="cursor-pointer" for="rateIncludeTax_change_tax2" >{{ t.tax_2_name }} ({{ t.tax_2_rate }}%)</label></div>
                        </div>
                        <div class="col-3" v-if="t.tax_3_rate>0">
                            <div class="py-2 gap-2 flex items-center w-full p-dropdown-label p-inputtext p-placeholder">
                            <Checkbox :disabled="t.allow_user_to_change_tax==0" inputId="rateIncludeTax_change_tax3" v-model="t.use_tax_3_rate" :binary="true" :trueValue="t.tax_3_rate" :falseValue = "0"  />
                            <label class="cursor-pointer" for="rateIncludeTax_change_tax3" >{{ t.tax_3_name }} ({{ t.tax_3_rate }}%)</label></div>
                        </div>
                    </div>
                   
                   
                </div>
                <hr class="my-2"/>
                <div class="mx-2 pt-1 flex justify-content-end">
                        <Button class="border-none btn-ok_ss" @click="onGroupChangeTax">
                            <span class="flex align-items-center">
                                <img class="pi pi-check-circle mr-2" :src="BtnOkIcon" style="height: 13px;" />
                                Save
                            </span>
                        </Button>
                    </div>
            </template>
        </ComReservationStayPanel>

         
    </ComDialogContent>
</template>
<script setup>
import { ref, onMounted, inject, postApi, useToast, getApi ,useConfirm} from '@/plugin';
import Enumerable from 'linq'
import BtnOkIcon from '@/assets/svg/icon-save.svg'
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
const loading = ref(false)
const toast = useToast()
const data = ref({ change_date_type: 'full_stay', "discount_type":"Percent" })
const moment = inject("$moment")
const dialogRef = inject("dialogRef");
const rate_type_data = ref()
const stays = ref([])
const reservation = ref()
const confirm = useConfirm();
const tax_rules = ref([])
 

const onRateTypeChange = (rate_type) => {
    if (rate_type) {
        getApi("utils.get_rate_type_info", { name: rate_type })
            .then((result) => {
                rate_type_data.value = result.message
                if (result.message?.tax_rule) {
                    rate_type_data.value.tax_rule_name = result.message.tax_rule.name
                    rate_type_data.value.is_rate_include_tax = result.message.tax_rule.is_rate_include_tax
                    rate_type_data.value.tax_1_rate = result.message.tax_rule.tax_1_rate
                    rate_type_data.value.tax_2_rate = result.message.tax_rule.tax_2_rate
                    rate_type_data.value.tax_3_rate = result.message.tax_rule.tax_3_rate
                    rate_type_data.value.allow_user_to_change_tax = result.message.allow_user_to_change_tax

                } else {
                    clearRateTypeTax()
                }
            })
    } else {
        clearRateTypeTax()
    }
}

function clearRateTypeTax() {
    rate_type_data.value.tax_rule = ""
    rate_type_data.value.tax_1_rate = 0
    rate_type_data.value.tax_2_rate = 0
    rate_type_data.value.tax_3_rate = 0
}



onMounted(() => {
    stays.value = dialogRef.value.data.stays
    reservation.value = dialogRef.value.data.reservation

    data.value.arrival_date = Enumerable.from(stays.value).select(x => new Date(x.arrival_date)).min();
    data.value.departure_date = Enumerable.from(stays.value).select(x => new Date(x.departure_date)).max();
    data.value.departure_date = moment(data.value.departure_date).add(-1,'days').toDate()
    data.value.min_date= Enumerable.from(stays.value).select(x => new Date(x.arrival_date)).min();
    data.value.max_date= Enumerable.from(stays.value).select(x => new Date(x.departure_date)).max();
    data.value.max_date= moment(data.value.max_date).add(-1,'days').toDate()
    data.value.is_override_rate = 0

    getTaxRules()


})

function getTaxRules(){
    postApi("group_operation.get_group_tax_rules", {stays:stays.value.map(r=>r.name)},"",false)
    .then(result=>{
        tax_rules.value = result.message
    
    })
}

function onChangeRateType() {
    if (!data.value.rate_type) {
        toast.add({ severity: 'warn', summary: "Group Change Rate", detail: 'Please select rate type', life: 5000 })
        return
    }
    loading.value = true
    let start_date =  moment(data.value.arrival_date).format("yyyy-MM-DD")
    let end_date =  moment(data.value.departure_date).format("yyyy-MM-DD")
    if (data.value.change_date_type == 'full_stay'){
        start_date =  moment(data.value.min_date).format("yyyy-MM-DD")
        end_date =  moment(data.value.max_date).format("yyyy-MM-DD")
        
    }

    postApi("group_operation.group_change_rate_type", {
        data: {
            reservation:reservation.value,
            stays: stays.value.map(r=>r.name),
            start_date:start_date,
            end_date: end_date,
            rate_type: data.value.rate_type,
            is_override_rate: data.value.is_override_rate,
            tax_rule:rate_type_data.value.tax_rule_name,
            rate_include_tax:rate_type_data.value.is_rate_include_tax==1?"Yes":"No",
            tax_1_rate: rate_type_data.value.tax_1_rate,
            tax_2_rate: rate_type_data.value.tax_2_rate,
            tax_3_rate: rate_type_data.value.tax_3_rate,
            property:window.property_name
            
        }
    }).then(r => {
        loading.value = false
        //reload reservation after close
        //refresh reservation stay
        stays.value.forEach(s => {
             
            window.socket.emit("ReservationStayDetail",{reservation_stay:s.name})
        })
        
        dialogRef.value.close(reservation.value)
        
    }).catch(err => {
        loading.value = false
    })
}



function onChangeNewRate() {
    if((data.value.new_rate || 0)<0){
        toast.add({ severity: 'warn', summary: "Group Change Rate", detail: 'Room rate cannot less that 0', life: 5000 })
        return
    }
    if((data.value.new_rate || 0)==0){
        confirm.require({
        message: 'Are you sure you want to set room rate to 0?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        accept:()=>{
            onSubmitChangeRate()
        }
    });
    }else {
        onSubmitChangeRate()
    }
   
     
    
}

function onSubmitChangeRate(){
   
    loading.value = true
    let start_date =  moment(data.value.arrival_date).format("yyyy-MM-DD")
    let end_date =  moment(data.value.departure_date).format("yyyy-MM-DD")
    if (data.value.change_date_type == 'full_stay'){
        start_date =  moment(data.value.min_date).format("yyyy-MM-DD")
        end_date =  moment(data.value.max_date).format("yyyy-MM-DD")
        
    }

    postApi("group_operation.group_change_rate", {
        data: {
            reservation:reservation.value,
            stays: stays.value.map(r=>r.name),
            start_date:start_date,
            end_date: end_date,
            rate_include_tax:(data.value.is_rate_include_tax || 0)==1?"Yes":"No",
            property:window.property_name,
            rate:data.value.new_rate
        }
    }).then(r => {
        loading.value = false
        //reload reservation after close
        //refresh reservation stay
        stays.value.forEach(s => {
            window.socket.emit("ReservationStayDetail",{reservation_stay:s.name})
        })
        dialogRef.value.close(reservation.value)
        
    }).catch(err => {
        loading.value = false
    })
}

function onGroupDiscount(){
   
    let start_date =  moment(data.value.arrival_date).format("yyyy-MM-DD")
    let end_date =  moment(data.value.departure_date).format("yyyy-MM-DD")
    if (data.value.change_date_type == 'full_stay'){
        start_date =  moment(data.value.min_date).format("yyyy-MM-DD")
        end_date =  moment(data.value.max_date).format("yyyy-MM-DD")
        
    }

    if (data.value.discount_type == "Percent" && (data.value.discount || 0)<0 ){
        toast.add({ severity: 'warn', summary: "Group Change Rate", detail: 'Discount percentage must be between 0 to 100', life: 5000 })
        return
    } 
    
    if (data.value.discount_type == "Percent" && (data.value.discount || 0)>100 ){
        toast.add({ severity: 'warn', summary: "Group Change Rate", detail: 'Discount percentage must be between 0 to 100', life: 5000 })
        return
    } 

    loading.value = true

    postApi("group_operation.group_room_rate_discount", {
        data: {
            reservation:reservation.value,
            stays: stays.value.map(r=>r.name),
            start_date:start_date,
            end_date: end_date,
            property:window.property_name,
            discount_type:data.value.discount_type,
            discount:data.value.discount_type=="Percent"?data.value.discount:data.value.discount_amount
        }
    }).then(r => {
        loading.value = false
        //reload reservation after close
        //refresh reservation stay
        stays.value.forEach(s => {
            window.socket.emit("ReservationStayDetail",{reservation_stay:s.name})
        })
        dialogRef.value.close(reservation.value)
        
    }).catch(err => {
        loading.value = false
    })
}


function onGroupChangeTax(){

    let start_date =  moment(data.value.arrival_date).format("yyyy-MM-DD")
    let end_date =  moment(data.value.departure_date).format("yyyy-MM-DD")
    if (data.value.change_date_type == 'full_stay'){
        start_date =  moment(data.value.min_date).format("yyyy-MM-DD")
        end_date =  moment(data.value.max_date).format("yyyy-MM-DD")
        
    }
 

    loading.value = true

    postApi("group_operation.group_change_tax", {
        data: {
            reservation:reservation.value,
            stays: stays.value.map(r=>r.name),
            start_date:start_date,
            end_date: end_date,
            property:window.property_name,
            tax_rules:tax_rules.value
        }
    }).then(r => {
        loading.value = false
        //reload reservation after close
        //refresh reservation stay
        stays.value.forEach(s => {
            window.socket.emit("ReservationStayDetail",{reservation_stay:s.name})
        })
        dialogRef.value.close(reservation.value)
        
    }).catch(err => {
        loading.value = false
    })
}



</script>