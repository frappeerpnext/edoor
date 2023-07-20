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
					<span class="text-sm"> {{gv.dateFormat(i.note_date)}}</span>
				</div>
				<div class="flex">
					<span class="btn-in-note hidden">
						<ComNoteGlobalButtonMore :data="i" @onEdit="onEdit"/>
					</span>
					<Button class="w-2rem h-2rem px-1 pb-1 pt-0 btn-in-note hidden" text rounded><ComIcon icon="pushPin" style="height:20px;"></ComIcon></Button>
				</div>
			</div>
			<div class="mt-1">
				<p>{{ i.content }}</p>
			</div>
		</div>
	</div>
</div>
</template>

<script setup>
import { ref, inject,useDialog,onMounted } from '@/plugin';
import ComAddNote from './ComAddNote.vue';
import ComNoteGlobalButtonMore from './ComNoteGlobalButtonMore.vue';
import ReservationStayDetail from "@/views/reservation/ReservationStayDetail.vue"
import ReservationDetail from "@/views/reservation/ReservationDetail.vue"
import ComFolioTransactionDetail from '@/views/reservation/components/reservation_stay_folio/ComFolioTransactionDetail.vue';
const frappe = inject('$frappe');
const gv = inject('$gv');
const db = frappe.db();
const dialog = useDialog()
const notes = ref([]);
const loading = ref(false);
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
		position:'top'
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
	db.getDocList('Frontdesk Note', {
		fields: ['name','note_date','reference_doctype','reference_name', "reservation", "reservation_stay", "content"],
		orderBy: {
			field: 'modified',
			order: 'desc',
		}
	}).then((docs) => {
		notes.value = docs;
		loading.value = false			
	}).catch((rr)=>{
		gv.toast('error', rr)
	})
}

onMounted(() => {
	onLoadData()
})

</script>
