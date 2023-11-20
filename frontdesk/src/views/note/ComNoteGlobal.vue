<template>
<div>
	<div>
		<div class="flex justify-end items-center gap-2">
			<div class="p-input-icon-left search-note-cs w-full mt-2 pt-1">
            <i class="pi pi-search" />
            <InputText v-model="keyword" class="w-full" placeholder="Search" @input="onSearch"/>
        	</div>
			<div class="flex items-center mt-3 mb-1">
				<!-- <ComAddNote :name="name"></ComAddNote> -->
				<Button @click="onEdit('')" class="conten-btn bg-yellow-50 white-space-nowrap text-yellow-500 border-yellow-500">
					<i class="pi pi-plus text-lg  me-2"></i>
					Add Note
				</Button>
			</div>
		</div>
		<ComPlaceholder text="No Data" :loading="loading"  :is-not-empty="notes.length > 0">
		<div v-for="i in notes" :key="index" class=" border-1 rounded-lg pt-2 px-3 mt-3 content-global-note relative">
			<div class="flex justify-between items-center " style="min-height: 26px;">
				<div class="line-height-2 mt-2" > 
					<div class="font-medium">
						<div class="text-overflow-ellipsis white-space-nowrap overflow-hidden" v-if="i.reference_doctype">
						<span class="text-lg" >
							{{ i.reference_doctype }}
						</span>
						-
						<div @click="onViewDetail(i)" class="text-lg inline link_line_action  border-none p-0 w-auto" >
							 {{ i.reference_name }}
						</div>
						</div>
						<div v-else>
							<span class="text-lg" >
								General Note
						</span>
							
						</div>
						<div >
							<span v-if="i.custom_note_date" class="font-italic text-500 text-sm">
								Note Date: {{ gv.dateFormat(i.custom_note_date) }}
							</span>
						</div>
					</div>
				</div>
				<div class="flex">
					<span class="btn-in-note">
						<ComNoteGlobalButtonMore :data="i" @onEdit="onEdit" @onDeleted="onLoadData"/>
					</span>
					<Button :class="i.custom_is_pin ? '' : 'hidden'" class="w-2rem h-2rem px-1 pb-1 pt-0 btn-in-note " text rounded @click="onPin(i)">
						<ComIcon v-tippy ="'Unpin Note'" v-if="i.custom_is_pin" icon="pushPined" style="height:20px;"></ComIcon>
						<ComIcon v-tippy ="'Pin Note'" v-else icon="pushPin" style="height:20px;"></ComIcon>
					</Button>
				</div>
			</div>
			<div v-if="i.content" class="mt-1 mb-2 max-h-28 whitespace-pre-wrap break-words overflow-auto py-3">
				{{ i.content }}
			</div>
			<div class="w-full bg-slate-200 mb-2" style="height: 1px;"></div>
			<div class="flex flex-col my-1 font-italic  line-height-2 py-1" style="font-size: 10px;">
				<div>
					Noted by : <span class=" text-500 "> {{ i.comment_by }} -<ComTimeago  :date="i.creation"/></span>
				</div>
				<div v-if="i.modified">
					Last Modified by : <span class=" text-500 ">{{ i.modified_by.split("@")[0] }} - <ComTimeago  :date="i.modified"/> </span>
				</div>
			</div>
		</div>
	</ComPlaceholder>
	</div>
</div>
</template>

<script setup>
import { ref, inject,useDialog,onMounted,updateDoc,useConfirm } from '@/plugin';
import ComAddNote from './ComAddNote.vue';
import ReservationDetail from "@/views/reservation/ReservationDetail.vue"
import ComNoteGlobalButtonMore from "@/views/note/ComNoteGlobalButtonMore.vue"
import ComFolioTransactionDetail from '@/views/reservation/components/reservation_stay_folio/ComFolioTransactionDetail.vue';
import Enumerable from 'linq'

const confirm = useConfirm()
const frappe = inject('$frappe');
const { getTotalNote } = inject('get_count_note')
const gv = inject('$gv');
const db = frappe.db();
const dialog = useDialog()
const notes = ref([]);
const loading = ref(false);
const keyword = ref()
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const property = JSON.parse(localStorage.getItem("edoor_property"))

function onEdit(name){
	const dialogRef = dialog.open(ComAddNote, {
            data: {
				name: name
            },
            props: {
                header: (name ? "Edit" : 'Add') + " Note",
                style: {
                    width: '60vw',
                },
                breakpoints: {
                    '960px': '100vw',
                    '640px': '100vw'
                },
                modal: true,
                maximizable: true,
                closeOnEscape: false,
				position:'top'
            },
            onClose: (options) => {
                const data = options.data;
                if(data){
					onLoadData()
					// update bage total notes
					getTotalNote()
				}
            }
        });
}

function onPin(i){
	i.custom_is_pin = !i.custom_is_pin
	updateDoc('Comment', i.name, i).then((r)=>{
		onLoadData()
	})
}
function onViewDetail(d){
    window.postMessage("view_" + d.reference_doctype.toLowerCase().replaceAll(" ","_") + "_detail|" + d.reference_name ,"*")
}
function onViewFolioDetail (selected) {
const dialogRef = dialog.open(ComFolioTransactionDetail, {
	data: {
		folio_transaction_number: selected
	},
	props: {
		header: 'Folio Transaction Detail - ' + selected,
		style: {
			width: '50vw',
		},
		modal: true,
		position:'top',
		closeOnEscape: false
	},
});

}
function onLoadData(){
	loading.value = true
	let filters = [
		["custom_property", "=", window.property_name],
		["custom_is_audit_trail", "=",1],
		["custom_is_note", "=",1],
		["comment_type","=","Comment"]
	]
	filters.push(["custom_note_date",">=", working_day.date_working_day])
	if (keyword.value){
		filters.push(["custom_keyword" ,"like", '%' + keyword.value + '%'])
	}

	db.getDocList('Comment', {
		fields: ["name","creation", "custom_is_pin", "modified_by" , "custom_note_date", "custom_posting_date", "reference_doctype", 
		 "reference_name", "content", "owner","comment_by", "modified","comment_type","custom_icon",'custom_is_note'],
		filters:filters,
		orderBy: {
			field: 'creation',
			order: 'DESC',
		}
	}).then((docs) => {
		notes.value = Enumerable.from(docs).orderByDescending("$.custom_is_pin").toArray();
		loading.value = false			
	}).catch((rr)=>{
		gv.toast('error', rr)
	})
}

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
const onSearch = debouncer(() => {
    onLoadData();
}, 500);

onMounted(() => {
	onLoadData()
})

</script>
<style scoped>
.conten-btn:hover{
	background-color: #eee0ba !important;
}
</style>
