<template>
<div>
	<div>
		<div class="flex justify-end items-center">
			<div class="flex items-center mt-3 mb-1">
				<!-- <ComAddNote :name="name"></ComAddNote> -->
				<Button @click="onEdit('')" class="conten-btn bg-yellow-50 white-space-nowrap text-yellow-500 border-yellow-500">
					<i class="pi pi-plus text-lg  me-2"></i>
					Add Note
				</Button>
				<div class="card flex flex-wrap justify-content-center gap-3">
        <span class="p-input-icon-left">
            <i class="pi pi-search" />
            <InputText v-model="keyword" placeholder="Search" @input="onSearch"/>
            </span>
    		</div>
			</div>
		</div>
		<div v-for="i in notes" :key="index" class=" border-1 rounded-lg pt-2 px-3 pb-4 mt-3 content-global-note">
			<div class="flex justify-between items-center " style="min-height: 26px;">
				<div class="line-height-1" > 
					<div class="font-medium">
						{{ i.reference_doctype }}
						<span v-if="i.reference_doctype && i.reference_name"> - </span>
						<span class="link_line_action w-auto border-none p-0" @click="showReservationStayDetail(i?.reference_name)" v-if="i.reference_doctype == 'Reservation Stay'">
							{{i.reference_name}}
						</span>
						<span class="link_line_action w-auto border-none p-0" @click="showReservationDetail(i?.reference_name)" v-if="i.reference_doctype == 'Reservation'">
							{{i.reference_name}}
						</span>
						<span class="link_line_action w-auto border-none p-0" @click="onViewFolioDetail(i?.reference_name)"  v-if="i.reference_doctype == 'Folio Transaction'">
							{{i.reference_name}}
						</span>
						<div class="text-sm">
							<div v-if="i?.reservation || i?.reservation_stay" class="inline me-1">
							<span @click="showReservationDetail(i?.reservation)" class="link_line_action w-auto border-none p-0">
								{{ i?.reservation }} 
							</span>
							<span v-if="i?.reservation && i?.reservation_stay">
								-
							</span>
							<span @click="showReservationStayDetail(i?.reservation_stay)" class="link_line_action w-auto border-none p-0" v-if="i?.reservation_stay">
								{{ i?.reservation_stay }}
							</span>
							</div>
						</div> 
					</div>
					<div> 	
					</div>
					<div class="flex items-center mt-1 text-500 font-italic">
						<span class="text-sm"> {{gv.dateFormat(i.note_date)}}</span>
					</div>
					
				</div>
				
				<div class="flex">
					<span class="btn-in-note hidden">
						<ComNoteGlobalButtonMore :data="i" @onEdit="onEdit" @onDeleted="onLoadData"/>
					</span>
					<Button :class="i.is_pin ? '' : 'hidden'" class="w-2rem h-2rem px-1 pb-1 pt-0 btn-in-note " text rounded @click="onPin(i)">
						<ComIcon v-tooltip.left="'Unpin Note'" v-if="i.is_pin" icon="pushPined" style="height:20px;"></ComIcon>
						<ComIcon v-tooltip.left="'Pin Note'" v-else icon="pushPin" style="height:20px;"></ComIcon>
						
					</Button>
				</div>
			</div>
			<div v-if="i.content" class="mt-1 max-h-28 whitespace-pre-wrap break-words overflow-auto">
				{{ i.content }}
			</div>
		</div>
	</div>
</div>
</template>

<script setup>
import { ref, inject,useDialog,onMounted,updateDoc } from '@/plugin';
import ComAddNote from './ComAddNote.vue';
import ComNoteGlobalButtonMore from './ComNoteGlobalButtonMore.vue';
import ReservationStayDetail from "@/views/reservation/ReservationStayDetail.vue"
import ReservationDetail from "@/views/reservation/ReservationDetail.vue"
import ComFolioTransactionDetail from '@/views/reservation/components/reservation_stay_folio/ComFolioTransactionDetail.vue';
import Enumerable from 'linq'

const frappe = inject('$frappe');
const gv = inject('$gv');
const db = frappe.db();
const dialog = useDialog()
const notes = ref([]);
const loading = ref(false);
const keyword = ref()
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))

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
                closeOnEscape: false
            },
            onClose: (options) => {
                const data = options.data;
                if(data){
					onLoadData()
				}
            }
        });
}
function onPin(i){
	i.is_pin = !i.is_pin
	updateDoc('Frontdesk Note', i.name, i).then((r)=>{
		onLoadData()
	})
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

function showReservationStayDetail(selected) {
    let stayName = selected
    const dialogRef = dialog.open(ReservationStayDetail, {
        data: {
            name: stayName
        },
        props: {
            header: 'Reservation Stay Detail',
			contentClass: 'ex-pedd',
            style: {
                width: '80vw',
            },
            maximizable: true,
            modal: true,
            closeOnEscape: false,
            position:"top"
        }, 
    });
}

function showReservationDetail(selected) {
    let rsName = selected
    const dialogRef = dialog.open(ReservationDetail, {
        data: {
            name: rsName
        },
        props: {
            header: 'Reservation Detail',
			contentClass: 'ex-pedd',
            style: {
                width: '80vw',
            },
            maximizable: true,
            modal: true,
            closeOnEscape: false,
            position:"top"
        }, 
    });
}

function onLoadData(){
	loading.value = true
	let filters = []
	filters.push(["note_date",">=", working_day.date_working_day])
	if (keyword.value){
		filters.push(["content","like", '%' + keyword.value + '%'])
	}
	db.getDocList('Frontdesk Note', {
		fields: ['name','note_date','reference_doctype','is_pin','reference_name', "reservation", "reservation_stay", "content"],
		filters:filters,
		orderBy: {
			field: 'creation',
			order: 'asc',
		}
	}).then((docs) => {
		notes.value = Enumerable.from(docs).orderByDescending("$.is_pin").toArray();
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
