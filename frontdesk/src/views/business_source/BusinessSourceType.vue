<template>
    <div>
        <ComHeader colClass="col-6" isRefresh @onRefresh="Refresh()">
            <template #start>
                <div class="text-xl md:text-2xl">Business Source Type</div>
            </template>
            <template #end>
                <Button class="border-none" :label="isMobile ? 'Add New' : 'Add New Business Source Type' " icon="pi pi-plus" @click="onAddNewBusinessSourceType" />
            </template>
        </ComHeader>
        <div class="mb-3 w-full md:w-20rem">
            <div class="flex w-full flex-wrap gap-2 ">
                <div class="p-input-icon-left w-full">
                    <i class="pi pi-search" />
                    <InputText class="w-full" v-model="filter.keyword" placeholder="Search" @input="onSearch" />
                </div>
            </div>
        </div>
        <div class="">
            <ComPlaceholder text="No Data" :loading="gv.loading" :is-not-empty="gv.search(data, filter.keyword).length > 0">
                <!-- data?.filter((r)=>r.business_source_type.toLowerCase().includes((filter.keyword ||'').toLowerCase()))  -->
                <DataTable showGridlines :value="gv.search(data, filter.keyword)" tableStyle="min-width: 50rem">
                    <Column field="business_source_type" header="Business Source Type"></Column>
                    <Column header="Owner">
                        <template #body="slotProps">
                            <div v-if="slotProps?.data && slotProps?.data?.owner">
                                <template v-for="(item) in slotProps.data?.owner?.split('@')[0]" :key="index">
                                    <span>{{ item }}</span>
                                </template>
                            </div>  
                        </template>
                    </Column>
                    <Column field="note" class="w-6" header="Note"></Column>
                    <Column header="Action" class="text-center w-10rem">
                        <template #body="slotProps">
                            <div class="flex gap-2 justify-center">
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
import { inject, ref, getDocList, onMounted, useDialog, useConfirm, deleteDoc,computed } from '@/plugin'
import ComAddBusinessSourceType from "@/views/business_source/components/ComAddBusinessSourceType.vue"
const gv = inject("$gv")
const dialog = useDialog()
const data = ref([])
const filter = ref({})
const loading = ref(false)
const confirm = useConfirm()
const isMobile = ref(window.isMobile) 
function onDelete(name) {
    confirm.require({
        message: 'Are you sure you want to delete business source type?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            deleteDoc('Business Source Type', name)
                .then(() => {
                    loadData()
                    loading.value = false
                })
                .catch((err) => {
                    loading.value = false
                })
        },
    });
}
function onEdit(edit) {
    dialog.open(ComAddBusinessSourceType, {
        props: {
            header: `Edit Business Source Type: ${edit.name}`,
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top',
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
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
    getDocList('Business Source Type', {
        fields: ['business_source_type', 'note', 'owner', 'name'],
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
const Refresh = debouncer(() => {
    loadData()
}, 500);

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

function onAddNewBusinessSourceType() {
    dialog.open(ComAddBusinessSourceType, {
        props: {
            header: `Add New Business Source Type`,
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top',
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
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
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
})

</script>