<template>
    <div>
        <ComHeader isRefresh @onRefresh="Refresh()">
            <template #start>
                
                <div class="text-2xl"> {{name}}</div>City Ledger Transaction
            </template>
            <template #end>
                <Button @click="AddTransaction(d)" v-for="(d, index) in setting.account_group.filter(r=>r.show_in_city_ledger==1)" :key="index">Post {{d.account_name}}</Button>
 
          
            </template>
        </ComHeader>
        <div class="mb-3">
            <div class="flex flex-wrap gap-2">
                <span class="p-input-icon-left">
                    <i class="pi pi-search" />
                    <InputText  v-model="filter.keyword" placeholder="Search" @input="onSearch" />
                </span>
                <div class="col-2 p-0">
                    <div class="flex relative">
                            <Calendar class="w-full" inputClass="pl-6" hideOnRangeSelection  dateFormat="dd-mm-yy" v-model="filter.date_range"
                        selectionMode="range" :manualInput="false" @date-select="onDateSelect"
                        placeholder="Select Date Range" :disabled="!filter.search_by_date" showIcon  />
                        <div class="check-box-filter">
                            <Checkbox  v-model="filter.search_by_date" :binary="true" @change="onChecked"/>
                        </div>
                    </div>
                </div>
                <ComAutoComplete
                     v-model="filter.selected_reservation" @onSelected="onSearch" placeholder="Reservation #"
                    doctype="Reservation" :filters="{property:property.name}"/>
              
                <ComAutoComplete 
                    v-model="filter.selected_reservation_stay" @onSelected="onSearch" placeholder="Reservation Stay"
                    doctype="Reservation Stay" :filters="{property:property.name}"/>
                <ComSelect :filters="[['property','=',property.name]]"  v-model="filter.selected_room_type" @onSelected="onSearch" placeholder="Room Type"
                    doctype="Room Type" isFilter optionLabel="room_type" optionValue="name"
                    />
                <ComSelect :filters="[['property','=',property.name]]" optionLabel="room_number" optionValue="name" v-model="filter.selected_room" @onSelected="onSearch"
                    placeholder="Room" doctype="Room" isFilter />
                
                <ComAutoComplete v-model="filter.selected_guest" @onSelected="onSearch" placeholder="Guest"
                    doctype="Customer" isFilter 
                    />
                <ComAutoComplete @onSelected="onSearch" v-model="filter.selected_account_code" placeholder="Account Code"
                    doctype="Account Code" isFilter 
                    />
                <ComAutoComplete @onSelected="onSearch" v-model="filter.selected_account_category" placeholder="Account Category"
                    doctype="Account Category" isFilter 
                    />
               
                <ComOrderBy doctype="Folio Transaction" @onOrderBy="onOrderBy" />
            </div>
        </div>
        
       

