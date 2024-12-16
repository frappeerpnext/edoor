<template>
    <ComDialogContent hideButtonOK hideButtonClose :hideIcon="false" :loading="loading">
       
            <div class="flex justify-content-between">
                <div class="col flex gap-2"  >
                    <div>
                        <InputText type="text" class="p-inputtext-sm w-full w-16rem" @input="onRefresh()"
                            :placeholder="$t('Search')" v-model="filter.keyword" :maxlength="50" />
                    </div>
                    <div class="w-16rem">
                        <ComAutoComplete v-model="filter.selected_business_source" placeholder="Business Source"
                            @onSelected="onRefresh()" doctype="Business Source" class="auto__Com_Cus w-full" />
                    </div>
                    <div>
                        <ComSelect v-model="filter.selected_room_type" extraFields="room_type" optionLabel="room_type"
                            optionValue="room_type"     @onSelected="onRefresh()" placeholder="Room Type"
                            doctype="Room Type" :filters="[['property', '=', property_name]]"></ComSelect>
                    </div>



                    <div    class="flex ml-2">
                        <tippy content="Arrival Date">
                        <Calendar   :selectOtherMonths="true" placeholder="Arrival Date" class="w-full" v-model="filter.arrival_date" @clear-click="onRefresh" @date-select="onRefresh" dateFormat="dd-mm-yy" showButtonBar showIcon/>
                    </tippy>
                    </div>

                    <div    class="flex ml-2">
                        <ComSelect tooltip="Order By"  :clear="false" v-model="pageState.order_by" placeholder="Sort Order Field"
                        @onSelected="onRefresh()" :options='columns'   optionLabel="label" optionValue="fieldname"    />

                        <ComSelect class="ml-2" v-model="pageState.order_type" placeholder="Sort Order Type"
                        @onSelected="onRefresh()"  :options='["asc","desc"]' :clear="false" />


                    </div>

                    <div>
                        <Button @click="onRefresh" icon="pi pi-refresh" :class="BtnClass ? BtnClass : ''"
                            class="d-bg-set btn-inner-set-icon p-button-icon-only content_btn_b"></Button>
                    </div> 
                </div>
                <div class="col text-right"><Button class="content_btn_b h-full px-3" @click="toggleShowColumn">
                        <ComIcon icon="iconEditGrid" height="16px"></ComIcon>
                    </Button>
                </div>
            </div>
           
        
        <!-- end filter -->
        <div class="overflow-auto h-full mt-4">
            <ComPlaceholder text="No Data" height="70vh" :is-not-empty="data?.length > 0">
                <DataTable class="res_list_scroll" :resizableColumns="true" columnResizeMode="expand" showGridlines
                    stateStorage="local" stateKey="table_reservation_stay_unassign_room_list_state" scrollable
                    :reorderableColumns="true" :value="data" :tableStyle="`min-width: ${width}%`"
                    @row-dblclick="onViewReservationStayDetail">
                    <Column
                        v-for="c of columns.filter(r => selectedColumns.includes(r.fieldname) && r.label && (r.can_view_rate || 'Yes') == 'Yes')"
                        :key="c.fieldname" :field="c.fieldname" :header="$t(c.label)"
                        :headerClass="c.header_class || ''" :bodyClass="c.header_class || ''" :frozen="c.frozen">
                        <template #body="slotProps">
                            <Button v-if="c.fieldtype == 'Link'" class="p-0 link_line_action1"
                                @click="onOpenLink(c, slotProps.data)" link>
                                {{ slotProps.data[c.fieldname] }}
                                <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
                                <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
                            </Button>
                            <span v-else-if="c.fieldtype == 'Date'">{{
                                moment(slotProps.data[c.fieldname]).format("DD-MM-YYYY") }} </span>
                            <ComTimeago v-else-if="c.fieldtype == 'Timeago'" :date="slotProps.data[c.fieldname]" />
                            <template v-else-if="c.fieldtype == 'Room'">
                                <div v-tippy="slotProps.data.rooms" v-if="slotProps?.data && slotProps?.data?.rooms">
                                    <div class="inline-block">
                                        <roomIDDisplay :item="slotProps.data.rooms.split(',')" />
                                    </div>
                                </div>
                                <div @click="onAssignRoom(slotProps.data)" class="link_line_action w-auto" v-else>
                                    <i class="pi pi-pencil"></i>
                                    {{ $t('Assign Room') }}

                                </div>
                            </template>
                            <template v-else-if="c.fieldname == 'owner' || c.fieldname == 'modified_by'">
                                <span>{{ slotProps.data[c.fieldname].split("@")[0] }}</span>
                            </template>
                            <CurrencyFormat v-else-if="c.fieldtype == 'Currency'"
                                :value="slotProps.data[c.fieldname]" />
                            <span v-else-if="c.fieldtype == 'Status'"
                                class="px-2 rounded-lg text-white p-1px border-round-3xl"
                                :style="{ backgroundColor: slotProps.data['status_color'] }">{{
                                    $t(slotProps.data[c.fieldname])
                                }}
                            </span>
                            <span v-else-if="c.fieldname == 'reservation_type'"
                                v-tippy="slotProps.data[c.fieldname] == 'FIT' ? 'Free Independent Traveler' : 'Group Inclusive Tour'">
                                {{ slotProps.data[c.fieldname] }}
                            </span>
                            <span v-else>
                                {{ slotProps.data[c.fieldname] }}
                                <span v-if="c.extra_field_separator" v-html="c.extra_field_separator"> </span>
                                <span v-if="c.extra_field">{{ slotProps.data[c.extra_field] }} </span>
                            </span>
                        </template>
                    </Column>
                </DataTable>
            </ComPlaceholder>
        </div>
        <div>
          
           
        </div>
        <Paginator class="p__paginator" v-model:first="pageState.activePage" :rows="pageState.rows"
                :totalRecords="pageState.totalRecords" :rowsPerPageOptions="[20, 30, 40, 50]" @page="pageChange"
                :pageLinkSize="isMobile ? '2' : '5'">
                <template #start="slotProps">
                    <strong v-if="!isMobile">{{ $t('Total Records') }} : <span class="ttl-column_re">{{
                        pageState.totalRecords }}</span></strong>
                </template>
            </Paginator>

            <OverlayPanel ref="opShowColumn" style="width:30rem;">
        <ComOverlayPanelContent ttl_header="mb-2" title="Show / Hide Columns" @onSave="OnSaveColumn" titleButtonSave="Save"
            @onCancel="onCloseColumn">
            <template #top>
                <span class="p-input-icon-left w-full mb-3">
                    <i class="pi pi-search" />
                    <InputText v-model="filter.search_field" :placeholder="$t('Search')" class="w-full" />
                </span>
            </template>
            <div class="grid">
                <div class="col-6 py-1" v-for="(c, index) in getColumns.filter(r => r.label)" :key="index">
                    <Checkbox v-model="c.selected" :binary="true" :inputId="c.fieldname" />
                    <label :for="c.fieldname">{{ $t(c.label) }}</label>
                </div>
            </div>
            <template #footer-left>
                <Button class="border-none" icon="pi pi-replay" @click="onResetTable" label="Reset List" />
            </template>
        </ComOverlayPanelContent>
    </OverlayPanel>

    </ComDialogContent>
