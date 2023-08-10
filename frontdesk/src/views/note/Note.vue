<template>
    <!-- <h1>Note list</h1> -->
    <!-- <p>@Ty you can bench mark from google keep if u want</p> -->
    <ComHeader isRefresh @onRefresh="Refresh()">
        <template #start>
            <div class="text-2xl">Note list</div>
        </template>
    </ComHeader>
    <div class="flex flex-wrap gap-2 items-center">
        <div class="col p-0">
            <div class="p-input-icon-left w-full">
                <i class="pi pi-search" />
                <InputText v-model="filter.keyword" class="w-full" placeholder="Search" @input="onSearch"/>
            </div>
        </div>
        <div class="col p-0">
            <div class="flex ">
                    <Calendar class="w-full" hideOnRangeSelection  dateFormat="dd-mm-yy" v-model="filter.date_range"
                selectionMode="range" :manualInput="false" @date-select="onDateSelect"
                placeholder="Select Date Range" :disabled="!filter.search_by_date" showIcon  />
                <Checkbox  v-model="filter.search_by_date" :binary="true" @change="onChecked"/>
            </div>
        </div>
        <div class="col p-0">
                <ComOrderBy doctype="Frontdesk Note" @onOrderBy="onOrderBy"/>
        </div>
         
    </div>
        
 
 

    

    <div>
    <Button label="Add Note" severity="warning" outlined icon="pi pi-plus" @click="onAddNote('')" />
    </div>
    

    <div v-for="i in notes" :key="index" class=" border-1 rounded-lg pt-2 px-3 mt-3 content-global-note relative">
      {{ i }}
       <Button label="Edit" @click="onEdit(i.name)"/>
       <Button @click="onDelete(i.name)">Delete</Button>
    </div>
  
 
    <Paginator :rows="pageState.rows" :totalRecords="pageState.totalRecords" :rowsPerPageOptions="[20, 30,40,50]"    @page="pageChange" ></Paginator>


</template>
<script setup>
import { ref, inject,onMounted,reactive,useDialog,getDocList,getCount,useConfirm,deleteDoc } from '@/plugin';

import ComAddNote from './ComAddNote.vue';
import Paginator from 'primevue/paginator';
import ComOrderBy from '@/components/ComOrderBy.vue';
const confirm = useConfirm()
const notes = ref([]);
const dialog = useDialog()
const loading = ref(false);
const gv = inject('$gv');
const moment = inject("$moment")

const filter = ref({})

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
					// // update bage total notes
					getTotalNote()
				}
            }
        });
}
 
const pageState = ref({order_by:"modified", order_type:"desc",page:0,rows:20,totalRecords:0})

 

function onDateSelect() {
    if(filter.value.date_range && filter.value.date_range[1]){
        onLoadData()
    }
}
function onChecked(){
    if(!filter.value.search_by_date){
        onLoadData()
    }else{
        onDateSelect()
    }
}

function pageChange(page){
    pageState.value.page=page.page
    pageState.value.rows=page.rows
    onLoadData()
}

function onLoadData(){
 
	loading.value = true
	let filters = []
	
	if (filter.value.keyword){
		filters.push(["content","like", '%' + filter.value.keyword + '%'])
	}
 
	if (filter.value.date_range && filter.value.search_by_date) {
        filters.push(['note_date', 'between',[ moment(filter.value.date_range[0]).format("YYYY-MM-DD"),moment(filter.value.date_range[1]).format("YYYY-MM-DD")]])
    }


	getDocList('Frontdesk Note', {
		fields: ['name','note_date','reference_doctype','is_pin','reference_name', "reservation", "reservation_stay", "content","modified_by",'modified','owner','creation'],
		filters:filters,
	    	orderBy: {
			field: pageState.value.order_by,
			order: pageState.value.order_type,
		},
        limit_start:((pageState.value?.page || 0 ) * (pageState.value?.rows || 20)) ,
        limit:pageState.value?.rows || 20,



	}).then((docs) => {
		notes.value = docs;
		loading.value = false			
	})

    getTotalRecord(filters)
}

function getTotalRecord(filters){
	
    getCount('Frontdesk Note', filters)
  .then((count) => pageState.value.totalRecords = count || 0)
	
}

function onOrderBy(data){
    pageState.value.order_by = data.order_by
    pageState.value.order_type = data.order_type
    pageState.value.page = 0
    onLoadData()
 
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

function onDelete (name){
        confirm.require({
        message: 'Are you sure you want to delete reservation note?',
        header: 'Confirmation',
        icon: 'pi pi-exclamation-triangle',
        acceptClass: 'border-none crfm-dialog',
        rejectClass: 'hidden',
        acceptIcon: 'pi pi-check-circle',
        acceptLabel: 'Ok',
        accept: () => {
            loading.value = true
             deleteDoc('Frontdesk Note',name )
                 .then(() =>{
                     onLoadData()

                 } ).catch((err)=>{
                    loading.value = false
                 })         
        },
    });
    }


const onSearch = debouncer(() => {
    onLoadData()
    }, 500);  

onMounted(() => {
	onLoadData()
})

function onAddNote(name){
    
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
            onClose:(options) => {
                const data = options.data;
                if(data){
                    dialogRef.value.close()
					onLoadData()
					// update bage total notes
					getTotalNote()
				}
            }
        });

}

</script>