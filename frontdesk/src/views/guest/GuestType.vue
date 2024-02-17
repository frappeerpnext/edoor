<template>
    <div>
        <ComHeader colClass="col-6" isRefresh @onRefresh="onRefresh()">
            <template #start>
                <div class="text-2xl">Guest Type</div>
            </template>
            <template #end>
                <Button class="border-none" :label="isMobile ? 'Add New' : 'Add New Guest Type' " icon="pi pi-plus" @click="onAddNewGuestType" />
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
            <ComPlaceholder text="No Data" :loading="gv.loading"
                :is-not-empty="(data?.filter((r) => r.customer_group_en.toLowerCase().includes((filter.keyword || '').toLowerCase()))).length > 0">
                <DataTable 
                showGridlines
                :value="data?.filter((r) => r.customer_group_en.toLowerCase().includes((filter.keyword || '').toLowerCase()))"
                tableStyle="min-width: 50rem">
                    <Column field="customer_group_en" header="Guest type"></Column>
                    <Column field="owner" header="Owner"></Column>
                    <Column field="note" class="w-6" header="Note"></Column>
                    <Column header="Action" headerClass="text-center w-10rem">
                        <template #body="slotProps">
                            <div class="flex gap-2 justify-center">
                                <Button @click="onEdit(slotProps.data)" icon="pi pi-pencil text-sm" iconPos="right" class="h-2rem border-none" label="Edit" rounded />
                                <Button @click="onDelete(slotProps.data.name)" severity="danger" icon="pi pi-trash text-sm" iconPos="right" class="h-2rem border-none" label="Delete" rounded />
                            </div>
                        </template>
                    </Column>
                </DataTable>
            </ComPlaceholder>
        </div>
    </div>
</template>
<script setup>
import { inject, ref, getDocList, onMounted, useDialog, useConfirm, deleteDoc ,onUnmounted } from '@/plugin'
import ComAddGuestType from "@/views/guest/components/ComAddGuestType.vue"
const gv = inject("$gv")
const isMobile = ref(window.isMobile) 
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
                window.socket.emit("GuestType", window.property_name)
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
const onRefresh = debouncer(() => {
    loadData();
}, 500);
function loadData(show_loading=true) {
    gv.loading = show_loading
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
function debouncer(fn, delay) {
    var timeoutID = null;
    return function () {
        clearTimeout(timeoutID);
        var args = arguments;
        var that = this;
        timeoutID = setTimeout(function () {
            fn.apply(that, args);
        }, delay);
    };
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
    loadData(false)
    window.socket.on("GuestType", (arg) => {
        if (arg == window.property_name) {
            setTimeout(function(){
                loadData(false)
            },3000) 
        }
    })
})
onUnmounted(() => {
    window.socket.off("GuestType");
})

</script>

 