</template>
<script setup>
import { inject, ref, reactive, useToast, postApi, getDocList, onMounted, getApi, computed, getDoc, onUnmounted } from '@/plugin'
import { useDialog } from 'primevue/usedialog';
import Paginator from 'primevue/paginator';
const loading = ref(false)
const dialogRef = inject("dialogRef");
const property_name = window.property_name
const isMobile = ref(window.isMobile)
import ComReservationStayAssignRoom from '@/views/reservation/components/ComReservationStayAssignRoom.vue';
const moment = inject("$moment")

const toast = useToast()
const opShowColumn = ref();
const width = ref(0)

const columns = ref([
    { fieldname: 'reservation', label: 'Reservation #', header_class: "text-center", fieldtype: "Link", post_message_action: "view_reservation_detail", default: true },
    { fieldname: 'name', label: 'Stay #', header_class: "text-center", fieldtype: "Link", post_message_action: "view_reservation_stay_detail", default: true },
    { fieldname: 'reference_number', label: 'Ref. #', default: true },
    { fieldname: 'reservation_type', label: 'Res. Type', header_class: "text-center", default: true },
    { fieldname: 'reservation_date', label: 'Res. Date', header_class: "text-center", fieldtype: "Date", frozen: true, default: true },
    { fieldname: 'arrival_date', label: 'Arrival', fieldtype: "Date", header_class: "text-center", default: true },
    { fieldname: 'departure_date', label: 'Departure', fieldtype: "Date", header_class: "text-center", default: true },
    { fieldname: 'room_nights', label: 'Room Night(s)', header_class: "text-center", default: true },
    { fieldname: 'room_types', label: 'Room Type', default: true },
    { fieldname: 'rooms', label: 'Rooms', fieldtype: "Room", header_class: "text-left", default: true },
    { fieldname: 'rate_type', label: 'Rate Type', default: false },
    
    { fieldname: 'room_rate', label: 'Room Rate', default: false },
    { fieldname: 'adult', label: 'Pax(A/C)', extra_field: "child", extra_field_separator: "/", header_class: "text-center", default: true },
    { fieldname: 'guest', extra_field: "guest_name", extra_field_separator: "-", label: 'Guest', fieldtype: "Link", post_message_action: "view_guest_detail", default: true },
    { fieldname: 'business_source', label: 'Business Source', default: true },
    { fieldname: 'adr', label: 'ADR', fieldtype: "Currency", header_class: "text-right", default: true, can_view_rate: window.can_view_rate ? 'Yes' : 'No' },
    { fieldname: 'total_amount', label: 'Total Room Rate', fieldtype: "Currency", header_class: "text-right", default: true, can_view_rate: window.can_view_rate ? 'Yes' : 'No' },
    { fieldname: 'owner', label: 'Created By' },
    { fieldname: 'creation', fieldtype: "Timeago", label: 'Creation', default: true },
    { fieldname: 'modified_by', label: 'Modified By' },
    { fieldname: 'modified', fieldtype: "Timeago", label: 'Last Modified', header_class: "text-center" },
    { fieldname: 'reservation_status', fieldtype: "Status", label: "Status", header_class: "text-center" },
    { fieldname: 'status_color' },
])

