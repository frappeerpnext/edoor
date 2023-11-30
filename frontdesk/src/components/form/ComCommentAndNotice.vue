<template lang="">
    <div> 
        <div class="mb-4">
            <label for="text--note" class="text-lg line-height-1 font-semibold">{{create.custom_is_note==0?'Comment':'Note'}}</label><br/>
            <div v-if="create.custom_is_note==1">
            <Calendar  :selectOtherMonths="true" class="p-inputtext-sm depart-arr  w-full border-round-xl"
                                 placeholder="Note Date"
                                 v-model="create.custom_note_date"
                                  dateFormat="dd-mm-yy" showIcon showButtonBar panelClass="no-btn-clear" />
            </div>
            <div class="-mb-2 mt-3" v-if="create.comment_type=='Notice'">
            </div>
            <div class="h-6rem mb-4">
                <Textarea class="w-full my-2 h-full" id="text--note" v-model="create.content" />
            </div>
            <div class="flex gap-3 justify-end items-center mt-1"> 
            <div class="flex gap-5 align-items-center">
                <div>
                    <RadioButton v-model="create.custom_is_note"  inputId="comment" name="noteType" :value="0" />
                    <label for="comment" class="cursor-pointer ml-1"> Comment </label>
                </div>
            <div>
                <RadioButton v-model="create.custom_is_note" inputId="note" name="noteType" :value="1" />
                <label for="note" class="cursor-pointer ml-1"> Notice </label>
            </div>
        </div>
        <div>
     
            <Button class="dialog_btn_transform conten-btn " :loading="saving" @click="onCreate">
                <img class="btn-add_comNote__icon me-1" :src="iconPlusSign">Add {{commentType}}
            </Button>
        </div>
        <ComHeader fillClass="dialog_btn_transform conten-btn" isRefresh @onRefresh="onRefresh()"/>
    </div>
    </div>
        <ComPlaceholder text="No Comment or Notice yet" :loading="loading" :is-not-empty="list.length > 0">
    <div v-for="(i, index) in list" :key="index" class="mb-3 p-3 rounded-xl shadow-card-edoor" :class="(i.comment_type == 'Notice') ? 'bg-yellow-notice-bg text-yellow-700' : 'bg-commnet-cart' ">
 
        <div class="flex justify-between">
        <div class="flex items-center">
            <!-- <i :class="(i.comment_type == 'Notice') ? 'pi pi-bookmark' : 'pi pi-comment'"></i> -->
            <span class="">
            <i :class="i.custom_icon" style="font-size:14px" class="me-2"></i>
            </span>
            <div class="ms-1 text-sm ">
                
                <span class="font-italic">{{i.subject}}</span> <span class="text-500 font-italic"> by: {{(currentUser.name==i.owner?"You ": i.comment_by).split("@")[0]}}    
                    <ComTimeago  :date="i.creation"/> 
                                 </span>
                                 <div class="inline" v-if="i.custom_is_note == 1">
                <span class="font-italic" > | Last Modified : </span> <span class="text-500 font-italic" v-if="i.modified_by">{{(currentUser.name==i.modified_by?"You ": i.modified_by).split("@")[0]}}  <ComTimeago  :date="i.modified"/> </span>
                                 </div>
            </div> 
           
          
        </div>
        <div class="gap-2 flex" v-if="i.comment_type=='Comment'">
            <Button text icon="pi pi-file-edit" class="w-1rem h-1rem" @click="onAddEdit($event,i)"></Button>
            <Button text icon="pi pi-trash" class="w-1rem h-1rem" :loading="deleting" severity="danger" @click="onRemove(i)"></Button>
        </div>
    </div>
    <div class="content-note-comment" v-if="doctype!=i.reference_doctype">
    {{i.reference_doctype}} | <a @click="onViewDetail(i)"> {{i.reference_name}}</a>
    </div>
        <!-- <div class="whitespace-pre-wrap break-words content-note-comment py-1" v-if="i.subject">{{currentUser.name==i.owner?"You ": i.comment_by }} </div> -->
        <div class="whitespace-pre-wrap break-words content-note-comment py-1" v-html="i.content"></div>
        <div class="text-500 font-italic  text-sm" v-if="i.custom_note_date && i.custom_is_note">
        Note Date: {{moment(i.custom_note_date).format("DD-MM-YYYY")}} 
        </div>
    </div>
    </ComPlaceholder>
    <OverlayPanel ref="op">
    <ComOverlayPanelContent width="35rem" :loading="saving" @onSave="onSave" @onCancel="onClose">
    <div>
    <span class="font-semibold text-lg mb-3" for="textnote">{{edit.custom_is_note==0?'Comment':"Note"}}</span>
    <div class="mb-2" v-if="edit.custom_is_note==1">

    <Calendar  :selectOtherMonths="true" class="p-inputtext-sm depart-arr w-full border-round-xl" panelClass="no-btn-clear" placeholder="Note Date" v-model="edit.custom_note_date" dateFormat="dd-mm-yy" showIcon showButtonBar />
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
import { ref, inject, getDocList, useConfirm, onMounted, deleteDoc, createUpdateDoc, onUnmounted,computed } from '@/plugin'
import Enumerable from 'linq'
const moment = inject("$moment");
const gv = inject("$gv");
const props = defineProps({
    doctype: String,
    docname: String,
    reference_doctypes: Object,
    docnames: Object,
})
const onRefresh = debouncer(() => {
    onLoad();
}, 500);

