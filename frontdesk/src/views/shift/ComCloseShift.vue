<template>
    <ComDialogContent @close="onClose" :loading="isSaving" hideButtonOK>
        <div v-for="(item, index) in doc?.cash_float" :key="index">
            {{ item }}
        </div>
        
        <div class="grid justify-between">
            <div class="col-6">
            <table>
                <tbody>
                    <ComStayInfoNoBox  label="Profile" :value="doc.pos_profile" />
                    <ComStayInfoNoBox  label="Business Branch" :value="doc.business_branch" />
                </tbody>
            </table> 
            </div>
            <div class="col-6">
                <table>
                    <tbody>
                    <ComStayInfoNoBox  label="Date" :value="moment(doc.creation).format('DD-MM-yyyy')"/>
                    </tbody>
                </table>
            </div>
        </div>
        <label>Cash Float</label>
        <div class="grid gap-0">
            <div v-for="(item, index) in doc?.cash_float" :key="index" class="col-12 md:col-6 lg:col-4">
                {{ item.currency }}
                <ComInputCurrency classCss="w-full" v-model="item.input_close_amount" id="input_amount" />
            </div>
        </div>
    </ComDialogContent>
    
        
    <Button>Close Shift</Button>
</template>
<script setup>
    import{ref, inject, getDoc, onMounted,useToast} from "@/plugin"
    const toast = useToast()
    const doc = ref({})
    const gv = inject("$gv")
    const moment = inject("$moment")
    const isSaving = ref(false);
 
    getDoc("Cashier Shift", gv.cashier_shift?.name).then((result)=>{
        doc.value = result
    })
    function onClose(){
        isSaving.value = true;
    }
</script>