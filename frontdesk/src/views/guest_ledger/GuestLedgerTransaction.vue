<template>
    <h1>Guest ledger Transasction</h1>
{{ loading }}

    <InputText v-model="filter.keyword" placeholder="Search" @input="onSearch" />
    <Calendar :selectOtherMonths="true" v-model="filter.start_date" placeholder="Start Date" dateFormat="dd-mm-yy" @date-select="onDateSelect"
        showIcon />
    <Calendar :selectOtherMonths="true" v-model="filter.end_date" placeholder="End Date" dateFormat="dd-mm-yy" showIcon  @date-select="onDateSelect" />
    <ComAutoComplete isIconSearch v-model="filter.business_source" class="pb-2" placeholder="Business Source"
        doctype="Business Source" @onSelected="onSearch" />
        {{ filter.guest }}
    <ComAutoComplete isIconSearch v-model="filter.guest" class="pb-2" placeholder="Guest" doctype="Customer"
        @onSelected="onSearch" />
        <ComAutoComplete  v-model="filter.reservation" class="pb-2" placeholder="Reservation #" doctype="Reservation"
        @onSelected="onSearch" :filters="{property:property.name}"  />
    <ComAutoComplete  v-model="filter.reservation_stay" class="pb-2" placeholder="Reservation Stay #" doctype="Reservation Stay"
        @onSelected="onSearch" :filters="{property:property.name}"  />
    <ComAutoComplete  v-model="filter.account_name" class="pb-2" placeholder="Account Name" doctype="Account Code"
        @onSelected="onSearch" :filters="{property:property.name}"  />
    <ComAutoComplete  v-model="filter.parent_account_name" class="pb-2" placeholder="Parent Acount Name" doctype="Reservation"
        @onSelected="onSearch" :filters="{property:property.name}"  />
Show Master Folio Only
        <Checkbox 
        @change="onSearch"
        v-model="filter.is_master" :binary="true" :trueValue="1" :falseValue="0" />

<Button @click="onSearch">Refresh</Button>
    <hr />
    <Dropdown v-model="filter.order_by" :options="sortOptions" optionValue="fieldname" optionLabel="label"  placeholder="Sort By" @change="onSelectOrderBy"/>

 

  <Button @click="onOrderTypeClick">{{filter.order_type}}</Button>

    <hr />
    <Button v-for="(s, index) in summary" :key="index" label="s.label">
        {{s.label}}
        <CurrencyFormat :value="s.value" class="p-0 " />
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
                <span v-else>
                    {{ slotProps.data[c.fieldname] }}
                    <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
                    <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
                </span>
            </template>
        </Column>

    </DataTable>
</template>

<script setup>
import { ref, onMounted,onUnmounted, inject } from '@/plugin'
import { Timeago } from 'vue2-timeago'
const edoor_setting = JSON.parse(localStorage.getItem("edoor_setting"))
const property = JSON.parse(localStorage.getItem("edoor_property"))
const data = ref()
const frappe = inject('$frappe');
const call = frappe.call();
const socket = inject("$socket")
const columns = ref()
const summary = ref()
const selectedColumns = ref([])
const moment = inject("$moment")
const filter = ref({ start_date: moment().startOf('month').toDate(),end_date:moment().toDate(),guest:"", order_by:"modified",order_type:"desc" })
const loading = ref(false)

const sortOptions = ref([
    {"fieldname":"modified", label:"Last Update On"},
    {"fieldname":"creation", label:"Created On"},
    {"fieldname":"name", label:"ID"}
])


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
    
    call.get("frappe.desk.query_report.run",{
        report_name:edoor_setting.guest_ledger_transaction_report,
        filters:{
            start_date:moment(filter.value.start_date).format("YYYY-MM-DD"), 
            end_date:moment(filter.value.end_date).format("YYYY-MM-DD"),
            property:property.name,
            guest:filter.value?.guest || "",
            business_source:filter.value?.business_source || "",
            reservation:filter.value?.reservation || "",
            reservation_stay:filter.value?.reservation_stay || "",
            keyword:filter.value?.keyword || "",
            order_by:filter.value.order_by,
            order_type:filter.value.order_type,
            is_master:filter.value.is_master
    }
    }).then((result) => {
        columns.value = result.message.columns
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