const getColumns = computed(() => {
    if (filter.value.search_field) {
        return columns.value.filter(r => (r.label || "").toLowerCase().includes(filter.value.search_field.toLowerCase())).sort((a, b) => a.label.localeCompare(b.label));
    } else {
        return columns.value.filter(r => r.label).sort((a, b) => a.label.localeCompare(b.label));
    }
})
const selectedColumns = ref([]);

const toggleShowColumn = (event) => {
    opShowColumn.value.toggle(event);
}

function OnSaveColumn(event) {
    selectedColumns.value = columns.value.filter(r => r.selected).map(x => x.fieldname)
    pageState.value.selectedColumns = selectedColumns.value
    localStorage.setItem("page_state_reservation_stay_unassign_room_list", JSON.stringify(pageState.value))
    opShowColumn.value.toggle(event);
}


function onResetTable() {
    localStorage.removeItem("page_state_reservation_stay_unassign_room_list")
    localStorage.removeItem("table_reservation_stay_unassign_room_list_state")
    window.location.reload()

}

const onCloseColumn = () => {
    opShowColumn.value.hide()
}

const dataTypeOptions = reactive([
    { label: 'Search Date', value: '' },
    { label: 'Arrival Date', value: 'arrival_date' },
    { label: 'Departure Date', value: 'departure_date' },
    { label: 'Reservation Date', value: 'reservation_date' },
    { label: 'Cancel/No Show/Voided Date', value: 'cancelled_date' }
])

const data = ref([])

const filter = ref({
    property: window.property_name,
    order_by: "arrival_date",
    order_by_type: "ASC",

})
let dateRange = reactive({
    start: '',
    end: ''
})
const pageState = ref({ order_by: "arrival_date", order_type: "asc", page: 0, rows: 20, totalRecords: 0, activePage: 0 })



const dialog = useDialog();

function onOpenLink(column, data) {
    window.postMessage(column.post_message_action + "|" + data[column.fieldname], '*')
}


const onRefresh = debouncer(() => {
    pageState.value.page = 0
    pageState.value.activePage = 0
    loadData();
    
}, 500);

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

