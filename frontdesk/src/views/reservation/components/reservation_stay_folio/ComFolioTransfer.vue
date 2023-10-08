<template>
    <ComDialogContent :loading="loading" @onOK="onOk" :hideButtonClose="true" @onClose="onClose">
        <div class="grid">
            <div class="col-12">

                <ComReservationStayPanel class="h-full" title="Transferring To">
                    <template #content>
                        <Message v-if="!(selectedFolio?.value)" :closable="false" severity="warn">
                            <div class="flex align-items-center">Please select folio number</div>
                        </Message>
                        <Message v-else :closable="false" severity="success" icon="pi pi-exclamation-circle">
                            <div class="flex align-items-center"> You Are Select {{ selectedFolio?.value }} - {{
                                selectedFolio?.description }}</div>
                        </Message>
                        <label>Folio Number</label>
                        <ComAutoComplete @onSelected="onSelectFolioNumber" v-model="data.new_folio_number"
                            placeholder="Select Folio" doctype="Reservation Folio" class="auto__Com_Cus w-full"
                            :filters="{ 'property': property_name, status: 'Open',is_active_reservation: 1, 'name': ['!=', data.folio_number] }" />
                        <label>Note</label>
               
                        <Textarea class="w-full" placeholder="Note" v-model="data.note" autoResize rows="2" />
                        <div class="mt-2">
                            <Checkbox  
                                    v-model="data.change_room_nmumber" :binary="true" :trueValue="1"
                                    inputId="change_room_number"
                                    :falseValue="0" />

                        <label for="change_room_number" class="ml-2   font-medium cursor-pointer ">
                            Change Room Number to Room Number of the target folio
                        </label>
                       
                        </div>
                        <div class="mt-2">
                            <Checkbox  
                                    v-model="data.change_guest" :binary="true" :trueValue="1"
                                    inputId="change_guest"
                                    :falseValue="0" />

                            <label for="change_guest" class="ml-2 font-medium cursor-pointer ">
                                Change Guest to the Guest of the target folio
                            </label>
                        </div>
                             

                    </template>
                </ComReservationStayPanel>
            </div>
            <div class="col-12">
                <ComReservationStayPanel class="h-full" title="Item Transferring">
                    <template #content>
                        <DataTable :rowClass="rowClass" class="p-datatable-sm mt-2" :value="data.folio_transaction"
                            tableStyle="">
                            <Column field="name" header="Folio Number"></Column>
                            <Column field="account_name" header="Account"></Column>
                            <Column header="Amount">
                                <template #body="{ data }">
                                    <CurrencyFormat :value="data.total_amount" />
                                </template>
                            </Column>
                        </DataTable>
                    </template>
                </ComReservationStayPanel>
            </div>
        </div>
    </ComDialogContent>
</template>
<script setup>
import { ref, onMounted, inject, useConfirm, postApi, useToast } from "@/plugin"
import ComReservationStayPanel from '@/views/reservation/components/ComReservationStayPanel.vue';
const dialogRef = inject("dialogRef");
const confirm = useConfirm()
const property_name = window.property_name
const data = ref({})
const selectedFolio = ref({})
const loading = ref(false)
const toast = useToast()

function onSelectFolioNumber(data) {
    selectedFolio.value = data

}
const rowClass = (data) => {
    return [{ 'border-left-3 bg-green-50 border-green-500': data.name }];

};
onMounted(() => {
    data.value = dialogRef.value.data
})

function onOk() {
    if (!data.value.new_folio_number) {
        toast.add({ severity: 'warn', summary: "Folio Transfer", detail: "Please select new folio number to transfer", life: 3000 })
        return
    }
    confirm.require({
        message: `Are you sure want to transfer these folio transaction to folio ` + selectedFolio.value.value,
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            loading.value = true
            postApi("reservation.folio_transfer", {
                data: {
                    folio_transaction: data.value.folio_transaction.filter(r => r.name).map(r => r.name),
                    folio_number: data.value.folio_number,
                    new_folio_number: data.value.new_folio_number,
                    note: data.value.note || " ", 
                    reservation: data.value.reservation,
                    reservation_stay: data.value.reservation_stay,
                    property: window.property_name,
                    change_guest:data.value.change_guest || 0,
                    change_room:data.value.change_room_nmumber || 0,
                }

            }).then((r) => {
                loading.value = false
                dialogRef.value.close("refresh_data")
                window.socket.emit("RefreshData", { reservation_stay: data.value.reservation_stay, action: "refresh_reservation_stay" })
            }).catch((err) => {
                loading.value = false
            })


        },

    });


}
</script>