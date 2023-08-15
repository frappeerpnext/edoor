<template>
    <div>
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
                <i class="pi pi-pencil" style="margin-right: 10px;" @click="onEdit"/>
                <i class="pi pi-trash" @click="onDelete(slotProps.data.name)"/>
            </template>
        </Column>
        </DataTable>

        <Dialog v-model:visible="visible" modal header="Add New City Ledger Account Type" :style="{ width: '50vw' }">
            <ComDialogContent :loading="loading" @onClose="visible = false" @onOK="onSave()">
                City Ledger Type
            <div class="card flex justify-content-left">
                <InputText type="text" v-model="accountType.city_ledger_type" />
            </div><br>
            Note
            <div class="card flex justify-left">
                 <Textarea v-model="accountType.note" rows="5" cols="50" />
            </div><br>
        </ComDialogContent> 
        </Dialog>
    </div>
</template>
<script setup>
import { inject, ref, useToast, getDocList, onMounted, createUpdateDoc,deleteDoc,useConfirm } from '@/plugin'
const moment = inject("$moment")
const gv = inject("$gv")
const toast = useToast()
const data = ref([])
const filter = ref({})
const visible = ref(false);
const accountType = ref({});
const loading = ref(false)
const frappe = inject('$frappe');
const confirm = useConfirm()

function onEdit (){ 
 dialog.open(ComDialogContent, {
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
        name: name.value,
    },
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
            loading.value = true
             deleteDoc('City Ledger Type',name)
                 .then(() =>{
                    
                    loading.value = false
                 } ).catch((err)=>{
                    loading.value = false
                 })         
        },
    });
}

function onSave(){
  if(!accountType.value.city_ledger_type){
    gv.toast('warn','Please input guest type.')
    return
  }
  loading.value = true
  createUpdateDoc("City Ledger Type", {data: accountType.value}).then((r)=>{
    loading.value = false
    visible.value = false
    loadData()
  }).catch((err)=>{
    loading.value = false
  })
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
    accountType.value = {}
    visible.value = true;
}
onMounted(() => {
    loadData()
})

</script>