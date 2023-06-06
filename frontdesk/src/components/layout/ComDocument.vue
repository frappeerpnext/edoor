<template>
    <div>
        <Button label="Attach File" @click="onModal"></Button>
 
        <div>
            <div class="wrap-file-list" v-if="data.length > 0">
                
                <DataTable :value="data">
                    <Column field="file_url" header="File">
                        <template #body="slotProps"> 
                            <ComAvatar size="xlarge" :image="slotProps.data.file_url" :fileName="slotProps.data.file_url" align="justify-start"/>
                        </template>
                    </Column>
                    <Column field="title" header="Title"></Column>
                    <Column field="description" header="Description"></Column>
                    <Column field="" header="Action">
                        <template #body="slotProps"> 
                            <Button text size="small" icon="pi pi-trash" @click="onRemove(slotProps.data.name)" severity="danger" />
                        </template>
                    </Column>
                </DataTable>
            </div>
        </div>
        <Dialog v-model:visible="visible" modal header="Documents" :style="{ width: '50vw' }">
            <ComDialogContent hideFooter> 
                <ComAttachFile :docname="docname" :doctype="doctype" @onSuccess="onSuccess"/>
            </ComDialogContent>
        </Dialog>
    </div>
</template>
<script setup>
import {inject, getDocList, ref,onMounted} from '@/plugin'
const props = defineProps({
    doctype: {
        type: String,
        required: true
    },
    docname: {
        type: String,
        required: true
    }
})
const visible = ref(false)
const loading = ref(false)
const data = ref([])
function onModal(){
    visible.value = true
}
function onSuccess(){
    onModal()
}
function onLoad(){
    loading.value = true
    getDocList('File', {
        fields: ['name', 'title','description','file_size','file_url'],
        filters: [
            ['attached_to_doctype', '=', props.doctype],
            ['attached_to_name', '=', props.docname]
        ],
    }).then((r)=>{
        data.value = r
        console.log(r)
        loading.value = false
    }).catch((err)=>{
        loading.value = false
    })
}
onMounted(() => {
   onLoad() 
})
</script>
<style lang="">
    
</style>