<Button   label="Show Column" @click="toggleShowColumn" />
<Button   label="Reset List" @click="onResetTable" />


        <DataTable  resizableColumns columnResizeMode="fit" showGridlines stateStorage="local"
            stateKey="table_folio_transaction_list_state" :reorderableColumns="true"
               :value="data" tableStyle="min-width: 50rem" @row-dblclick="onViewReservationStayDetail">
            <Column v-for="c of columns.filter(r=>selectedColumns.includes(r.fieldname) && r.label)" :key="c.fieldname" :field="c.fieldname" :header="c.label" :headerClass="c.header_class || ''" :bodyClass="c.header_class || ''" 
            :frozen="c.frozen" 
            >
                <template #body="slotProps" >
                    <Button  v-if="c.fieldtype=='Link' && slotProps.data[c.fieldname]" class="p-0 link_line_action1" @click="onOpenLink(c, slotProps.data)" link>
                        {{ slotProps.data[c.fieldname] }} 
                        <span v-if="c.extra_field_separator" v-html="c.extra_field_separator" > </span>
                        <span v-if="c.extra_field" >{{ slotProps.data[c.extra_field] }} </span>  
                    </Button>
                    <span v-else-if="c.fieldtype=='Date' && slotProps.data[c.fieldname]">{{ moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY") }} </span>
                    <span v-else-if="c.fieldtype=='Datetime'">{{ moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY  h:mm a") }} </span>
                    <Timeago v-else-if="c.fieldtype=='Timeago'" :datetime="slotProps.data[c.fieldname]" long ></Timeago>
                    <div v-else-if="c.fieldtype=='Room'" class="rounded-xl px-2 me-1 bg-gray-edoor inline room-num"
                    v-if="slotProps?.data && slotProps?.data?.rooms">
                    <template v-for="(item, index) in slotProps.data.rooms.split(',')" :key="index">
                        <span>{{ item }}</span>
                        <span v-if="index != Object.keys(slotProps.data.rooms.split(',')).length - 1">, </span>
                    </template>
                    </div>
                    <CurrencyFormat  v-else-if="c.fieldtype=='Currency'" :value="slotProps.data[c.fieldname]" />
                    <div v-else-if="c.fieldtype=='Debit'">
                        <CurrencyFormat v-if="slotProps.data.type=='Debit'" :value="slotProps.data[c.fieldname]" />
                        <span v-else>-</span>
                    </div>
                    <div v-else-if="c.fieldtype=='Credit'">
                        <CurrencyFormat v-if="slotProps.data.type=='Credit'" :value="slotProps.data[c.fieldname]" />
                        <span v-else>-</span>
                    </div>
            
                    
                    <span v-else>
                        <div v-if="slotProps.data[c.fieldname]">
                            {{ slotProps.data[c.fieldname] }}
                            <span v-if="c.extra_field_separator" v-html="c.extra_field_separator" > </span>
                            <span v-if="c.extra_field" >{{ slotProps.data[c.extra_field] }} </span>  
                        </div>
                    </span>
                    
                </template> 
                
            </Column>
            <Column>
                <template #body="slotProps">
                        <Button @click="onEdit">Edit</Button>
                        <Button>Delete</Button>
                </template>
            </Column>

        </DataTable>
    </div>
 
    <Paginator :rows="pageState.rows"  :totalRecords="pageState.totalRecords" :rowsPerPageOptions="[20, 30, 40, 50]"
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
import { inject, ref, reactive, useToast, getCount, getDocList, onMounted, onUnmounted,getApi,useDialog, computed } from '@/plugin'
import Paginator from 'primevue/paginator';
import ComOrderBy from '@/components/ComOrderBy.vue';
import {Timeago} from 'vue2-timeago'

import ComAddFolioTransaction from '@/views/reservation/components/ComAddFolioTransaction.vue';
const props = defineProps({
    name:String
})

const moment = inject("$moment")
const gv = inject("$gv")
const toast = useToast()
const dialog = useDialog()
const opShowColumn = ref();

const socket = inject("$socket")

const data = ref([])
const filter = ref({})
const pageState = ref({ order_by: "modified", order_type: "desc", page: 0, rows: 20, totalRecords: 0 })
const property = JSON.parse(localStorage.getItem("edoor_property"))
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const dialogRef = inject("dialogRef")

socket.on("RefreshData", (arg) => {

    if (arg.property == property.name && arg.action=="refresh_folio_transaction" ) {

        loadData()
    }
})

const columns = ref([
    { fieldname: 'name', label: 'Folio Transaction Code', fieldtype:"Link",post_message_action:"view_folio_transaction_detail" ,default:true},
    { fieldname: 'posting_date', label: 'Date',fieldtype: "Date", default:true,header_class:"text-center" },
    { fieldname: 'room_number', label: 'Room Number' ,default:true, header_class:"text-center"},
    { fieldname: 'account_code' , extra_field:"account_name", extra_field_separator:"-",  label: 'Account Code',default:true},
    { fieldname: 'guest' , extra_field:"guest_name", extra_field_separator:"-",  label: 'Guest',fieldtype:"Link", post_message_action:"view_guest_detail"  ,default:true},
    { fieldname: 'total_amount', label: 'Debit',fieldtype:"Debit",default:true,header_class:"text-right"},
    { fieldname: 'total_amount', label: 'Credit',fieldtype:"Credit",default:true,header_class:"text-right"},
    { fieldname: 'owner', label: 'User' ,default:true},
    { fieldname: 'note', label: 'Note' ,default:true},
    { fieldname: 'type',default:true},
])
 
const selectedColumns = ref([]);

const toggleShowColumn = (event) => {
    opShowColumn.value.toggle(event);
}

function onEdit(){
    alert(123)
}
function OnSaveColumn(event){
    selectedColumns.value = columns.value.filter(r=>r.selected).map(x=>x.fieldname)
    pageState.value.selectedColumns = selectedColumns.value
    localStorage.setItem("page_state_folio_transaction", JSON.stringify(pageState.value) )
    opShowColumn.value.toggle(event);
}


function onResetTable(){
    localStorage.removeItem("page_state_folio_transaction")
    localStorage.removeItem("table_folio_transaction_list_state")
    window.location.reload()
}
const getColumns = computed(()=>{
    if (filter.value.search_field){ 
        return columns.value.filter(r=>(r.label ||"").toLowerCase().includes(filter.value.search_field.toLowerCase())).sort((a, b) => a.label.localeCompare(b.label));
    }else {
        return columns.value.filter(r=>r.label).sort((a, b) => a.label.localeCompare(b.label));
    }
})

function AddTransaction(account_code){

        const dialogRef = dialog.open(ComAddFolioTransaction, {
            data: {
                new_doc:{
                    transaction_type:"City Ledger",
                    transaction_number:props.name,
                    property: property.name,
                    account_group:account_code.name
                }
            },
            props: {
                header: 'Post ' + account_code.account_name + ' to City Ledger ' + props.name,
                style: {
                    width: '50vw',
                },

                modal: true,
                position: "top",
                closeOnEscape: false
            },
            onClose: (options) => {
                const data = options.data;

                if (data) {
                    loadData()
                }

            }
        })

 

}
  
function onOpenLink(column, data){
    window.postMessage(column.post_message_action + "|" + data[column.fieldname] , '*')
}

function Refresh() {
    pageState.value.page = 0
    loadData()
}

function pageChange(page) {
    pageState.value.page = page.page
    pageState.value.rows = page.rows

    loadData()
}
function onDateSelect() {
    if(filter.value.date_range && filter.value.date_range[1]){
        loadData()
    }
}
function onChecked(){
    if(!filter.value.search_by_date){
        loadData()
    }else{
        onDateSelect()
    }
}

function loadData() {
   
    gv.loading = true
    let filters = [
        ["property","=",property.name],
        ["transaction_type","=","City Ledger"],
        ["transaction_number","=",props.name],
    ]
    if (filter.value?.keyword) {
        filters.push(["keyword", 'like', '%' + filter.value.keyword + '%'])
    }
    if (filter.value.date_range && filter.value.search_by_date) {
        filters.push(['posting_date', 'between',[ moment(filter.value.date_range[0]).format("YYYY-MM-DD"),moment(filter.value.date_range[1]).format("YYYY-MM-DD")]])
    }
    if (filter.value?.selected_reservation) {
         filters.push(["reservation", '=', filter.value.selected_reservation])
    }
    if (filter.value?.selected_reservation_stay) {
         filters.push(["reservation_stay", '=', filter.value.selected_reservation_stay])
    }
    if (filter.value?.selected_room) {
         filters.push(["room_id", '=', filter.value.selected_room])
    }
    if (filter.value?.selected_room_type) {
         filters.push(["room_type_id", '=', filter.value.selected_room_type])
     }
     if (filter.value?.selected_guest) {
         filters.push(["guest", '=', filter.value.selected_guest])
     }
     if (filter.value?.selected_account_code) {
         filters.push(["account_code", '=', filter.value.selected_account_code])
     }
     if (filter.value?.selected_account_category) {
         filters.push(["account_category", '=', filter.value.selected_account_category])
     }
 
    let fields = [...columns.value.map(r=>r.fieldname),  ...columns.value.map(r=>r.extra_field)]
    fields = [...fields , ...selectedColumns.value]

    fields =  [...new Set(fields.filter(x=>x))]
 
    getDocList('Folio Transaction', {

        fields: fields,
        orderBy: {
            field: '`tabFolio Transaction`.' + pageState.value.order_by,
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
         
        });
    getTotalRecord(filters)

    localStorage.setItem("page_state_folio_transaction", JSON.stringify(pageState.value))

}
function getTotalRecord(filters) {

    getCount('Folio Transaction', filters)
        .then((count) => pageState.value.totalRecords = count || 0)

}
function onOrderBy(data) {
    pageState.value.order_by = data.order_by
    pageState.value.order_type = data.order_type
    pageState.value.page = 0
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
 
 


onMounted(() => {
 
    let state = localStorage.getItem("page_state_folio_transaction")
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
    getApi("frontdesk.get_meta",{doctype:"Folio Transaction"}).then((result)=>{
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
                label:r.label,
                fieldtype:r.fieldtype.toLowerCase(),
                header_class:header_class,
                selected:selectedColumns.value.includes(r.fieldname)
            })
        })
    })

})

 
onUnmounted(()=>{
    socket.off("RefreshData");
})
</script>