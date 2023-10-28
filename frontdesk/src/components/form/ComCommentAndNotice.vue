<template lang="">
    <div> 
        <div class="mb-4">
            <label for="text--note" class="text-lg line-height-1 font-semibold">{{create.note_type}}</label><br/>
            <div v-if="create.note_type=='Notice'">
            <Calendar  :selectOtherMonths="true" class="p-inputtext-sm depart-arr  w-full border-round-xl"
                                 placeholder="Note Date"
                                 v-model="create.note_date"
                                  dateFormat="dd-mm-yy" showIcon showButtonBar panelClass="no-btn-clear" />
            </div>
            <div class="-mb-2 mt-3" v-if="create.note_type=='Notice'">
            </div>
            <div class="h-6rem mb-4">
                <Textarea class="w-full my-2 h-full" id="text--note" v-model="create.content" />
            </div>
            <div class="flex gap-5 justify-end items-center mt-1"> 
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
            <Button class="dialog_btn_transform conten-btn" :loading="saving" @click="onCreate">
                <img class="btn-add_comNote__icon me-1" :src="iconPlusSign">Add {{create.note_type}}
            </Button>
        </div>
    </div>
    </div>
        <ComPlaceholder text="No Comment or Notice yet" :loading="loading" :is-not-empty="list.length > 0">
    <div v-for="(i, index) in list" :key="index" class="mb-3 p-3 rounded-xl shadow-card-edoor" :class="(i.note_type == 'Notice') ? 'bg-yellow-notice-bg text-yellow-700' : 'bg-commnet-cart' ">
 
        <div class="flex justify-between">
        <div class="flex items-center">

            <i :class="(i.note_type == 'Notice') ? 'pi pi-bookmark' : 'pi pi-comment'"></i>
            <div class="ms-1 text-sm">
                
                <span class="font-italic" v-if="i.note_type!='Info'">{{i.note_type}}</span> <span class="text-500 font-italic"> by: {{i.owner}}    
                    <Timeago  :datetime="i.creation" long>
                                </Timeago> 
                                 </span>
                <span class="font-italic" v-if="i.modified">, Last Modified:</span> <span class="text-500 font-italic" v-if="i.modified">{{i.modified_by}} {{moment(i.modified).format("DD-MM-yy h:ss a") }}</span>
            </div> 
           
          
        </div>
        <div class="gap-2 flex" v-if="i.note_type!='Info'">
            <Button text icon="pi pi-file-edit" class="w-1rem h-1rem" @click="onAddEdit($event,i)"></Button>
            <Button text icon="pi pi-trash" class="w-1rem h-1rem" :loading="deleting" severity="danger" @click="onRemove(i)"></Button>
        </div>
    </div>
        <div class="whitespace-pre-wrap break-words py-1" v-if="i.subject">{{currentUser.name==i.owner?"You ": i.user_full_name }} {{i.subject}}</div>
        <div class="whitespace-pre-wrap break-words py-1" v-html="i.content"></div>
        <div class="text-500 font-italic  text-sm" v-if="i.note_date">
        Note Date: {{moment(i.note_date).format("DD-MM-YYYY")}} 
        </div>
    </div>
    </ComPlaceholder>
    <OverlayPanel ref="op">
    <ComOverlayPanelContent width="35rem" :loading="saving" @onSave="onSave" @onCancel="onClose">
    <div>
    <span class="font-semibold text-lg mb-3" for="textnote">{{edit.note_type}}</span>
    <div class="mb-2" v-if="edit.note_type=='Notice'">
    <Calendar  :selectOtherMonths="true" class="p-inputtext-sm depart-arr w-full border-round-xl" panelClass="no-btn-clear" placeholder="Note Date" v-model="edit.note_date" dateFormat="dd-mm-yy" showIcon showButtonBar />
    </div>
    <div>
    <Textarea id="textnote" v-model="edit.content" rows="5" class="w-full" />
    </div>
    </div>
    </ComOverlayPanelContent>
    </OverlayPanel>
    </div>
</template>
<script setup>
import iconPlusSign from '@/assets/svg/icon-add-plus-sign-purple.svg'
import { ref, inject, getApi, useConfirm, onMounted, deleteDoc, createUpdateDoc, onUnmounted } from '@/plugin'
import Enumerable from 'linq'
import { Timeago } from 'vue2-timeago'
const moment = inject("$moment");
const gv = inject("$gv");
const props = defineProps({
    doctype: String,
    docname: String,
    reservationStay: String,
    reservation: String

})

