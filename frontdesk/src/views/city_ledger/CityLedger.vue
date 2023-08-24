<template>
    <ComHeader isRefresh @onRefresh="onRefresh()">
        <template #start>
            <div class="text-2xl">City Ledger</div>
        </template>
    </ComHeader>
    <!-- <h1>City ledger</h1> -->
    <!-- {{ loading }} -->
    <div class="flex justify-between">
        <div>
            <div class="flex gap-2">

                <InputText v-model="filter.keyword" placeholder="Search" @input="onSearch" />
                
                <hr />
                <Dropdown v-model="filter.order_by" :options="sortOptions" optionValue="fieldname" optionLabel="label"  placeholder="Sort By" @change="onSelectOrderBy"/>
                <Button @click="onOrderTypeClick">{{filter.order_type}}</Button>
            </div>
        </div>
        <div>
            <Button   label="Show Column" @click="toggleShowColumn" />
            <Button   label="Reset List" @click="onResetTable" />
            <Button   label="Print" @click="onPrint" />
        </div>
    </div>
    <Button v-for="(s, index) in summary" :key="index" label="s.label">
        {{s.label}}
        {{ s.value }}
    </Button>

    <DataTable resizableColumns columnResizeMode="fit" showGridlines stateStorage="local"
        stateKey="table_guest_ledger_state" :reorderableColumns="true" :value="data" tableStyle="min-width: 50rem" paginator
        :rows="20" :rowsPerPageOptions="[20, 30, 40, 50]">
        <Column v-for="c of columns?.filter(r => r.label && selectedColumns?.includes(r.fieldname))" :key="c.fieldname" :field="c.fieldname" :header="c.label"
            :headerClass="c.header_class || ''" :bodyClass="c.header_class || ''">
            <template #body="slotProps">
                <Button v-if="c.fieldtype == 'Link'" class="p-0 link_line_action1" @click="onOpenLink(c, slotProps.data)"
                    link>
                    {{ slotProps.data[c.fieldname] }}
                    <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
                    <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
                </Button>
                <span v-else-if="c.fieldtype == 'Date' && slotProps.data[c.fieldname]">{{
                    moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY") }} </span>
                <span v-else-if="c.fieldtype == 'Datetime'">{{ moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY h:mm a")
                }} </span>
                <Timeago v-else-if="c.fieldtype == 'Timeago'" :datetime="slotProps.data[c.fieldname]" long></Timeago>
                <div v-else-if="c.fieldtype == 'Room'" class="rounded-xl px-2 me-1 bg-gray-edoor inline room-num"
                    v-if="slotProps?.data && slotProps?.data?.rooms">
                    <template v-for="(item, index) in slotProps.data.rooms.split(',')" :key="index">
                        <span>{{ item }}</span>
                        <span v-if="index != Object.keys(slotProps.data.rooms.split(',')).length - 1">, </span>
                    </template>
                </div>
                <CurrencyFormat v-else-if="c.fieldtype == 'Currency'" :value="slotProps.data[c.fieldname]" />
                <span v-else-if="c.fieldtype=='ReservationStatus'"  class="px-2 rounded-lg me-2 text-white p-1px border-round-3xl"
                :style="{ backgroundColor: slotProps.data['reservation_status_color'] }">{{ slotProps.data[c.fieldname]
                }}</span>
                <span v-else>
                    {{ slotProps.data[c.fieldname] }}
                    <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
                    
                    <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
                </span>
            </template>
        </Column>

    </DataTable>

    
<OverlayPanel ref="opShowColumn">
    <InputText v-model="filter.search_field" placeholder="Search" />
    <div v-for="(c, index) in getColumns.filter(r=>r.label)" :key="index">
        
        <Checkbox v-model="c.selected" :binary="true" :inputId="c.fieldname"   />
        <label :for="c.fieldname">{{ c.label }}</label>
    </div>
    <Button @click="OnSaveColumn">Save</Button>
</OverlayPanel>

<OverlayPanel ref="showAdvanceSearch" style="width:70rem">
    <ComOverlayPanelContent title="Advance Filter" @onSave="onClearFilter" titleButtonSave="Clear Filter"
            icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onCloseAdvanceSearch"> 
        <Calendar :selectOtherMonths="true" v-model="filter.start_date" placeholder="Start Date" dateFormat="dd-mm-yy" @date-select="onDateSelect"
                        showIcon />
        <Calendar :selectOtherMonths="true" v-model="filter.end_date" placeholder="End Date" dateFormat="dd-mm-yy" showIcon  @date-select="onDateSelect" />
        <ComAutoComplete  v-model="filter.business_source" class="pb-2" placeholder="Business Source"
            doctype="Business Source" @onSelected="onSearch" />
            {{ filter.guest }}
        <ComAutoComplete  v-model="filter.city_ledger_type" class="pb-2" placeholder="City Ledger Type" doctype="City Ledger Type"
            @onSelected="onSearch" :filters="['property','=',property.name]" />
        <Button @click="onSearch">Refresh</Button>
    </ComOverlayPanelContent>
</OverlayPanel>

</template>

<script setup>
import { ref, onMounted,onUnmounted, inject,computed ,useDialog,getApi} from '@/plugin'
import { Timeago } from 'vue2-timeago'
import ComIFrameModal from '@/components/ComIFrameModal.vue';
const dialog = useDialog();
const edoor_setting = JSON.parse(localStorage.getItem("edoor_setting"))
const property = JSON.parse(localStorage.getItem("edoor_property"))
const data = ref()
const frappe = inject('$frappe');
const call = frappe.call();
const socket = inject("$socket")
const columns = ref()
const summary = ref()
const moment = inject("$moment")
const filter = ref({status:'All Status', start_date: moment().startOf('month').toDate(),end_date:moment().toDate(),guest:"", order_by:"modified",order_type:"desc" })
const loading = ref(false)
const selectedColumns = ref([])
const sortOptions = ref([
    {"fieldname":"modified", label:"Last Update On"},
    {"fieldname":"creation", label:"Created On"},
    {"fieldname":"name", label:"ID"}
])
const pageState = ref({})

const opShowColumn = ref();

const getColumns = computed(()=>{
    if (filter.value.search_field){ 
        return columns.value.filter(r=>(r.label ||"").toLowerCase().includes(filter.value.search_field.toLowerCase())).sort((a, b) => a.label.localeCompare(b.label));
    }else {
        return columns.value.filter(r=>r.label).sort((a, b) => a.label.localeCompare(b.label));
    }
})

function onOpenLink(column, data) {
    window.postMessage(column.post_message_action + "|" + data[column.fieldname], '*')
}

 

socket.on("RefresheDoorDashboard", (arg) => {
if (arg == property.name) {
    setTimeout(function(){
        loadData()
    },3000)
}
})

const toggleShowColumn = (event) => {
    opShowColumn.value.toggle(event);
}

function OnSaveColumn(event){
    selectedColumns.value = columns.value.filter(r=>r.selected).map(x=>x.fieldname)
    pageState.value.selectedColumns = selectedColumns.value
    localStorage.setItem("page_state_guest_ledger", JSON.stringify(pageState.value) )
    opShowColumn.value.toggle(event);
}


function onResetTable(){
    localStorage.removeItem("page_state_guest_ledger")
    localStorage.removeItem("table_guest_ledger_state")
    window.location.reload()
}

function onPrint(){
    const dialogRef = dialog.open(ComIFrameModal, {

data: {
    "doctype": "Customer",
    name: property.name,
    report_name: "xx",
    fullheight: true
},
props: {
    header:"U print me",
    style: {
        width: '90vw',
    },
    position:"top",
    modal: true,
    maximizable: true,
    closeOnEscape: false
}

});
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

function onOrderTypeClick(){
    filter.value.order_type = filter.value.order_type =="desc"?"asc":"desc"
    loadData()
}
function onSelectOrderBy(){
 
    loadData()
}

function onDateSelect(d){
    onSearch()
}

const onSearch = debouncer(() => {
 
    loadData();
}, 500);


function loadData() {
    loading.value = true
    const filters = JSON.parse(JSON.stringify(filter.value))
    filters.start_date = moment(filter.value.start_date).format("YYYY-MM-DD")
    filters.end_date = moment(filter.value.end_date).format("YYYY-MM-DD")
    filters.property = property.name
    call.get("frappe.desk.query_report.run",{
        report_name:edoor_setting.city_ledger_report_name,
        filters: filters
    }).then((result) => {
        columns.value = result.message.columns
        if (selectedColumns.value && selectedColumns.value.length==0){
          selectedColumns.value = columns.value.filter(r=>r.default).map(r=>r.fieldname)
        }  
        columns.value.forEach(r => {
                r.selected = selectedColumns.value.includes(r.fieldname)
        });

        data.value = result.message.result.slice(0, -1)
        summary.value = result.message.report_summary
        sortOptions.value = [...sortOptions.value, ...columns.value]
        loading.value = false

    }).catch((err) => {
        loading.value = false

        if (err._server_messages) {

            const _server_messages = JSON.parse(err._server_messages)
 
            _server_messages.forEach(r => {
                window.postMessage('show_alert|' + JSON.parse(r).message.replace("Error: ", ""), '*')
            });
        }else{
            window.postMessage('show_alert|' + err.exception , '*')
        }


    })
}

onMounted(() => {
    let state =JSON.parse( localStorage.getItem("page_state_guest_ledger"))
    
    if (state) {
        if( state.selectedColumns){
          
            selectedColumns.value = state.selectedColumns   
        }
    }

    loadData()
})
onUnmounted(() => {
    socket.off("RefresheDoorDashboard");
})


</script>