<template>
    <div>
        <ComHeader isRefresh @onRefresh="loadData()">
            <template #start>
                <div class="text-2xl">Guest Type</div>
            </template>
            <template #end>
              <Button label="Add Guest Type" icon="pi pi-plus" severity="warning" outlined @click="onAdGuestType" />
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
        <DataTable  :value="data?.filter((r)=>r.customer_group_en.toLowerCase().includes((filter.keyword ||'').toLowerCase()))" tableStyle="min-width: 50rem" @row-click=" ">
            <Column field="customer_group_en" header="Guest type"></Column>
            <Column field="note" header="Note"></Column>
            <Column field="owner" header="Owner"></Column>
            <Column header="">
             <template #body="slotProps">
                <i class="pi pi-pencil" style="margin-right: 10px;" @click="onEdit"/>
                <i class="pi pi-trash" @click="onDelete"/>
            </template>
        </Column>
        </DataTable>

    </div>
</template>
<script setup>
import { inject, ref, useToast, getDocList, onMounted,useDialog, createUpdateDoc } from '@/plugin'
const moment = inject("$moment")
const gv = inject("$gv")
const toast = useToast()
const dialog = useDialog()
const data = ref([])
const filter = ref({})
const visible = ref(false);
const guestType = ref({});
const loading = ref(false)

function onDelete(){
    alert()
}

function onEdit(){
    visible.value = true
}

function loadData() {
    gv.loading = true
    getDocList('Customer Group', {
        fields: ['customer_group_en', 'note','owner',],
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
function onAdGuestType(){
    alert()

}

onMounted(() => {
    loadData()
})

</script>