const commentType = computed(()=>{
    return (create.value.custom_is_note || 0) ==0? "Comment":"Note"
})

function debouncer(fn, delay) {
    var timeoutID = null;
    return function () {
        clearTimeout(timeoutID);
        var args = arguments;
        var that = this;
        timeoutID = setTimeout(function () {
            fn.apply(that, args);
        }, delay);
    };
}

let op = ref()
const loading = ref(false)
const saving = ref(false)
const deleting = ref(false)

const dialogConfirm = useConfirm();
const currentUser = window.user
const create = ref({
    comment_type: 'Comment',
    content: '',
    custom_note_date: moment(window.current_working_date).toDate(),
    custom_is_note: 0
})
const edit = ref({
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

function onViewDetail(d){
    window.postMessage("view_" + d.reference_doctype.toLowerCase().replaceAll(" ","_") + "_detail|" + d.reference_name ,"*")
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
    loading.value = show_loading
	let filters = ([
		["custom_property", '=', window.property_name], ["custom_is_audit_trail", '=', 1]
	])
	filters.push(["reference_doctype", 'in', props.reference_doctypes])
	filters.push(["reference_name", 'in', props.docnames])
    getDocList('Comment', {
		fields: ["name","creation", "custom_keyword" ,"custom_note_date" ,"custom_audit_trail_type" , "custom_posting_date", "reference_doctype", "reference_name", "subject", "content", "owner","comment_by", "modified_by" ,"modified","comment_type","custom_icon",'custom_is_note'],
		orderBy: {
			field: "creation",
			order:"DESC",
		},
		filters: filters, 
		limit_start: 0,
		limit: 20,
	}).then((r) => {
        
            list.value = r
  

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
        edit.value.custom_note_date = moment(edit.value.custom_note_date).toDate()
    } else {
        edit.value = {
            content: ''
        }
    }
    op.value.data = selected
    op.value.toggle($event)
}
function onCreate() {
    op.value = {}
    let note_data = JSON.parse(JSON.stringify(create.value))
    note_data.subject = note_data.custom_is_note==1?"Adding Note":"Adding Comment"
    note_data.custom_audit_trail_type = note_data.custom_is_note==1?"Note":"Comment"
    note_data.custom_note_date = moment(note_data.custom_note_date).format("YYYY-MM-DD")
    
    onSaveNote('Comment', note_data)
}

function onSave() {
    let note_data = JSON.parse(JSON.stringify(edit.value))

    if (note_data.custom_note_date) {
        note_data.custom_note_date = moment(note_data.custom_note_date).format("YYYY-MM-DD")
    }


        onSaveNote('Comment', note_data)

}
function onSaveNote(doctype, data) {
   
    if (!data.content) {
        gv.toast('warn', 'Please input text.')
        return
    }
    saving.value = true
    if (!data.name) {
        data.custom_property = window.property_name
    }
    // for folio trancation
    if (props.doctype == 'Folio Transaction') {
        data.reservation = props.reservation || ''
        data.reservation_stay = props.reservationStay || ''
    }
    data.reference_doctype = props.doctype
    data.reference_name = props.docname
    data.comment_type = 'Comment'
    data.name = op.value.data?.name || ''
    data.custom_is_audit_trail =1
    data.custom_posting_date = window.current_working_date
    
    createUpdateDoc(doctype,  data ).then((r) => {
        saving.value = false
        create.value = {
            content: '',
            custom_note_date: moment().toDate(),
            custom_is_note:0
            
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
            deleteDoc('Comment', selected.name).then((doc) => {
                if (doc) {
                    deleting.value = false
                    onLoad()
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