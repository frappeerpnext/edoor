<template>
    <div class="flex-col flex" style="height: calc(100vh - 92px);">
        <div>
            <ComHeader isRefresh @onRefresh="Refresh()">
                <template #start>
                    <div class="text-2xl">Guest Database</div>
                </template>
                <template #end>
                    <Button v-tooltip.left="'Add New Guest'" @click="onAddNewGuest" label="Add New Guest" class="d-bg-set btn-inner-set-icon border-none">
                        <ComIcon class="mr-2" icon="iconAddNewGuest"></ComIcon>
                        Add New Guest
                    </Button>
                </template>
            </ComHeader> 
            <div class="mb-3 flex justify-between">
                <div class="flex flex-wrap gap-2">
                    <div>
                        <span class="p-input-icon-left">
                            <i class="pi pi-search" />
                            <InputText v-model="filter.keyword" placeholder="Search" @input="onSearch" />
                        </span>
                    </div>
                    <div>
                        <Button icon="pi pi-sliders-h" class="content_btn_b" @click="advanceFilter"/>
                    </div>
                    <div v-if="gv.isNotEmpty(filter)">
                        <Button class="content_btn_b" label="Clear Filter" icon="pi pi-filter-slash" @click="onClearFilter"/>
                    </div>
                    <div>
                        <ComOrderBy doctype="Customer" @onOrderBy="onOrderBy" />
                    </div>
                </div>
                <div>
                    <Button class="content_btn_b h-full px-3" @click="toggleShowColumn">
                        <ComIcon icon="iconEditGrid" height="16px"></ComIcon>
                    </Button>
                </div>
            </div>
        </div>
        <div class="overflow-auto h-full">
            <ComPlaceholder text="No Data"  :loading="gv.loading"  :is-not-empty="data?.length > 0">       
                <DataTable 
                class="res_list_scroll"
                :resizableColumns="true"  
                columnResizeMode="fit" 
                showGridlines 
                stateStorage="local"
                stateKey="table_customer_list_state" 
                scrollable 
                :reorderableColumns="true"   
                :value="data" 
                tableStyle="min-width: 50rem" 
                @row-dblclick="onViewReservationStayDetail">
                    <Column v-for="c of columns.filter(r=>selectedColumns.includes(r.fieldname) && r.label)" :key="c.fieldname" :headerClass="c.header_class || ''" :field="c.fieldname" :header="c.label" :labelClass="c.header_class || ''" :bodyClass="c.header_class || ''" 
                    :frozen="c.frozen">
                        <template #body="slotProps" >
                            <Button v-if="c.fieldtype=='Link'" class="p-0 link_line_action1" @click="onOpenLink(c, slotProps.data)" link>
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
                            <span v-else>
                                {{ slotProps.data[c.fieldname] }}
                                <span v-if="c.extra_field_separator" v-html="c.extra_field_separator" > </span>
                                <span v-if="c.extra_field" >{{ slotProps.data[c.extra_field] }} </span>  
                            </span>
                        </template>
                    </Column>
                </DataTable>
            </ComPlaceholder> 
        </div>
        <div v-if="data.length > 0 && !gv.loading">
            <Paginator class="p__paginator" v-model:first="pageState.activePage" :rows="pageState.rows" :totalRecords="pageState.totalRecords" :rowsPerPageOptions="[20, 30, 40, 50]"
                @page="pageChange">
                <template #start="slotProps">
                    <strong>Total Records: <span class="ttl-column_re">{{ pageState.totalRecords }}</span></strong>
                </template>
            </Paginator>
        </div>
    </div>
    <OverlayPanel ref="opShowColumn" style="width:30rem;">
        <ComOverlayPanelContent title="Show / Hide Columns" @onSave="OnSaveColumn" ttl_header="mb-2" titleButtonSave="Save" @onCancel="onCloseColumn">
            <template #top>
                <span class="p-input-icon-left w-full mb-3">
                    <i class="pi pi-search" />
                    <InputText v-model="filter.search_field" placeholder="Search" class="w-full"/>
                </span>
            </template>
            <ul class="res__hideshow">
                <li class="mb-2" v-for="(c, index) in getColumns.filter(r=>r.label)" :key="index">
                    <Checkbox v-model="c.selected" :binary="true" :inputId="c.fieldname"   />
                    <label :for="c.fieldname">{{ c.label }}</label>
                </li>
            </ul>
            <template #footer-left>
                <Button class="border-none" icon="pi pi-replay" @click="onResetTable" label="Reset List"/>
            </template>
        </ComOverlayPanelContent>
    </OverlayPanel>

    <OverlayPanel ref="showAdvanceSearch" style="width:70rem">
        <ComOverlayPanelContent title="Advance Filter" @onSave="onClearFilter" titleButtonSave="Clear Filter" icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onCloseAdvanceSearch">
            <div class="grid">
                <ComSelect class="col-4" width="100%" optionLabel="customer_group_en" optionValue="name"
                    v-model="filter.selected_customer_group" @onSelected="onSearch" placeholder="Guest Type"
                    doctype="Customer Group" />
                <ComSelect class="col-4" width="100%" :options="['Not Set', 'Male', 'Female']"
                    v-model="filter.selected_gender" @onSelected="onSearch" placeholder="Gender"/>
                <ComSelect class="col-4" width="100%" v-model="filter.selected_country" @onSelected="onSearch" placeholder="Country"
                        doctype="Country" isFilter />
            </div>
        </ComOverlayPanelContent>
    </OverlayPanel>

