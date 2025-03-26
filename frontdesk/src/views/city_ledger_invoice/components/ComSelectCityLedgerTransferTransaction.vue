<template>
    <ComDialogContent titleButtonOK="Save Selection" @onOK="onSaveSelection" hideButtonClose :hideIcon="false">


        <Grid>
            <Col>

            <Card class="m-0 p-0" :pt="{'body': { class: 'py-0' }}">
                <template #content>
                    <strong class="link_line_action1">{{ doc?.name }}</strong>
                    <p>{{ doc?.city_ledger_name }}</p>
                    <p>{{ doc?.city_ledger_type }}</p>
                </template>
            </Card>
            </Col>
            <Col>
                <Card class="m-0 p-0" :pt="{'body': { class: 'py-0' }}">
                <template #content>
                    <Stack row>
                        <p>Contact Name:</p>
                        <strong>{{ doc?.contact_name }}</strong>
                    </Stack>
                    <Stack row>
                    
                    <p>Phone number:</p>
                    <strong> {{ doc?.phone_number }} {{ doc?.contact_phone_number }}</strong>
                    </Stack>
                    <Stack row>
                    
                    <p>Email:</p>
                    <strong> {{ doc?.email_address }}</strong>
                </Stack>
                </template>
            </Card>
        </Col>
        </Grid>

        <Panel header="City Ledger Transactions" class="mt-4">
            {{ selectedTransactions }}
            <ComSelectFolioTransactionList :city_ledger="city_ledger" v-model:selectedData="selectedTransactions"/>
        </Panel>
    </ComDialogContent>




</template>
<script setup>
import { ref, inject, useDialog, onMounted, getDocument } from '@/plugin'

import ComSelectFolioTransactionList from '@/views/city_ledger_invoice/components/ComSelectFolioTransactionList.vue';
const selectedTransactions = ref([])
const gv= inject("$gv")
const dialogRef = inject("dialogRef")
const doc = ref()
const loading = ref(true)

const dialog = useDialog()

const city_ledger = ref()


function onSaveSelection(){
    
    if(selectedTransactions.value.length == 0){
        gv.toast('warn', 'Please select city ledger transaction')

        return;
    }
}


onMounted(async () => {
    city_ledger.value = dialogRef.value.data.city_ledger
    const res = await getDocument("City Ledger", city_ledger.value)
    if (!res.error) {
        doc.value = res.data
    }
    loading.value = false;

});
</script>