function loadData(show_loading = true) {
    loading.value = show_loading
    let filters = [
        ["Reservation Stay", "property", '=', window.property_name],
        ["Reservation Stay", "rooms", 'is', "not set"],
        ["Reservation Stay", "is_active_reservation", '=', 1],
       
    ]
   
    if(filter.value?.arrival_date){
        filters.push(
        ["Reservation Stay", "arrival_date", '=', moment(filter.value?.arrival_date).format("YYYY-MM-DD")]
    )
    }else {
        filters.push(["Reservation Stay", "arrival_date", '>=', dateRange.start])
    }


    if (filter.value?.keyword) {
        filters.push(["keyword", 'like', '%' + filter.value.keyword + '%'])
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
        filters.push(["Reservation Stay Room", "room_type", "like",'%' + filter.value.selected_room_type + "%"])
    }
    if (filter.value?.selected_room_number) {
        filters.push(["Reservation Stay Room", "room_id", "=", filter.value.selected_room_number])
    }

    if (filter.value?.search_date_type && filter.value.date_range != null) {
        filters.push([filter.value.search_date_type, '>=', dateRange.start])
        filters.push([filter.value.search_date_type, '<=', dateRange.end])
    }




    let fields = [...columns.value.map(r => r.fieldname), ...columns.value.map(r => r.extra_field)]
    fields = [...fields, ...selectedColumns.value]

    fields = [...new Set(fields.filter(x => x))]
 
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
            loading.value = false
        })
        .catch((error) => {
            loading.value = false
            toast.add({ severity: 'error', summary: 'Error Message', detail: error, life: 3000 });
        });
    getTotalRecord(filters)
    localStorage.setItem("page_state_reservation_stay_unassign_room_list", JSON.stringify(pageState.value))

}
function getTotalRecord(filters) {

    postApi('frappe.desk.reportview.get_count', {
        doctype: "Reservation Stay",
        filters: filters
    }, "", false, "")
        .then((result) => {

            pageState.value.totalRecords = result.message || 0;
        })

}

function onOrderBy(data) {
    pageState.value.order_by = data.order_by
    pageState.value.order_type = data.order_type
    pageState.value.page = 0
    loadData()

}

function onSelectFilterDate(event) {
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




const actionRefreshData = async function (e) {
    if (e.isTrusted && typeof (e.data) != 'string') {
        if (e.data.action == "ComUnassignRoom") {
            setTimeout(() => {
                loadData(false)
            }, 1000 * 2)

        }
    };
}

onMounted(() => {
    
    if (window.isMobile) {
        let elem = document.querySelectorAll(".p-dialog");
        if (elem) {
            elem = elem[elem.length - 1]
            elem?.classList.add("p-dialog-maximized"); // adds the maximized class
        }
    }

    width.value = 100
    window.addEventListener('message', actionRefreshData, false);
    let state = localStorage.getItem("page_state_reservation_stay_unassign_room_list")
    if (state) {
        state = JSON.parse(state)
        state.page = 0
        pageState.value = state
        if (state.selectedColumns) {
            selectedColumns.value = state.selectedColumns

        } else {
            selectedColumns.value = columns.value.filter(r => r.default).map(x => x.fieldname)
        }
    } else {
        selectedColumns.value = columns.value.filter(r => r.default).map(x => x.fieldname)
    }
    columns.value.forEach(r => {
        r.selected = selectedColumns.value.includes(r.fieldname)
    });

    dateRange.start = dialogRef.value.data.date
    pageState.value.page = 0
    pageState.value.activePage = 0
    loadData()
    getApi("frontdesk.get_meta", { doctype: "Reservation Stay" }).then((result) => {
        result.message.fields.filter(r => r.in_list_view == 1 && !columns.value.map(x => x.fieldname).includes(r.fieldname)).forEach(r => {
            let header_class = ""

            if (["Date", "Int"].includes(r.fieldtype)) {
                header_class = "text-center"
            } else if (["Currency"].includes(r.fieldtype)) {
                header_class = "text-right"
            }

            columns.value.push({
                fieldname: r.fieldname,
                label: r.label,
                fieldtype: r.fieldtype.toLowerCase(),
                header_class: header_class,
                selected: selectedColumns.value.includes(r.fieldname)
            })
        })
    })

})



function onAssignRoom(data) {
    getDoc("Reservation Stay", data.name).then(doc => {
        const stay_room = doc.stays.find(r => !r.room_id)
        if (stay_room) {
            dialog.open(ComReservationStayAssignRoom, {
                data: { stay_room: stay_room },
                props: {
                    header: `Assign Room`,
                    style: {
                        width: '80vw',
                    },
                    modal: true,
                    closeOnEscape: false,
                    position: 'top',
                    breakpoints: {
                        '960px': '80vw',
                        '640px': '100vw'
                    },
                },
                onClose: (options) => {
                    if (options.data && options.data.message) {
                        loadData()
                    }
                }
            })
        }
    })
}

onUnmounted(() => {
    window.removeEventListener('message', actionRefreshData, false);
})



</script>