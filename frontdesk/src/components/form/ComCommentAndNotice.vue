<template lang="">
    <div>
        <ComReservationStayPanel class="mb-2" title="Notice & Comment">
            <template #content>
                <div class="mb-4">
                    <label for="text--note">{{data.note_type}}</label><br/>
                    <Textarea id="text--note" v-model="data.content" rows="3" class="w-full" />
                    <div class="flex gap-2 justify-between items-center"> 
                        <div>
                            <div class="flex gap-2 align-items-center">
                                <div>
                                    <RadioButton v-model="data.note_type" inputId="note" name="noteType" value="Notice" />
                                    <label for="note" class="ml-2"> Notice </label>
                                </div>
                                <div>
                                    <RadioButton v-model="data.note_type" inputId="comment" name="noteType" value="Comment" />
                                    <label for="comment" class="ml-2"> Comment </label>
                                </div>
                            </div>
                        </div>
                        <Button class="border-none" icon="pi pi-save" :loading="saving" @click="onSave" label="Save"></Button>
                    </div>
                </div>
                <ComPlaceholder :loading="loading" :is-not-empty="list.length > 0">
                    <div v-for="(i, index) in list" :key="index" class="mb-2 p-2 bg-white rounded-sm">
                        <div class="text-right">
                            <Button text icon="pi pi-file-edit" @click="onAddEdit($event,i)"></Button>
                            <Button text icon="pi pi-trash" :loading="deleting" severity="danger" @click="onRemove(i)"></Button>
                        </div>
                        <div>
                            {{i.name}} / {{i.note_type}} / {{i.owner}} / {{i.creation}}
                            <div>
                                {{i.content}}
                            </div>
                        </div>
                        
                    </div>
                </ComPlaceholder>
            </template>
        </ComReservationStayPanel>
        <OverlayPanel ref="op">
            <ComOverlayPanelContent :loading="saving" @onSave="onSave" @onCancel="onClose">
                <div>
                    <div>
                        <label for="textnote">{{data.note_type}}</label><br/>
                        <Textarea id="textnote" v-model="data.content" rows="5" cols="30" />
                    </div>
                </div>
            </ComOverlayPanelContent>
        </OverlayPanel>
    </div>
</template>
<script setup>
    import {ref, updateDoc, getApi,useConfirm, onMounted, deleteDoc} from '@/plugin'
    import Enumerable from 'linq'
    import ComReservationStayPanel from '../../views/reservation/components/ComReservationStayPanel.vue';
    const props = defineProps({
        doctype: String,
        docname: String
    })
    let op = ref() 
    const loading = ref(false)
    const saving = ref(false)
    const deleting = ref(false)
    const dialogConfirm = useConfirm();
    const currentUser = JSON.parse(localStorage.getItem('edoor_user'))
    const data = ref({
        note_type: 'Notice',
        content: ''
    })
    const list = ref([])
    onMounted(() => {
        onLoad()
    })
    function onLoad(){
        loading.value = true
        getApi('reservation.get_reservation_comment_note',{
            doctype: props.doctype,
            docname: props.docname
        }).then((r)=>{
            if(r.message && r.message.length > 0)
                list.value = Enumerable.from(r.message).orderByDescending("$.creation").toArray()
            loading.value = false
        }).catch((err)=>{
            loading.value = false
        })
    }
    function onClose(){
        op.value.hide()
    }
    function onAddEdit($event, selected){
        if(selected){
            data.value = JSON.parse(JSON.stringify(selected))
        }else{
            data.value = {
                note_type: 'Notice',
                content: ''
            }
        }
        op.value.data = selected
        op.value.toggle($event)
    }
    function onSave(){
        if(data.value.note_type == 'Notice'){
            onSaveNote('Frontdesk Note')
        }else{
            onSaveNote('Comment')
        }
    }
    function onSaveNote(doctype){
        saving.value = true
        const name = op.value.data?.name;
        data.value.reference_doctype = props.doctype
        data.value.reference_name = props.docname
        data.value.comment_type = 'Comment'
        data.value.comment_by = currentUser.name
        updateDoc(doctype,name,data.value).then((r)=>{
            saving.value = false
            data.value = {
                note_type: 'Notice',
                content: ''
            }
            op.value.hide()
            onLoad()
        }).catch((err)=>{
            saving.value = false
        })
    }
    function onRemove(selected){
        dialogConfirm.require({
            message: 'Do you want to delete this record?',
            header: 'Delete Confirmation',
            icon: 'pi pi-info-circle',
            acceptClass: 'p-button-danger',
            accept: () => {
                deleting.value = true
                deleteDoc(selected.note_type == 'Comment' ? 'Comment' : 'Frontdesk Note', selected.name).then((doc) => {
                    if(doc){
                        deleting.value = false
                        onLoad()
                    }
                }).catch((err)=>{
                    deleting.value = false
                })
            }
        })
    }
</script>
<style lang="">
    
</style>