<template>
    <ComDialogContent @close="onClose" :loading="isSaving" hideButtonOK titleButtonClose="Close Shift">
        <div class="grid justify-between">
            <div class="col-6">
                {{ doc }}
            <table>
                <tbody>
                    <template v-for="(item, index) in doc?.cash_float" :key="index">
                        <ComStayInfoNoBox label="Name" :value="item?.name" />
                        <ComStayInfoNoBox label="Payment Method" :value="item?.payment_method" />
                        <ComStayInfoNoBox label="Exchange Rate" :value="item?.exchange_rate" />
                        <ComStayInfoNoBox label="Input Amount" :value="item?.input_amount" />
                        <ComStayInfoNoBox label="Opening Amount" :value="item?.opening_amount" />
                        <ComStayInfoNoBox label="Input System Close Amount" :value="item?.input_system_close_amount" />
                        <ComStayInfoNoBox label="System Close Amount" :value="item?.system_close_amount" />
                        <ComStayInfoNoBox label="Input Close Amount" :value="item?.input_close_amount" />
                        <ComStayInfoNoBox label="Close Amount" :value="item?.close_amount" />
                        <ComStayInfoNoBox label="Input Different Amount" :value="item?.input_different_amount" />
                        <ComStayInfoNoBox label="Different Amount" :value="item?.different_amount" />
                        <ComStayInfoNoBox label="Currency" :value="item?.currency" />
                        <ComStayInfoNoBox label="Currency Symbol" :value="item?.currency_symbol" />
                        <ComStayInfoNoBox label="Currency Precision" :value="item?.currency_precision" />
                        <ComStayInfoNoBox label="Payment Type Group" :value="item?.payment_type_group" />
                        <ComStayInfoNoBox label="Parent" :value="item?.parent" />
                        <ComStayInfoNoBox label="Parent Field" :value="item?.parentfield" />
                        <ComStayInfoNoBox label="Parent Type" :value="item?.parenttype" />
                        <ComStayInfoNoBox label="Doctype" :value="item?.doctype" />
                    </template>
                </tbody>
            </table> 
            </div>
            <div class="col-6">
                <table>
                    <tbody>
                        <ComStayInfoNoBox label="Name" :value="doc.name" />
                        <ComStayInfoNoBox label="Owner" :value="doc.owner"/>
                        <ComStayInfoNoBox label="Creation" :value="doc.creation"/>
                        <ComStayInfoNoBox label="Modified" :value="doc.modified"/>
                        <ComStayInfoNoBox label="Modified By" :value="doc.modified_by"/>
                        <ComStayInfoNoBox label="Modified By" :value="doc.modified_by"/>
                        <ComStayInfoNoBox label="Posting Date" :value="doc.posting_date"/>
                        <ComStayInfoNoBox label="Is Edoor Shift" :value="doc.is_edoor_shift"/>
                        <ComStayInfoNoBox label="Total Opening Amount" :value="doc.total_opening_amount"/>
                        <ComStayInfoNoBox label="Total System Close Amount" :value="doc.total_system_close_amount"/>
                        <ComStayInfoNoBox label="Total Close Amount" :value="doc.total_close_amount"/>
                        <ComStayInfoNoBox label="Total Different Amount" :value="doc.total_different_amount"/>
                        <ComStayInfoNoBox label="Is Closeed" :value="doc.is_closed"/>
                        <ComStayInfoNoBox label="Outlet" :value="doc.outlet"/>
                    </tbody>
                </table>
            </div>
        </div>
        <div class="grid justify-between">
            <div v-for="(item, index) in doc?.cash_float" :key="index" class="col-6">
                <span class="text-500 font-italic">{{ item.payment_method }}</span>     
                <ComInputCurrency classCss="w-full" v-model="item.input_close_amount" id="input_amount" :currency="item.currency_symbol" />
            </div>
        </div>
        <div class="col-3 p-0">
            <div class="flex justify-end">
                <div class="flex flex-column grow p-2 rounded-lg shadow-charge-total border">
                    <span class="text-500 uppercase text-sm text-end">Total</span>
                    <span class="text-xl line-height-2 font-semibold text-end">
                        <CurrencyFormat :value="total_close_amount"/>
                    </span>
                </div>
            </div>
        </div>
    </ComDialogContent>
</template>
<script setup>
    import{ref, inject, getDoc, onMounted,useToast, computed} from "@/plugin"
    const toast = useToast()
    const doc = ref({})
    const gv = inject("$gv")
    const moment = inject("$moment")
    const isSaving = ref(false);
    const current_date = moment(new Date).format('DD-MM-YYYY');

    getDoc("Cashier Shift", gv.cashier_shift?.name).then((result)=>{
        doc.value = result
    })

    const total_close_amount = computed(() => {
    if (doc?.value.cash_float) {

        return doc?.value.cash_float.reduce((n, r) => n + (r.input_close_amount / r.exchange_rate), 0);
    }
    return 0;
}) 

    function onClose(){
        isSaving.value = true;
    }
</script>
