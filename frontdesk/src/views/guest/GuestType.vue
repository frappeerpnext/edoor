<template>
    <div>
        <ComHeader isRefresh @onRefresh="loadData()">
            <template #start>
                <div class="text-2xl">Guest Type</div>
            </template>me
            <template #end>
                <Button class="border-none" label="Add New Guest Type" icon="pi pi-plus" @click="onAddNewGuestType" />
            </template>
        </ComHeader>
        <div class="mb-3 w-20rem">
            <div class="flex w-full flex-wrap gap-2 ">
                <div class="p-input-icon-left w-full">
                    <i class="pi pi-search" />
                    <InputText class="w-full" v-model="filter.keyword" placeholder="Search" @input="onSearch" />
                </div>
            </div>
        </div>
        <div class="rounded-xl">
            <ComPlaceholder text="No Data" :loading="loading"
                :is-not-empty="(data?.filter((r) => r.customer_group_en.toLowerCase().includes((filter.keyword || '').toLowerCase()))).length > 0">
                <DataTable
                    :value="data?.filter((r) => r.customer_group_en.toLowerCase().includes((filter.keyword || '').toLowerCase()))"
                    tableStyle="min-width: 50rem" 
                    showGridlines>
                    <Column field="customer_group_en" header="Guest type"></Column>
                    <Column field="owner" header="Owner"></Column>
                    <Column field="note" class="w-6" header="Note"></Column>
                    <Column header="Action" headerClass="text-right">
                        <template #body="slotProps">
                            <div class="flex gap-2 justify-end">
                                <Button @click="onEdit(slotProps.data)" icon="pi pi-pencil text-sm" iconPos="right"
                                    class="h-2rem border-none" label="Edit" rounded />
                                <Button @click="onDelete(slotProps.data.name)" severity="danger" icon="pi pi-trash text-sm"
                                    iconPos="right" class="h-2rem border-none" label="Delete" rounded />
                            </div>
                        </template>
                    </Column>
                </DataTable>
            </ComPlaceholder>
        </div>
    </div>
</template>
<script setup>
import { inject, ref, getDocList, onMounted, useDialog, useConfirm, deleteDoc } from '@/plugin'
import ComAddGuestType from "@/views/guest/components/ComAddGuestType.vue"
const gv = inject("$gv")
const dialog = useDialog()
const data = ref([])
const filter = ref({})
const loading = ref(false)
const confirm = useConfirm()
function onDelete(name) {
    confirm.require({
        message: 'Are you sure you want to delete guest type?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            deleteDoc('Customer Group', name)
                .then(() => {
                    loadData()
                    loading.value = false

                }).catch((err) => {
                    loading.value = false
                })
        },
    });
}
function onEdit(edit) {
    dialog.open(ComAddGuestType, {
        props: {
            header: `Edit Guest Type: ${edit.name}`,
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
        data: edit,
        onClose: (options) => {
            const data = options.data;
            if (data) {
                loadData()
            }
        }
    });
}
function loadData() {
    gv.loading = true
    getDocList('Customer Group', {
        fields: ['customer_group_en', 'note', 'owner', 'name'],
        limit: 10000,
    })
        .then((doc) => {
            data.value = doc
            gv.loading = false
        })
        .catch((error) => {
            gv.loading = false

        });
}
function onAddNewGuestType() {
    dialog.open(ComAddGuestType, {
        props: {
            header: `Add New Guest Type`,
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top'
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
                loadData()
            }
        }
    });
}
onMounted(() => {
    loadData()
})

</script>

 