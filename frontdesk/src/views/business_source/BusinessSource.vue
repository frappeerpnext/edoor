<template>
    <div class="flex-col flex" style="height: calc(100vh - 92px);"> 
        <div>
            <ComHeader colClass="col-6" isRefresh @onRefresh="Refresh()">
                <template #start>
                    <div class="text-xl md:text-2xl"> {{ $t('Business Source') }} </div>
                </template>
                <template #end>
                    <Button class="border-none" :label="isMobile ? $t('Add New') : $t('Add New Business Source') " icon="pi pi-plus"  @click="onAddNewBusinessSource" />
                </template>
            </ComHeader>
            <div class="mb-3 flex justify-between">
                <div class="flex flex-wrap gap-2">
                    <div v-if="!isMobile">
                        <span class="p-input-icon-left">
                            <i class="pi pi-search" />
                            <InputText v-model="filter.keyword" :placeholder=" $t('Search') " @input="onSearch" />
                        </span>
                    </div>
                    <div>
                        <Button icon="pi pi-sliders-h" class="content_btn_b" @click="advanceFilter"/>
                    </div>
                    <div v-if="gv.isNotEmpty(filter)">
                        <Button class="content_btn_b" label="Clear Filter" icon="pi pi-filter-slash" @click="onClearFilter"/>
                    </div>
                    
                </div>
                <div class="flex grap-2">
                    <div class="px-2">
                        <ComOrderBy doctype="Business Source" @onOrderBy="onOrderBy" />
                    </div>
                    <Button class="content_btn_b h-full px-3" @click="toggleShowColumn">
                        <ComIcon icon="iconEditGrid" height="16px"></ComIcon>
                    </Button>
                </div>
            </div>
        </div>
        <div class="overflow-auto h-full">
            <ComPlaceholder text="No Data" :loading="gv.loading"  :is-not-empty="pageState.totalRecords > 0">
                <DataTable 
                class="res_list_scroll"
                :resizableColumns="true"  
                columnResizeMode="expand" 
                showGridlines 
                stateStorage="local"
                stateKey="table_business_source_list_state" 
                scrollable 
                :reorderableColumns="true"   
                :value="data" tableStyle="min-width: 50rem" 
                @row-dblclick="onViewReservationStayDetail">
                    <Column v-for="c of columns.filter(r=>selectedColumns.includes(r.fieldname) && r.label)" :key="c.fieldname" :headerClass="c.header_class || ''" :field="c.fieldname" :header=" $t(c.label) " :labelClass="c.header_class || ''" :bodyClass="c.header_class || ''" 
                    :frozen="c.frozen" 
                    >
                        <template #body="slotProps" >
                            <Button v-if="c.fieldtype=='Link'" class="p-0 link_line_action1" @click="onOpenLink(c, slotProps.data)" link>
                                {{ slotProps.data[c.fieldname] }} 
                                <span v-if="c.extra_field_separator" v-html="c.extra_field_separator" > </span>
                                <span v-if="c.extra_field" >{{ slotProps.data[c.extra_field] }} </span>  
                            </Button>
                            <span v-else-if="c.fieldtype=='Date' && slotProps.data[c.fieldname]">{{ moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY") }} </span>
                            <span v-else-if="c.fieldtype=='Datetime'">{{ moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY  h:mm a") }} </span>
                            <ComTimeago v-else-if="c.fieldtype=='Timeago'" :date ="slotProps.data[c.fieldname]"  />
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
        <div>
            <Paginator class="p__paginator" :rows="pageState.rows"  :totalRecords="pageState.totalRecords" :rowsPerPageOptions="[20, 30, 40, 50]"
                    @page="pageChange" :pageLinkSize="isMobile ? '2' : '5'" >
                <template #start="slotProps">
                    <strong v-if="!isMobile" > {{ $t('Total Records') }}: <span class="ttl-column_re">{{ pageState.totalRecords }}</span></strong>
                </template>
            </Paginator>
        </div>
    </div>
 
    

<OverlayPanel ref="opShowColumn" style="width:35rem">
    <ComOverlayPanelContent title="Show / Hide Columns" @onSave="OnSaveColumn" ttl_header="mb-2" titleButtonSave="Save" @onCancel="onCloseColumn">
        <template #top>
            <span class="p-input-icon-left w-full mb-3">
                <i class="pi pi-search" />
                <InputText v-model="filter.search_field" :placeholder=" $t('Search') " class="w-full"/>
            </span>
        </template>
        <div class="grid">
            <div class="col-6 py-1" v-for="(c, index) in getColumns.filter(r=>r.label)" :key="index">
                <Checkbox v-model="c.selected" :binary="true" :inputId="c.fieldname"   />
                <label :for="c.fieldname">{{  $t(c.label)  }}</label>
            </div>
        </div>
        <template #footer-left>
            <Button class="border-none" icon="pi pi-replay" @click="onResetTable" :label=" $t('Reset List') "/>
        </template>
    </ComOverlayPanelContent>
</OverlayPanel>

<OverlayPanel ref="showAdvanceSearch" style="max-width:40rem">
    <ComOverlayPanelContent title="Advance Filter" @onSave="onClearFilter" titleButtonSave="Clear Filter" icon="pi pi-filter-slash" :hideButtonClose="false" @onCancel="onCloseAdvanceSearch">
        <div class="grid">
            <div class="col-12" v-if="isMobile">
                        <span class="p-input-icon-left w-full">
                            <i class="pi pi-search" />
                            <InputText v-model="filter.keyword" class="w-full" :placeholder="$t('Search')" @input="onSearch" />
                        </span>
                    </div>
            <div class="col-6">
                <ComAutoComplete isFull v-model="filter.selected_business_source_type" @onSelected="onSearch" placeholder="Business Source Type" doctype="Business Source Type" />
            </div>
            <div class="col-6">
                <ComSelect isFull v-model="filter.selected_country" @onSelected="onSearch" placeholder="Country" doctype="Country" isFilter />
            </div>
        </div>
    </ComOverlayPanelContent>
</OverlayPanel>

</template>
<script setup>
import { inject, ref, getCount, getDocList, onMounted,getApi,useDialog, computed , onUnmounted } from '@/plugin'
import Paginator from 'primevue/paginator';
import ComOrderBy from '@/components/ComOrderBy.vue';
import {Timeago} from 'vue2-timeago'
import ComAddBusinessSource from '@/views/business_source/components/ComAddBusinessSource.vue';
import ComBusinessSourceDetail from '@/views/business_source/components/ComBusinessSourceDetail.vue';
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const moment = inject("$moment")
const gv = inject("$gv")
const dialog = useDialog()
const opShowColumn = ref();
const data = ref([])
const filter = ref({})
const showAdvanceSearch = ref()
const pageState = ref({ order_by: "modified", order_type: "desc", page: 0, rows: 20, totalRecords: 0 })
const property = JSON.parse(localStorage.getItem("edoor_property"))
const isMobile = ref(window.isMobile) 

 
const columns = ref([
    { fieldname: 'name', label: 'Business Source', fieldtype:"Link",default:true},
    { fieldname: 'business_source_type', label:'Business Source Type', default:true},
    { fieldname: 'country', label: 'Country' , default:true},
    { fieldname: 'city', label: 'City' , default:true},
    { fieldname: 'contact_name', label: 'Contact Name' , default:true},
    { fieldname: 'phone_number', label: 'Phone Number' ,default:true},
    { fieldname: 'email', label: 'Email' ,default:true},
])
 
const selectedColumns = ref([]);
const toggleShowColumn = (event) => {
    opShowColumn.value.toggle(event);
}

function OnSaveColumn(event){
    selectedColumns.value = columns.value.filter(r=>r.selected).map(x=>x.fieldname)
    pageState.value.selectedColumns = selectedColumns.value
    localStorage.setItem("page_state_business_source", JSON.stringify(pageState.value) )
    opShowColumn.value.toggle(event);
}

function onResetTable(){
    localStorage.removeItem("page_state_business_source")
    localStorage.removeItem("table_business_source_list_state")
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
    const dialogRef = dialog.open(ComBusinessSourceDetail, {
        data: {
            name: data.name,
        },
        props: {
            header: 'Business Source - ' + data.name,
            style: {
                width: '80vw',
            },
            modal: true,
            position:"top",
            closeOnEscape: false,
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        },
        onClose: (options) => {
            const data = options.data;
            if (data) {
                loadData()
            }
        }
    });
}


const Refresh = debouncer(() => {
    pageState.value.page = 0
    loadData()
}, 500);

function pageChange(page) {
    pageState.value.page = page.page
    pageState.value.rows = page.rows

    loadData()
}

function loadData(show_loading=true) {
    gv.loading = show_loading
    let filters = [
    ["property","=",property.name]
    ]
    if (filter.value?.keyword) {
        filters.push(["keyword", 'like', '%' + filter.value.keyword + '%'])
    }
    if (filter.value?.selected_business_source_type) {
        filters.push(["business_source_type", '=', filter.value.selected_business_source_type])
    }
    if (filter.value?.selected_country) {
        filters.push(["country", '=', filter.value.selected_country])
    }
     
    let fields = [...columns.value.map(r=>r.fieldname),  ...columns.value.map(r=>r.extra_field)]
    fields = [...fields , ...selectedColumns.value]

    fields =  [...new Set(fields.filter(x=>x))]
 
    getDocList('Business Source', {

        fields: fields,
        orderBy: {
            field: '`tabBusiness Source`.' + pageState.value.order_by,
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
    localStorage.setItem("page_state_business_source", JSON.stringify(pageState.value))
}

function getTotalRecord(filters) {
    getCount('Business Source', filters)
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
    if(window.isMobile){
        let elem = document.querySelectorAll(".p-dialog");
        if (elem){
            elem = elem[elem.length-1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }
    let state = localStorage.getItem("page_state_business_source")
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
    getApi("frontdesk.get_meta",{doctype:"Business Source"}).then((result)=>{
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
    
    window.addEventListener('message', actionRefreshData, false)
})

const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if(e.data.action=="BusinessSource"){
            setTimeout(()=>{
                loadData(false) 
            },1000*2)
            
        }
    };
}

function onAddNewBusinessSource(){
    dialog.open(ComAddBusinessSource, {
        data:{
            // name: name.value,
            is_city_ledger: true
        },
        props: {
            header: `Add New Businese Source`,
            style: {
                width: '50vw',
            },
            modal: true,
            closeOnEscape: false,
            position: 'top',
            breakpoints:{
                '960px': '50vw',
                '640px': '100vw'
            },
        },
        onClose:(options) => {
            const data = options.data;
            if(data){
				loadData(data.name)
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

onUnmounted(() => {
    window.removeEventListener('message', actionRefreshData, false)
})

</script>