let op = ref()
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)

const dialogConfirm = useConfirm();
const currentUser = window.user
const create = ref({
    note_type: 'Comment',
    content: '',
    note_date: moment().toDate()
})
const edit = ref({
    note_type: 'Comment',
    content: ''
})
const list = ref([])
const onLoadComment = async function (e) {

    if (e.data.action == "load_comment") {
        setTimeout(function () {
            onLoad(false)
        }, e.data.timeout || 5000)

    }
}
onMounted(() => {
    window.addEventListener('message', onLoadComment, false);
    onLoad()
})

onUnmounted(() => {
    window.removeEventListener('message', onLoadComment, false);
})

function onLoad(show_loading = true) {
    loading.value = show_loading
    getApi('reservation.get_reservation_comment_note', {
        doctype: props.doctype,
        docname: props.docname
    }).then((r) => {
        if (r.message && r.message.length > 0)
            list.value = Enumerable.from(r.message).orderByDescending("$.creation").toArray()
        else
            list.value = []

        loading.value = false
        //add event listener to click view detail popup

        setTimeout(function () {
            document.querySelectorAll('[data-action]').forEach(el => {
                
                if (!el.dataset.click) {
                    el.addEventListener('click', function () {
                        window.postMessage(el.dataset.action + "|" + el.dataset.name, "*")

                    })
                    el.setAttribute('data-click', '1');
                    
                }
            })
        }, 2000)
    }).catch((err) => {
        loading.value = false
    })
}

function onClose() {
    op.value.hide()
}
function onAddEdit($event, selected) {

    if (selected) {
        edit.value = JSON.parse(JSON.stringify(selected))
        edit.value.note_date = moment(edit.value.note_date).toDate()
    } else {
        edit.value = {
            note_type: 'Comment',
            content: ''
        }
    }
    op.value.data = selected
    op.value.toggle($event)
}
function onCreate() {
    op.value = {}
    let note_data = JSON.parse(JSON.stringify(create.value))
    if (note_data.note_date) {
        note_data.note_date = moment(note_data.note_date).format("YYYY-MM-DD")
    }
    if (create.value.note_type == 'Notice') {
        onSaveNote('Frontdesk Note', note_data)
    } else {
        onSaveNote('Comment', note_data)
    }
}

function onSave() {
    let note_data = JSON.parse(JSON.stringify(edit.value))

    if (note_data.note_date) {
        note_data.note_date = moment(note_data.note_date).format("YYYY-MM-DD")
    }

    if (note_data.note_type == 'Notice') {
        onSaveNote('Frontdesk Note', note_data)
    } else {
        onSaveNote('Comment', note_data)
    }
}
function onSaveNote(doctype, data) {
    if (!data.content) {
        gv.toast('warn', 'Please input text.')
        return
    }
    saving.value = true
    if (!data.name) {
        data.property = window.property_name
    }
    // for folio trancation
    if (props.doctype == 'Folio Transaction') {
        data.reservation = props.reservation || ''
        data.reservation_stay = props.reservationStay || ''
    }
    data.reference_doctype = props.doctype
    data.reference_name = props.docname
    data.comment_type = 'Comment'
    data.comment_by = currentUser.name
    data.name = op.value.data?.name || ''
    createUpdateDoc(doctype, { data: data }).then((r) => {
        saving.value = false
        create.value = {
            note_type: 'Comment',
            content: '',
            note_date: moment().toDate()
        }
        edit.value = data.value
        onLoad()
        op.value.hide()
    }).catch((err) => {
        saving.value = false
    })
}
function onRemove(selected) {
    dialogConfirm.require({
        message: 'Do you want to delete this record?',
        header: 'Delete Confirmation',
        icon: 'pi pi-info-circle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            deleting.value = true
            deleteDoc(selected.note_type == 'Comment' ? 'Comment' : 'Frontdesk Note', selected.name).then((doc) => {
                if (doc) {
                    deleting.value = false
                    onLoad()
                    // window.socket.emit("ReservationDetail", window.reservation)     
                    window.socket.emit("ReservationStayDetail", { reservation_stay: window.reservation_stay })
                }
            }).catch((err) => {
                deleting.value = false
            })
        }
    })
}


</script>
<style scoped>
.bg-yellow-notice-bg {
    background-color: #faf6e9;
}
</style>