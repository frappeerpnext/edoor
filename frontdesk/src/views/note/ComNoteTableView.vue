<template>  
<div class="overflow-auto h-full mb-3">  
        <ComPlaceholder text="No Data" height="70vh" :is-not-empty="notes.length > 0">
            <DataTable
                class="res_list_scroll" 
                :resizableColumns="true" 
                columnResizeMode="expand" 
                showGridlines
                stateStorage="local" 
                stateKey="table_note_state" 
                :reorderableColumns="true" 
                scrollable
                :tableStyle="`min-width: ${width}%`"
                :value="notes">
                <Column header="Note Date">
                    <template #body="slotProps">
                        <span>{{ moment(custom_note_date).format("DD-MM-YYYY") }}</span>
                    </template>
                </Column>   
                <Column header="Reference Name">
                    <template #body="slotProps">
                        <Button v-if="slotProps.data.reference_name" class="p-0 link_line_action1" @click="onOpenLink(slotProps.data)" link>{{ slotProps.data.reference_name }}</Button>
                    </template>
                </Column>  
                <Column field="content" header="Note">
                    <template #body="slotProps">
                        <span class="mt-3 mb-6 whitespace-pre-wrap break-words overflow-auto pb-5 line-height-2">{{ slotProps.data.content }}</span>                        
                    </template>
                </Column>     
                <Column field="comment_by" header="By"></Column>  
                <Column header="Date">
                    <template #body="slotProps">
                        <span>{{ moment(slotProps.data.custom_posting_date).format("DD-MM-YYYY") }}</span>
                    </template>
                </Column>   
                
                
                        
            </DataTable> 
        </ComPlaceholder>
</div> 

<!-- {{ notes }} -->
</template>
<script setup>
import { onMounted, ref, inject } from "@/plugin"
const moment = inject("$moment")
const width = ref(0)
const props = defineProps({
    notes:Object
})

onMounted(()=> {
    width.value = 100
})

function onOpenLink(data) {
	const action = ("view_" + data.reference_doctype.toLowerCase().replaceAll(" ", "_") + "_detail")

	window.postMessage(action + '|' + data.reference_name, '*')
}

</script>