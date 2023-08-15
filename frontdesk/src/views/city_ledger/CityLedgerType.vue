<template>
 
        <ComHeader isRefresh @onRefresh="loadData()">
            <template #start>
                <div class="text-2xl">City Ledger Account Type</div>
            </template>
            <template #end>
              <Button label=" Add New City Ledger Account Type" icon="pi pi-plus" severity="warning" outlined @click="onAddCityLedgerAccountType" />
            </template>
        </ComHeader>
        <div class="mb-3">
            <div class="flex flex-wrap gap-2">
                <span class="p-input-icon-left">
                    <i class="pi pi-search" />
                    <InputText v-model="filter.keyword" placeholder="Search" @input="onSearch" />
                </span>
            </div>
        </div>
        <DataTable  :value="data?.filter((r)=>r.city_ledger_type.toLowerCase().includes((filter.keyword ||'').toLowerCase()))" tableStyle="min-width: 50rem" @row-click=" ">
            <Column field="city_ledger_type" header="City Ledger Type"></Column>
            <Column field="note" header="Note"></Column>
            <Column field="owner" header="Owner"></Column>
            <Column header="">
             <template #body="slotProps">
                <i class="pi pi-pencil" style="margin-right: 10px;" @click="onEdit(slotProps.data.name)"/>
                <i class="pi pi-trash" @click="onDelete(slotProps.data.name)"/>
            </template>
        </Column>
        </DataTable>
       
</template>
<script setup>
import { inject, ref, getDocList, onMounted,deleteDoc,useConfirm,useDialog } from '@/plugin'
import ComAddCityLedgerType from "@/views/city_ledger/components/ComAddCityLedgerType.vue"
const gv = inject("$gv")
const data = ref([])
const filter = ref({})
const confirm = useConfirm()
const dialog = useDialog()

function onEdit (name){ 

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
    data:{
        name: name,
    },
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
        fields: ['name','city_ledger_type', 'note','owner',],
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
            header: `Add New City Ledger Type`,
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