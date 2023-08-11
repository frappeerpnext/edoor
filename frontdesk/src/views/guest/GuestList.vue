<template>
    <div>
        <ComHeader isRefresh @onRefresh="Refresh()">
            <template #start>
                <div class="text-2xl">Guest Database</div>
            </template>
            <template #end>
              <Button @click="onAddNewGuest">Add New Guest</Button>
            </template>
        </ComHeader>
        <div class="mb-3">
            <div class="flex flex-wrap gap-2">
                <span class="p-input-icon-left">
                    <i class="pi pi-search" />
                    <InputText v-model="filter.keyword" placeholder="Search" @input="onSearch" />
                </span>

                <ComSelect optionLabel="customer_group_en" optionValue="name"
                    v-model="filter.selected_customer_group" @onSelected="onSearch" placeholder="Guest Type"
                    doctype="Customer Group" />
                <ComSelect :options="['Not Set', 'Male', 'Female']"
                    v-model="filter.selected_gender" @onSelected="onSearch" placeholder="Gender"
                     />
                
                     <ComSelect  
                    v-model="filter.selected_country" @onSelected="onSearch" placeholder="Country"
                    doctype="Country" isFilter />
                 
         
                <ComOrderBy doctype="Customer" @onOrderBy="onOrderBy" />
            </div>
        </div>
        
       

