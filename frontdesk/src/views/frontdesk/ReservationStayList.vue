<template>
    <div>
        <ComHeader isRefresh @onRefresh="Refresh()">
            <template #start>
                <div class="text-2xl">Reservation Stay List</div>
            </template>
            <template #end>
                <NewFITReservationButton />
                <NewGITReservationButton />

            </template>
        </ComHeader>
        <div class="mb-3">
            <div class="flex flex-wrap gap-2">
                <span class="p-input-icon-left">
                    <i class="pi pi-search" />
                    <InputText v-model="filter.keyword" placeholder="Search" @input="onSearch" />
                </span>

                <ComSelect optionLabel="business_source_type" optionValue="name"
                    v-model="filter.selected_business_source_type" @onSelected="onSearch" placeholder="Business Source Type"
                    doctype="Business Source Type" />

                <ComSelect isFilter groupFilterField="business_source_type"
                    :groupFilterValue="filter.selected_business_source_type" optionLabel="business_source"
                    optionValue="name" v-model="filter.selected_business_source" @onSelected="onSearch"
                    placeholder="Business Source" doctype="Business Source" />

                <ComSelect v-model="filter.selected_reservation_type"
                    @onSelected="onSearch" placeholder="Reservation Type" :options="['GIT', 'FIT']"/>

                <ComSelect optionLabel="reservation_status" optionValue="name" v-model="filter.selected_reservation_status"
                    @onSelected="onSearch" placeholder="Reservation Status" doctype="Reservation Status" />

                <ComSelect optionLabel="building" optionValue="name" v-model="filter.selected_building"
                    @onSelected="onSearch" placeholder="Building" doctype="Building" />

                <ComSelect isFilter optionLabel="room_type" optionValue="name" v-model="filter.selected_room_type"
                    @onSelected="onSearch" placeholder="Room Type" doctype="Room Type"></ComSelect>

                <ComSelect isFilter groupFilterField="room_type_id" :groupFilterValue="filter.selected_room_type"
                    optionLabel="room_number" optionValue="name" v-model="filter.selected_room_number"
                    @onSelected="onSearch" placeholder="Room Name" doctype="Room"></ComSelect>

                <ComSelect v-model="filter.search_date_type" :options="dataTypeOptions" optionLabel="label"
                    optionValue="value" placeholder="Search Date Type" :clear="false"
                    @onSelectedValue="onSelectFilterDate($event)"></ComSelect>

                <Calendar hideOnRangeSelection v-if="filter.search_date_type" dateFormat="dd-MM-yy"
                    v-model="filter.date_range" selectionMode="range" :manualInput="false" @date-select="onDateSelect"
                    placeholder="Select Date Range" />
                <ComOrderBy doctype="Reservation Stay" @onOrderBy="onOrderBy" />
            </div>
        </div>
        
       

