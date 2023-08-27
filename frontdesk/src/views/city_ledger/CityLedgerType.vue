<template>
 
        <ComHeader isRefresh @onRefresh="loadData()">
            <template #start>
                <div class="text-2xl">City Ledger Account Type</div>
            </template>
            <template #end>
              <Button class="border-none" label=" Add New City Ledger Account Type" icon="pi pi-plus"  @click="onAddCityLedgerAccountType" />
            </template>
        </ComHeader>
        <div class="mb-3 w-20rem">
            <div class="flex w-full flex-wrap gap-2">
                <div class="p-input-icon-left w-full">
                    <i class="pi pi-search" />
                    <InputText class="w-full" v-model="filter.keyword" placeholder="Search" @input="onSearch" />
                </div>
            </div>
        </div>
        <div>
            <ComPlaceholder text="No Data" :loading="gv.loading"  :is-not-empty="(data?.filter((r)=>r.city_ledger_type.toLowerCase().includes((filter.keyword ||'').toLowerCase()))).length > 0">
            <DataTable showGridlines :value="data?.filter((r)=>r.city_ledger_type.toLowerCase().includes((filter.keyword ||'').toLowerCase()))" tableStyle="min-width: 50rem" @row-click=" ">
                <Column field="city_ledger_type" header="City Ledger Type"></Column>
                <Column field="owner" header="Owner"></Column>
                <Column field="note" class="w-6" header="Note"></Column>
                <Column header="Action" class="text-center w-10rem">
                <template #body="slotProps">
                    <div class="flex gap-2 justify-center">
                    <Button @click="onEdit(slotProps.data)" icon="pi pi-pencil text-sm" iconPos="right" class="h-2rem border-none" label="Edit" rounded />
                    <Button @click="onDelete(slotProps.data.name)"  severity="danger"  icon="pi pi-trash text-sm" iconPos="right" class="h-2rem border-none" label="Delete" rounded />
                    </div>
                </template>
            </Column>
            </DataTable>
            </ComPlaceholder>
        </div>
       
</template>
<script setup>
import { inject, ref, getDocList, onMounted,deleteDoc,useConfirm,useDialog } from '@/plugin'
import ComAddCityLedgerType from "@/views/city_ledger/components/ComAddCityLedgerType.vue"
const gv = inject("$gv")
const data = ref([])
const filter = ref({})
const confirm = useConfirm()
const dialog = useDialog()

function onEdit (selected){ 
 dialog.open(ComAddCityLedgerType, {
    props: {
        header: `Edit City Ledger Type`,
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
    data:selected,
    onClose:(options) => {
            const data = options.data;
            if(data){
				loadData()
			}
        }
});  
}

function onDelete (name){ 
        confirm.require({
        message: 'Are you sure you want to delete guest?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            // loading.value = false
             deleteDoc('City Ledger Type',name)
                 .then(() =>{
                    loadData()
                    loading.value = false
                 } ).catch((err)=>{
                    loading.value = false
                 })         
        },
    });
}

function loadData() {
    gv.loading = true
    getDocList('City Ledger Type', {
        fields: ['name','city_ledger_type', 'note','owner'],
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
function onAddCityLedgerAccountType(){
    dialog.open(ComAddCityLedgerType, {
        props: {
            header: `Add New City Ledger Account Type`,
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top'
        },
        onClose:(options) => {
            const data = options.data;
            if(data){
				loadData()
			}
        }
    });  
}
onMounted(() => {
    loadData()
})

</script>