<Button   label="Show Column" @click="toggleShowColumn" />
<Button   label="Reset List" @click="onResetTable" />

 
        <DataTable  resizableColumns columnResizeMode="fit" showGridlines stateStorage="local" stateKey="table_reservation_stay_list_state" :reorderableColumns="true"   :value="data" tableStyle="min-width: 50rem" @row-dblclick="onViewReservationStayDetail">
            <Column v-for="c of columns.filter(r=>selectedColumns.includes(r.fieldname) && r.label)" :key="c.fieldname" :field="c.fieldname" :header="c.label" :labelClass="c.header_class || ''" :bodyClass="c.header_class || ''" 
            :frozen="c.frozen" 
            >
                <template #body="slotProps" >
                    <Button v-if="c.fieldtype=='link'" class="p-0 link_line_action1" @click="onOpenLink(c, slotProps.data)" link>
                        {{ slotProps.data[c.fieldname] }} 
                        <span v-if="c.extra_field_separator" v-html="c.extra_field_separator" > </span>
                        <span v-if="c.extra_field" >{{ slotProps.data[c.extra_field] }} </span>  
                    </Button>
                    <span v-else-if="c.fieldtype=='date' && slotProps.data[c.fieldname]">{{ moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY") }} </span>
                    <span v-else-if="c.fieldtype=='datetime'">{{ moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY  h:mm a") }} </span>
                    <Timeago v-else-if="c.fieldtype=='timeago'" :datetime="slotProps.data[c.fieldname]" long ></Timeago>
                    <div v-else-if="c.fieldtype=='room'" class="rounded-xl px-2 me-1 bg-gray-edoor inline room-num"
                    v-if="slotProps?.data && slotProps?.data?.rooms">
                    <template v-for="(item, index) in slotProps.data.rooms.split(',')" :key="index">
                        <span>{{ item }}</span>
                        <span v-if="index != Object.keys(slotProps.data.rooms.split(',')).length - 1">, </span>
                    </template>
                    </div>
                    <CurrencyFormat  v-else-if="c.fieldtype=='currency'" :value="slotProps.data[c.fieldname]" />
                    <span v-else>
                        {{ slotProps.data[c.fieldname] }}
                        <span v-if="c.extra_field_separator" v-html="c.extra_field_separator" > </span>
                        <span v-if="c.extra_field" >{{ slotProps.data[c.extra_field] }} </span>  
                    </span>
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
import { inject, ref, reactive, useToast, getCount, getDocList, onMounted,getApi,useDialog, computed } from '@/plugin'
import Paginator from 'primevue/paginator';
import ComOrderBy from '@/components/ComOrderBy.vue';
import {Timeago} from 'vue2-timeago'
import ComAddGuest from '@/views/guest/components/ComAddGuest.vue';

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
socket.on("RefreshGuestDatabase", (arg) => {

if (arg == property.name) {
    loadData()
     
}
})

const columns = ref([
    { fieldname: 'name', label: 'Customer Code', fieldtype:"link",post_message_action:"view_guest_detail" ,default:true},
    { fieldname: 'customer_name_en', label: 'Customer Name' ,default:true},
    { fieldname: 'gender', label: 'Gender' ,default:true},
    { fieldname: 'date_of_birth', fieldtype:"date", label: 'Birthdate' ,default:true},
    { fieldname: 'company_name', label: 'Company' ,default:true},
    { fieldname: 'country', label: 'Country' ,default:true},
    { fieldname: 'customer_group', label: 'Guest Type' ,default:true},
    { fieldname: 'phone_number', label: 'Phone Number' ,default:true},
    { fieldname: 'email_address', label: 'Email' ,default:true},
    { fieldname: 'identity_type', label: 'Identity Type' ,default:true},
    { fieldname: 'owner' ,  label: 'Created By'},
    { fieldname: 'creation' , fieldtype:"timeago",  label: 'Creation', header_class:"text-center", default:true},
    { fieldname: 'modified_by' ,  label: 'Modified By'},
    { fieldname: 'modified' , fieldtype:"timeago",  label: 'Last Modified', header_class:"text-center"},
  
])
 
const selectedColumns = ref([]);

const toggleShowColumn = (event) => {
    opShowColumn.value.toggle(event);
}

function OnSaveColumn(event){
    selectedColumns.value = columns.value.filter(r=>r.selected).map(x=>x.fieldname)
    pageState.value.selectedColumns = selectedColumns.value
    localStorage.setItem("page_state_customer", JSON.stringify(pageState.value) )
    opShowColumn.value.toggle(event);
}


function onResetTable(){
    localStorage.removeItem("page_state_customer")
    localStorage.removeItem("table_guest_customer_list_state")
    selectedColumns.value = columns.value.filter(r=>r.default).map(x=>x.fieldname)
    
    columns.value.forEach(r=>r.selected = selectedColumns.value.includes(r.fieldname))
    pageState.value.page =0
    pageState.value.rows=20

    loadData()

}
const getColumns = computed(()=>{
    if (filter.value.search_field){ 
        return columns.value.filter(r=>(r.label ||"").toLowerCase().includes(filter.value.search_field.toLowerCase())).sort((a, b) => a.label.localeCompare(b.label));
    }else {
        return columns.value.filter(r=>r.label).sort((a, b) => a.label.localeCompare(b.label));
    }
})
 
  
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



function loadData() {
    gv.loading = true
    let filters = []
    if (filter.value?.keyword) {
        filters.push(["keyword", 'like', '%' + filter.value.keyword + '%'])
    }
    if (filter.value?.selected_customer_group) {
        filters.push(["customer_group", '=', filter.value.selected_customer_group])
    }
    if (filter.value?.selected_country) {
        filters.push(["country", '=', filter.value.selected_country])
    }
    if (filter.value?.selected_gender) {
        filters.push(["gender", '=', filter.value.selected_gender])
    }
     
    let fields = [...columns.value.map(r=>r.fieldname),  ...columns.value.map(r=>r.extra_field)]
    fields = [...fields , ...selectedColumns.value]

    fields =  [...new Set(fields.filter(x=>x))]
 
    getDocList('Customer', {

        fields: fields,
        orderBy: {
            field: '`tabCustomer`.' + pageState.value.order_by,
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

    localStorage.setItem("page_state_customer", JSON.stringify(pageState.value))

}
function getTotalRecord(filters) {

    getCount('Customer', filters)
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
 
 


onMounted(() => {
    let state = localStorage.getItem("page_state_customer")
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
    getApi("frontdesk.get_meta",{doctype:"Customer"}).then((result)=>{
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

function onAddNewGuest(){
    dialog.open(ComAddGuest, {
        data:{
            // name: name.value,
        },
        props: {
            header: `Add New Guest`,
            style: {
                width: '50vw',
            },
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true,
            closeOnEscape: false,
            position: 'top'
        },
        onClose:(options) => {
            const data = options.data;
            if(data){
				loadData()
			}
        }
    });  
}
</script>