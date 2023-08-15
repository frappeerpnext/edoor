<template>
    <ComDialogContent hideButtonOK :hideButtonClose="true">
        <TabView>
            <TabPanel header="Account Information">
                <div>
                    {{ data }}
                </div>
            </TabPanel>
            <TabPanel header="City Ledger Transaction">
                <ComCityLedgerTransaction :name="data?.name"/>
            </TabPanel>
            <TabPanel header="Document">
                <div>
                    Document
                </div>
            </TabPanel>
        </TabView>

        <template #footer-left>

            <Button @click="onEditcityLedger">Edit</Button>
            <Button @click="onDeletecityLedger">Delete</Button>
        </template>
    </ComDialogContent>
</template>
<script setup>
import { ref, getDoc, inject, useDialog, onMounted } from '@/plugin'
import ComAddCityLedgerAccount from '@/views/city_ledger/components/ComAddCityLedgerAccount.vue';
import ComCityLedgerTransaction from '@/views/city_ledger/components/ComCityLedgerTransaction.vue';
const dialogRef = inject("dialogRef")
const dialog = useDialog()
const data = ref()
const loading = ref(false)

function onEditcityLedger() {
    dialog.open(ComAddCityLedgerAccount, {
        data: {
            name: data.value.name,
        },
        props: {
            header: `Edit Ledger Account`,
            style: {
                width: '50vw',
            },
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true,
            closeOnEscape: false,
            position: 'top'
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
                loadData()
                loading.value = false
            }
        }
    });
}
function onDeletecityLedger() {
    alert('onDelete')
}

function loadData() {
    loading.value = true
    getDoc('City Ledger', dialogRef.value.data.name)
        .then((r) => {
            data.value = r
            loading.value = false
        }).catch((err) => {
            loading.value = false
        })
}

onMounted(() => {
    loadData()

})

</script>