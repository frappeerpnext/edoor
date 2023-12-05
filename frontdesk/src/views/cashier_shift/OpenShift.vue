<template>
    <ComDialogContent :titleButtonOK="shift.name?'Save':'Open'" titleButtonClose="Cancel" @onClose="dialogRef.close()" @onOK="onOpen" :loading="loading">
 
        <ComSelect v-model="shift.shift_name" :clear="false" @onSelected="onSelectShift" doctype="Shift Type"
            placeholder="Shift Name" optionLabel="shift_name" optionValue="name" extraFields="start_time,end_time" />
        <div class="bg-card-info border-round-xl p-3 h-full mt-3">
            <table>
                <thead>
                    <tr>
                        <td class="pr-2"><label>Type</label></td>
                        <td class="px-2 text-end"><label>Amount</label></td>
                        <td class="pl-2 text-end"><label>Amount {{ setting?.currency?.name }}</label></td>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(p, index) in shift.cash_float" :key="index">
                        <td class="pr-2">
                            {{ p.payment_method }}
                        </td>
                        <td class="px-2 text-end">
                            <div class="w-full flex justify-end">
                                <div class="relative w-15rem">
                                    <InputNumber class="text-end w-full w-15rem" v-model="p.input_amount"
                                        :minFractionDigits="0" :maxFractionDigits="p.currency_precision" mode="currency"
                                        :currency="p.currency" :locale="p.locale" />
                                    <ComOpenShiftExchangeRate :item="p" />
                                </div>

                            </div>
                        </td>

                        <td class="pl-2">
                            <div class="p-inputtext-pt text-end border-1 border-white">
                                <CurrencyFormat :value="(p.input_amount / p.exchange_rate) || 0" class="w-10rem" />
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td class="pr-2"></td>
                        <td class="px-2 text-end">
                            <label>Total</label>
                        </td>
                        <td class="pl-2">
                            <div class="p-inputtext-pt text-end border-1 border-white h-12">
                                <CurrencyFormat
                                    :value="shift.cash_float.reduce((n, d) => n + ((d.input_amount / d.exchange_rate) || 0), 0)" />
                            </div>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
        <div class="w-full mt-3">
            <label>Note:</label> <br />
            <Textarea v-model="shift.opened_note" rows="4" class="w-full" />
        </div>

    </ComDialogContent>
</template>
<script setup>
import { ref, inject, onMounted,getDoc,createUpdateDoc } from "@/plugin"
import { useConfirm } from "primevue/useconfirm";
import { useToast } from "primevue/usetoast";
import ComDialogContent from '@/components/form/ComDialogContent.vue'
import ComOpenShiftExchangeRate from "./components/ComOpenShiftExchangeRate.vue";
const confirm = useConfirm();
const dialogRef = inject("dialogRef");
 
const gv = inject("$gv")
 
const toast = useToast();
const selectedShift = ref({})
const setting = window.setting

const payment_types = setting?.payment_type.filter(r => r.allow_cash_float == 1)
const loading = ref(false)
 
const shift = ref({
    working_day: window.working_day.name,
    pos_profile: setting.pos_profile.name,
    cash_float: []
})
payment_types.forEach(p => {
    shift.value.cash_float.push({
        payment_method: p.payment_type,
        exchange_rate: p.exchange_rate,
        input_amount: 0,
        currency: p.currency,
        locale: p.locale,
        currency_precision: p.currency_precision
    })
});
const onSelectShift = (d) => {
    selectedShift.value = d
}

const onOpen = () => {
    if (!shift.value.shift_name) {
        toast.add({ severity: 'warn', summary: 'Open Shift', detail: "Please select shift name", life: 3000 })
        return
    }
    if(!shift.value.name){
        const total = shift.value.cash_float.reduce((n, d) => n + ((d.input_amount / d.exchange_rate) || 0), 0)
    
    
    confirm.require({
        message: 'Are you sure you want to open shift with amount ' + gv.currencyFormat(total || 0) + "?",
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
          saveData()
        },
    });
    }else {
        saveData()
    }
    
}

function saveData(){
 
    loading.value = true
 
    createUpdateDoc("Cashier Shift", shift.value,shift.value.name?"Save data successfully":"Open cashier shift successuflly")
                .then((doc) => {
                    gv.cashier_shift = doc

                    window.working_day.cashier_shift = {
                        creation:doc.creation,
                        name:doc.name,
                        shift_name:doc.shift_name
                    }
                    localStorage.setItem("edoor_working_day",JSON.stringify(window.working_day))


                    window.socket.emit("UpdateCashierShift", doc);
                    loading.value = false
                    dialogRef.value.close(doc);
                }).catch((e)=>{
                   console.log(e)
                    loading.value = false
                })
}

onMounted(() => {
    if ( dialogRef.value.data?.name){
        getDoc("Cashier Shift", dialogRef.value.data.name).then((result) => {
            shift.value = result
    })
}
 
    

})


</script>
<style scoped>table {
    width: 100%;
}</style>