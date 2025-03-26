<template>
    <ComDialogContent @onOK="onSave" hideButtonClose titleButtonOK="Save" :hideIcon="false" :loading="loading">
        {{ doc }}
        {{ editdata }}
        <Grid>
            <Col>
            <Stack>
                <div>
                    <label for="posting_date">{{ $t('Posting Date') }}</label>
                    <Calendar :selectOtherMonths="true" inputId="posting_date" v-model="doc.posting_date" class="w-full"
                        dateFormat="dd-mm-yy" showIcon showButtonBar selectOtherMonths panelClass="no-btn-clear" />
                </div>
                <div>
                    <label for="reference_number">{{ $t('Reference Number') }}</label>
                    <InputText id="reference_number" class="w-full" type="text" v-model="doc.reference_number" />
                </div>

                <div>
                    {{ doc.city_ledger }}
                    <label for="posting_date">{{ $t('City Ledger Account') }}</label>
                    <ComAutoComplete v-model="doc.city_ledger" :placeholder="$t('City Ledger Account')"
                        @onSelected="onSelectCityLedgerAccount" doctype="City Ledger"
                        :filters="{ 'property': doc.property }" class="auto__Com_Cus w-full" />
                </div>
            </Stack>
            </Col>
            <Col>
            <div>
                <label>{{ $t('Note') }}</label><br />
                <Textarea v-model="doc.note" rows="5" :placeholder="$t('Note')" cols="30"
                    class="w-full border-round-xl" />
            </div>
            </Col>
        </Grid>


        <Panel header="Folio Transaction" class="mt-4">


            <ComSelectFolioTransactionList :city_ledger="doc.city_ledger"
                v-model:selectedData="selectedFolioTransactions" />
        </Panel>

    </ComDialogContent>
</template>
<script setup>
import { ref, inject, postData ,updateDoc, onMounted , getDoc } from "@/plugin"
import ComSelectFolioTransactionList from "@/views/city_ledger_invoice/components/ComSelectFolioTransactionList.vue"
import { i18n } from '@/i18n';
import { useConfirm } from "primevue/useconfirm";
import { useDialog } from 'primevue/usedialog';
const dialog = useDialog();
const confirm = useConfirm();
const { t: $t } = i18n.global;
const moment = inject("$moment")
const loading = ref(false)
const doc = ref({
    property: window.property_name,
    posting_date: moment.utc(window.current_working_date).toDate(),
})

const dialogRef = inject('dialogRef')
const editdata = ref(dialogRef.value.data)
const selectedFolioTransactions = ref([])

function onSelectCityLedgerAccount(d) {

}

async function onSave() {
  
    if (selectedFolioTransactions.value.length == 0) {
       
        const result = await new Promise((resolve) => {

            confirm.require({
                message: "You do not select any transaction for this city ledger invoice. Do you want to continue?",
                header: "Confirmation",
                accept: () => resolve(true),
                reject: () => resolve(false),
            });
        });

        if (!result) {
            return;
        }
    }




    loading.value = true;

    const data = {
        doc: JSON.parse(JSON.stringify(doc.value)),
        folio_transactions: selectedFolioTransactions.value.map(r=>r.name)
    }
    data.doc.posting_date = moment.utc(data.doc.posting_date).format("YYYY-MM-DD")
    const res = await postData("city_ledger_invoice.add_new_city_ledger_invoice", {
        data: data
    }, "", true, "edoor.edoor.doctype.city_ledger_invoice.");
    // updateDoc('City Ledger Invoice', data.value.name, savedData).then((r) => {
        
    // })
    loading.value = false;
    if(res.data){
        dialogRef.value.close(res.data)
    }
    }
    onMounted(() => {
        if (dialogRef.value.data.name) {
             getDoc("City Ledger Invoice",dialogRef.value.data.name).then(d=>{
            console.log(d)
            doc.value = d
        }) 
        }
})
</script>