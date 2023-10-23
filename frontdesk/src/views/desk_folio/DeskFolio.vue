 
<template>
    <div>
        <ComHeader isRefresh @onRefresh="df.loadData()">
            <template #start>
                <div class="text-2xl">
                    <Button @click="onViewComponent('desk_folio')">Desk Folio</Button> 
            <Button @click="onViewComponent('desk_folio_transaction')">Desk Folio Transaction</Button> 
                </div>
            </template>
            <template #end>
                <Button class="border-none" label="Add New Desk Folio" icon="pi pi-plus" @click="onAddNewGuestType" />
            </template>
        </ComHeader>

        <div class="rounded-xl">
                        <ComDeskFolioList v-if="showComponent=='desk_folio'"/>
                        <ComDeskFolioTransaction v-else />
                  
        </div>
    </div>
</template>
<script setup>
    import {ref, inject} from "@/plugin"
    import ComDeskFolioList from "@/views/desk_folio/components/ComDeskFolioList.vue"
    import ComDeskFolioTransaction from "@/views/desk_folio/components/ComDeskFolioTransaction.vue"
    
    const showComponent = ref("desk_folio")

    const df = inject("$desk_folio")
    function onViewComponent(name){
        showComponent.value = name
    }

</script>

 