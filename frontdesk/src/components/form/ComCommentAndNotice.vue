<template lang="">
    <div>
                <div class="mb-4">
                    <label for="text--note" class="text-lg line-height-1 font-semibold">{{create.note_type}}</label><br/>
                    <Textarea class="w-full my-2" id="text--note" v-model="create.content" rows="3" />
                    <div class="flex gap-5 justify-end items-center mt-2"> 
                            <div class="flex gap-5 align-items-center">
                                <div>
                                    <RadioButton v-model="create.note_type" inputId="comment" name="noteType" value="Comment" />
                                    <label for="comment" class="cursor-pointer ml-1"> Comment </label>
                                </div>
                                <div>
                                    <RadioButton v-model="create.note_type" inputId="note" name="noteType" value="Notice" />
                                    <label for="note" class="cursor-pointer ml-1"> Notice </label>
                                </div>
                                
                            </div>
                            <div>
                                <Button class="border-none" :loading="saving" @click="onCreate">
                                    <img class="btn-add_comNote__icon me-1" :src="iconPlusSign">
                                    <label for="comment" class="font-normal ml-1"> Add {{create.note_type}} </label>
                                </Button>
                            </div>
                    </div>
                </div>
                <ComPlaceholder :loading="loading" :is-not-empty="list.length > 0">
                    <div v-for="(i, index) in list" :key="index" class="mb-3 p-3 rounded-xl shadow-card-edoor" :class="(i.note_type == 'Notice') ? 'bg-yellow-notice-bg text-yellow-700' : 'bg-commnet-cart' ">
                        <div class="flex justify-between">
                            <div class="flex items-center">
                               <i :class="(i.note_type == 'Notice') ? 'pi pi-bookmark' : 'pi pi-comment'"></i>
                               <div class="ms-1 text-sm">
                                <span class="font-italic">{{i.note_type}} by:</span> <span class="text-500 font-italic">{{i.owner}} {{moment(i.creation).format("DD-MM-yy h:ss a") }}, </span>
                                <span class="font-italic">Last Modified:</span> <span class="text-500 font-italic">{{i.owner}} {{moment(i.modified).format("DD-MM-yy h:ss a") }}</span>
                                </div>  
                            </div>
                            <div class="gap-2 flex">
                                <Button text icon="pi pi-file-edit" class="w-1rem h-1rem" @click="onAddEdit($event,i)"></Button>
                                <Button text icon="pi pi-trash" class="w-1rem h-1rem" :loading="deleting" severity="danger" @click="onRemove(i)"></Button>
                            </div>
                        </div>
                        <div class="whitespace-pre-wrap py-1" v-html="i.content"> 
                        </div>
                    </div>
                </ComPlaceholder>
        <OverlayPanel ref="op">
            <ComOverlayPanelContent :loading="saving" @onSave="onSave" @onCancel="onClose">
                    <div>
                        <label for="textnote">{{edit.note_type}}</label><br/>
                        <Textarea id="textnote" v-model="edit.content" rows="5" cols="30" />
                    </div>
            </ComOverlayPanelContent>
        </OverlayPanel>
    </div>
</template>
<script setup>
    import iconPlusSign from '@/assets/svg/icon-add-plus-sign.svg'
    import {ref, inject, toaster, getApi,useConfirm, onMounted, deleteDoc,createUpdateDoc} from '@/plugin'
    import Enumerable from 'linq'
    import ComReservationStayPanel from '../../views/reservation/components/ComReservationStayPanel.vue';
    const moment = inject("$moment");
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
    const create = ref({
        note_type: 'Comment',
        content: ''
    })
    const edit = ref({
        note_type: 'Comment',
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
            else
                list.value = []
            
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
            edit.value = JSON.parse(JSON.stringify(selected))
        }else{
            edit.value = {
                note_type: 'Comment',
                content: ''
            }
        }
        op.value.data = selected
        op.value.toggle($event)
    }
    function onCreate(){ 
        if(create.value.note_type == 'Notice'){
            onSaveNote('Frontdesk Note', create.value)
        }else{
            onSaveNote('Comment', create.value)
        }
    }
    function onSave(){
        if(edit.value.note_type == 'Notice'){
            onSaveNote('Frontdesk Note', edit.value)
        }else{
            onSaveNote('Comment', edit.value)
        }
    }
    function onSaveNote(doctype, data){
        if(!data.content){
            toaster('warn','Please input text.')
            return
        }
        saving.value = true
        data.reference_doctype = props.doctype
        data.reference_name = props.docname
        data.comment_type = 'Comment'
        data.comment_by = currentUser.name
        data.name = op.value.data?.name || ''
        createUpdateDoc(doctype,data).then((r)=>{
            saving.value = false
            create.value = {
                note_type: 'Comment',
                content: ''
            }
            edit.value = data.value
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
<style scoped>
    .bg-yellow-notice-bg{
        background-color: #faf6e9;
    }
</style>