<Button   label="Show Column" @click="toggleShowColumn" />
<Button   label="Reset List" @click="onResetTable" />

 
        <DataTable 
            resizableColumns 
            columnResizeMode="fit" 
            showGridlines   
            stateStorage="local" 
            stateKey="table_reservation_stay_list_state" 
            scrollable 
            :reorderableColumns="true"   :value="data" tableStyle="min-width: 50rem" @row-dblclick="onViewReservationStayDetail" >
            <Column v-for="c of columns.filter(r=>selectedColumns.includes(r.fieldname) && r.label)" :key="c.fieldname" :field="c.fieldname" :header="c.label" :headerClass="c.header_class || ''" :bodyClass="c.header_class || ''" 
            :frozen="c.frozen" 
            >
                <template #body="slotProps" >
                    <Button v-if="c.fieldtype=='Link'" class="p-0 link_line_action1" @click="onOpenLink(c, slotProps.data)" link>
                        {{ slotProps.data[c.fieldname] }} 
                        <span v-if="c.extra_field_separator" v-html="c.extra_field_separator" > </span>
                        <span v-if="c.extra_field" >{{ slotProps.data[c.extra_field] }} </span>  
                    </Button>
                    <span v-else-if="c.fieldtype=='Date'">{{ moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY") }} </span>
                    <Timeago v-else-if="c.fieldtype=='Timeago'" :datetime="slotProps.data[c.fieldname]" long ></Timeago>
                    <div v-else-if="c.fieldtype=='Room'" class="rounded-xl px-2 me-1 bg-gray-edoor inline room-num"
                    v-if="slotProps?.data && slotProps?.data?.rooms">
                    <template v-for="(item, index) in slotProps.data.rooms.split(',')" :key="index">
                        <span>{{ item }}</span>
                        <span v-if="index != Object.keys(slotProps.data.rooms.split(',')).length - 1">, </span>
                    </template>
                    </div>
                    <CurrencyFormat  v-else-if="c.fieldtype=='Currency'" :value="slotProps.data[c.fieldname]" />
                    <span v-else-if="c.fieldtype=='Status'"  class="px-2 rounded-lg me-2 text-white p-1px border-round-3xl"
                    :style="{ backgroundColor: slotProps.data['status_color'] }">{{ slotProps.data[c.fieldname]
                    }}</span>
                    <span v-else>
                        {{ slotProps.data[c.fieldname] }}
                        <span v-if="c.extra_field_separator" v-html="c.extra_field_separator" > </span>
                        <span v-if="c.extra_field" >{{ slotProps.data[c.extra_field] }} </span>  
                    </span>
                </template>
            </Column>
  
            
        </DataTable>
    </div>
 
    <Paginator :rows="pageState.rows" :totalRecords="pageState.totalRecords" :rowsPerPageOptions="[20, 30, 40, 50]"
        @page="pageChange">
        <template #start="slotProps">
            Total Records: {{ pageState.totalRecords }}
        </template>
    </Paginator>

<OverlayPanel ref="opShowColumn">
    <InputText v-model="filter.search_field" placeholder="Search" />
    <div v-for="(c, index) in getColumns.filter(r=>r.label)" :key="index">
        
        <Checkbox v-model="c.selected" :binary="true" :inputId="c.fieldname"   />
        <label :for="c.fieldname">{{ c.label }}</label>
    </div>
    <Button @click="OnSaveColumn">Save</Button>
</OverlayPanel>

</template>
<script setup>
import { inject, ref, reactive, useToast, getCount, getDocList, onMounted,getApi, computed } from '@/plugin'
 
import { useDialog } from 'primevue/usedialog';
import NewFITReservationButton from '../reservation/components/NewFITReservationButton.vue';
import NewGITReservationButton from "@/views/reservation/components/NewGITReservationButton.vue"
import Paginator from 'primevue/paginator';
import ComOrderBy from '@/components/ComOrderBy.vue';
import {Timeago} from 'vue2-timeago'

const moment = inject("$moment")
const gv = inject("$gv")
const toast = useToast()
const opShowColumn = ref();
const socket = inject("$socket")
socket.on("RefresheDoorDashboard", (arg) => {

if (arg == property.name) {
    loadData()
     
}
})



const columns = ref([
    { fieldname: 'reservation', label: 'Reservation #', fieldtype:"Link",post_message_action:"view_reservation_detail",default:true },
    { fieldname: 'name', label: 'Stay #', fieldtype:"Link",post_message_action:"view_reservation_stay_detail" ,default:true},
    { fieldname: 'reference_number', label: 'Ref. #' },
    { fieldname: 'reservation_type', label: 'Res. Type' ,default:true},
    { fieldname: 'reservation_date', label: 'Res. Date', fieldtype:"Date", frozen:true,default:true },
    { fieldname: 'arrival_date', label: 'Arrival', fieldtype:"Date",header_class:"text-center",default:true },
    { fieldname: 'departure_date', label: 'Departure', fieldtype:"Date",header_class:"text-center" ,default:true},
    { fieldname: 'room_nights', label: 'Room Nights',header_class:"text-center" ,default:true},
    { fieldname: 'rooms',  label: 'Rooms',fieldtype:"Room", header_class:"text-center" ,default:true},
    { fieldname: 'adult',  label: 'Pax(A/C)',extra_field:"child", extra_field_separator:"/", header_class:"text-center" ,default:true},
    { fieldname: 'guest' , extra_field:"guest_name", extra_field_separator:"-",  label: 'Guest',fieldtype:"Link", post_message_action:"view_guest_detail"  ,default:true},
    { fieldname: 'business_source' ,  label: 'Business Source'  ,default:true},
    { fieldname: 'adr' ,  label: 'ADR', fieldtype:"Currency" , header_class:"text-right" ,default:true},
    { fieldname: 'total_room_rate' ,  label: 'Total Room Rate', fieldtype:"Currency" , header_class:"text-right",default:true },
    { fieldname: 'total_debit' ,  label: 'Debit', fieldtype:"Currency" , header_class:"text-right" ,default:true},
    { fieldname: 'total_credit' ,  label: 'Credit', fieldtype:"Currency" , header_class:"text-right" ,default:true},
    { fieldname: 'balance' ,  label: 'Balance', fieldtype:"Currency" , header_class:"text-right" ,default:true},
    { fieldname: 'owner' ,  label: 'Created By'},
    { fieldname: 'creation' , fieldtype:"Timeago",  label: 'Creation', header_class:"text-center", default:true},
    { fieldname: 'modified_by' ,  label: 'Modified By'},
    { fieldname: 'modified' , fieldtype:"Timeago",  label: 'Last Modified', header_class:"text-center"},
    { fieldname: 'reservation_status', fieldtype:"Status", label:"Status" ,header_class:"text-center" },
    { fieldname: 'status_color' },
])
 
const getColumns = computed(()=>{
    if (filter.value.search_field){ 
        return columns.value.filter(r=>(r.label ||"").toLowerCase().includes(filter.value.search_field.toLowerCase())).sort((a, b) => a.label.localeCompare(b.label));
    }else {
        return columns.value.filter(r=>r.label).sort((a, b) => a.label.localeCompare(b.label));
    }
})
const selectedColumns = ref([]);

const toggleShowColumn = (event) => {
    opShowColumn.value.toggle(event);
}

function OnSaveColumn(event){
    selectedColumns.value = columns.value.filter(r=>r.selected).map(x=>x.fieldname)
    pageState.value.selectedColumns = selectedColumns.value
    localStorage.setItem("page_state_reservation_stay", JSON.stringify(pageState.value) )
    opShowColumn.value.toggle(event);
}


function onResetTable(){
    localStorage.removeItem("page_state_reservation_stay")
    localStorage.removeItem("table_reservation_stay_list_state")
   window.location.reload()

}

 


const dataTypeOptions = reactive([
    { label: 'Search Date', value: '' },
    { label: 'Arrival Date', value: 'arrival_date' },
    { label: 'Departure Date', value: 'departure_date' },
    { label: 'Reservation Date', value: 'reservation_date' }])
const data = ref([])

const filter = ref({})
let dateRange = reactive({
    start: '',
    end: ''
})
const pageState = ref({ order_by: "modified", order_type: "desc", page: 0, rows: 20, totalRecords: 0 })

const working_date = ref('')
const property = JSON.parse(localStorage.getItem("edoor_property"))
const dialog = useDialog();

 

function onOpenLink(column, data){
    window.postMessage(column.post_message_action + "|" + data[column.fieldname] , '*')
}

function Refresh() {
    pageState.value.page = 0
    loadData()
}
function onDateSelect() {
    if (filter.value.date_range && filter.value.date_range[0] && filter.value.date_range[1]) {
        dateRange.start = moment(filter.value.date_range[0]).format("YYYY-MM-DD")
        dateRange.end = moment(filter.value.date_range[1]).format("YYYY-MM-DD")
        loadData()
    }
}
function pageChange(page) {
    pageState.value.page = page.page
    pageState.value.rows = page.rows

    loadData()
}



function loadData() {
    gv.loading = true
    let filters = [
        ["Reservation Stay", "property", '=', property.name]
    ]
    if (filter.value?.keyword) {
        filters.push(["keyword", 'like', '%' + filter.value.keyword + '%'])
    }
    if (filter.value?.selected_business_source_type) {
        filters.push(["business_source_type", '=', filter.value.selected_business_source_type])
    }
    if (filter.value?.selected_business_source) {
        filters.push(["business_source", '=', filter.value.selected_business_source])
    }
    if (filter.value?.selected_reservation_status) {
        filters.push(["reservation_status", '=', filter.value.selected_reservation_status])
    }
    if (filter.value?.selected_reservation_type) {
        filters.push(["reservation_type", '=', filter.value.selected_reservation_type])
    }

    if (filter.value?.selected_room_type) {
        filters.push(["Reservation Stay Room", "room_type_id", "=", filter.value.selected_room_type])
    }
    if (filter.value?.selected_room_number) {
        filters.push(["Reservation Stay Room", "room_id", "=", filter.value.selected_room_number])
    }

    if (filter.value?.search_date_type && filter.value.date_range != null) {
        filters.push([filter.value.search_date_type, '>=', dateRange.start])
        filters.push([filter.value.search_date_type, '<=', dateRange.end])
    }
    
    let fields = [...columns.value.map(r=>r.fieldname),  ...columns.value.map(r=>r.extra_field)]
    fields = [...fields , ...selectedColumns.value]

    fields =  [...new Set(fields.filter(x=>x))]
 
    getDocList('Reservation Stay', {

        fields: fields,
        orderBy: {
            field: '`tabReservation Stay`.' + pageState.value.order_by,
            order: pageState.value.order_type,
        },
        filters: filters,
        limit_start: ((pageState.value?.page || 0) * (pageState.value?.rows || 20)),
        limit: pageState.value?.rows || 20,
    })
        .then((doc) => {
            data.value = doc
            gv.loading = false
        })
        .catch((error) => {
            gv.loading = false
            toast.add({ severity: 'error', summary: 'Error Message', detail: error, life: 3000 });
        });
    getTotalRecord(filters)

    localStorage.setItem("page_state_reservation_stay", JSON.stringify(pageState.value))

}
function getTotalRecord(filters) {

    getCount('Reservation Stay', filters)
        .then((count) => pageState.value.totalRecords = count || 0)

}
function onOrderBy(data) {
    pageState.value.order_by = data.order_by
    pageState.value.order_type = data.order_type
    pageState.value.page = 0
    loadData()

}

function onSelectFilterDate(event) {
    filter.value.search_date_type = event
    if (filter.value.search_date_type == '')
        filter.value.date_range = null
    loadData()
}


const onSearch = debouncer(() => {
    loadData();
}, 500);


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
 

getApi('frontdesk.get_working_day', {
    property: JSON.parse(localStorage.getItem("edoor_property")).name
}).then((r) => {
    working_date.value = r.message?.date_working_day
    // const startDate = moment(working_date.value)
    // const endDate = moment(working_date.value).add(1, 'days')
    // filter.value.date_range = [new Date(startDate), new Date(endDate)];
})

 


onMounted(() => {
    let state = localStorage.getItem("page_state_reservation_stay")
    if (state) {
        state = JSON.parse(state)
        state.page = 0
        pageState.value = state
        if( state.selectedColumns){
            selectedColumns.value = state.selectedColumns
            
        }else {
            selectedColumns.value = columns.value.filter(r=>r.default).map(x=>x.fieldname)
        }
    }else {
         selectedColumns.value = columns.value.filter(r=>r.default).map(x=>x.fieldname) 
    }
    columns.value.forEach(r => {
        r.selected = selectedColumns.value.includes(r.fieldname)
    });
    loadData()
    getApi("frontdesk.get_meta",{doctype:"Reservation Stay"}).then((result)=>{
        console.log(result.message)
        result.message.fields.filter(r=>r.in_list_view==1 && !columns.value.map(x=>x.fieldname).includes(r.fieldname)).forEach(r=>{
            let header_class = ""
             
            if (["Date","Int"].includes(r.fieldtype)){
                header_class ="text-center"
            }else if(["Currency"].includes(r.fieldtype)){
                header_class ="text-right"
            }
             
            columns.value.push({
                fieldname:r.fieldname,
                header:r.label,
                fieldtype:r.fieldtype.toLowerCase(),
                header_class:header_class,
                selected:selectedColumns.value.includes(r.fieldname)
            })
        })
    })

})
</script>