</template>
<script setup>
import { inject, ref, getCount, getDocList, onMounted,getApi,useDialog, computed, onUnmounted } from '@/plugin'
import Paginator from 'primevue/paginator';
import ComOrderBy from '@/components/ComOrderBy.vue';
import {Timeago} from 'vue2-timeago'
import ComAddGuest from '@/views/guest/components/ComAddGuest.vue';

const moment = inject("$moment")
const gv = inject("$gv")
const dialog = useDialog()
const opShowColumn = ref();
const data = ref([])
const filter = ref({})
const showAdvanceSearch = ref()
const pageState = ref({ order_by: "modified", order_type: "desc", page: 0, rows: 20, totalRecords: 0, activePage: 0 })



window.socket.on("RefreshData", (arg) => {
   
    if (arg.property == window.property_name && arg.action == "refresh_guest_database") {
        setTimeout(function(){
            loadData(false)
        },3000) 
    }
})


const columns = ref([
    { fieldname: 'name', label: 'Customer Code', header_class:"text-center", fieldtype:"Link",post_message_action:"view_guest_detail" ,default:true},
    { fieldname: 'customer_name_en', label: 'Customer Name' ,default:true},
    { fieldname: 'gender', label: 'Gender' , header_class:"text-center", default:true},
    { fieldname: 'date_of_birth', fieldtype:"Date", header_class:"text-center", label: 'Birthdate' ,default:true},
    { fieldname: 'company_name', label: 'Company' ,default:true},
    { fieldname: 'country', label: 'Country' ,default:true},
    { fieldname: 'customer_group', label: 'Guest Type' ,default:true},
    { fieldname: 'phone_number', label: 'Phone Number' ,default:true},
    { fieldname: 'email_address', label: 'Email' ,default:true},
    { fieldname: 'identity_type', label: 'Identity Type' ,default:true},
    { fieldname: 'owner' ,  label: 'Created By'},
    { fieldname: 'creation' , fieldtype:"Timeago",  label: 'Creation', header_class:"text-center", default:true},
    { fieldname: 'modified_by' ,  label: 'Modified By'},
    { fieldname: 'modified' , fieldtype:"Timeago",  label: 'Last Modified', header_class:"text-center"},
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
    window.location.reload()
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

function loadData(show_loading = true) {
    gv.loading = show_loading
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

const onCloseColumn = () => {
    opShowColumn.value.hide()
}

const advanceFilter = (event) => {
    showAdvanceSearch.value.toggle(event);
}

const onClearFilter = () => {
    filter.value={}
    loadData()
    showAdvanceSearch.value.hide()
}

const onCloseAdvanceSearch = () => {
    showAdvanceSearch.value.hide()
}

const care = ref(0)
const dd = ref()
onMounted(()=>{
    const height = care.value.clientHeight
    dd.value = height
})

onUnmounted(() => {
    window.socket.off("RefreshData")
})

</script>