<template>
    <ComDialogContent titleButtonOK="Open" titleButtonClose="Cancel" @onClose="dialogRef.close()" @onOK="onOpen">
        <ComSelect v-model="shift.shift_name" :clear="false" @onSelected="onSelectShift"  doctype="Shift Type" placeholder="Shift Name" optionLabel="shift_name" optionValue="name" extraFields="start_time,end_time"/> 
        <table>
            <thead>
                <tr>
                    <td><label>Type</label></td>
                    <td><label>Amount</label></td>
                    <td><label>Amount {{ setting?.currency?.name }}</label></td>
                </tr>
            </thead>
            <tbody>
                <tr v-for="(p, index) in shift.cash_float" :key="index">
                    <td>
                        {{ p.payment_method }}
                    </td>
                    <td>
                        <InputText  v-model="p.input_amount" />
                        <div v-if="p.exchange_rate!=1">
                            Excahnge Rate:  {{ p.exchange_rate }}
                        </div>
                    </td>
                    <td>
                        <div class="p-inputtext-pt text-center border-1 border-white h-12">
                            <CurrencyFormat :value="(p.input_amount/p.exchange_rate) || 0 "/>
                        </div>
                    </td>
                </tr>
                <tr>
                    <td>
                        Total
                    </td>
                    <td></td>
                    <td>
                        <div class="p-inputtext-pt text-center border-1 border-white h-12">
                            <CurrencyFormat :value="shift.cash_float.reduce((n, d) => n + ((d.input_amount/d.exchange_rate) || 0),0)"/>
                        </div>
                    </td>
                </tr>
            </tbody>
            Note: <InputText v-model="shift.open_note" />
        </table>

        <!-- <div class="flex gap-2">
            <Button class="border-none" @click="onOpen">Open</Button>
            <Button class="border-none" @click="dialogRef.close()">Cancel</Button>
        </div> -->
    </ComDialogContent>
</template>
<script setup>
    import {ref,inject} from "@/plugin"
    import { useConfirm } from "primevue/useconfirm";
    import { useToast } from "primevue/usetoast";
    import ComDialogContent from '@/components/form/ComDialogContent.vue'
    const confirm = useConfirm();
    const dialogRef = inject("dialogRef");
    const frappe = inject('$frappe');
    const gv = inject("$gv")
    const db = frappe.db();
    const socket = inject("$socket")
    const toast = useToast();
    const selectedShift = ref({})
    const setting = JSON.parse(localStorage.getItem("edoor_setting"))
    const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
    const payment_types = setting?.payment_type.filter(r=>r.allow_cash_float==1)
    const shift = ref({
       working_day:working_day.name,
        pos_profile:setting.pos_profile.name,
        cash_float:[]
    })
    payment_types.forEach(p => {
        shift.value.cash_float.push({
            payment_method:p.payment_type,
            exchange_rate :p.exchange_rate,
            input_amount:0,
            currency:p.currency
        })
    });
    const onSelectShift = (d)=>{
        selectedShift.value = d
    }
    const onOpen = () =>{
        if(!shift.value.shift_name){
            toast.add({ severity: 'warn', summary: 'Open Shift', detail: "Please select shift name", life: 3000 })
            return
        }
        const total = shift.value.cash_float.reduce((n, d) => n + ((d.input_amount/d.exchange_rate) || 0),0)
        confirm.require({
        message: 'Are you sure you want to open shift with amount ' + total + "?",
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
          db.createDoc("Cashier Shift", shift.value)
          .then((doc)=>{
            toast.add({ severity: 'success', summary: 'Open Shift', detail: "Open cashier shift successuflly", life: 3000 })
            gv.cashier_shift = doc
            
            socket.emit("UpdateCashierShift", doc);
            dialogRef.value.close();
          })
          .catch((err)=>{
            gv.showErrorMessage(err)
          })
        },
    });
    }
</script>
<style scoped>
table{
    width: 100%;
}
</style>