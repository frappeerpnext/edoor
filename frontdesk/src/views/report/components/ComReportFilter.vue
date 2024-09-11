<template>
 
    <div v-if="showFilter">
        <div class="">
            <ComReportFilterOnly v-if="!isMobile" :filter="filter" :selectedReport="selectedReport" />
        </div>
        <div class="w-full items-center flex justify-end p-3 pb-0">
            <div class="flex justify-end gap-2">
                <Button class="white-space-nowrap content_btn_b w-3rem justify-center" @click="customReport"><i
                        class="pi pi-cog text-xl" />
                </Button>
                <Button v-if="isMobile" class="white-space-nowrap content_btn_b w-3rem justify-center" @click="openFilter">
                    <i class="pi pi-sliders-h text-xl" />
                </Button>
                <div class="border-left-1 border-primary-100"></div>
                <Button class="white-space-nowrap content_btn_b" @click="onSearch"><i class="pi pi-file me-2" />
                    {{ $t('Preview Report') }}
                    
                    </Button> 
            </div>
        </div>
        <OverlayPanel ref="showCustomReport" :style="{ width: isMobile ? '100%' : '50rem' }">
            <ComOverlayPanelContent title="Advance Custom Report" hideButtonOK="true" :hideButtonClose="false"
                @onCancel="onCloseCustomReport">
                <div class="grid">
                    <div class="col-12 lg:col-6">
                        <label>{{ $t('Letter Head') }} </label><br>
                        <ComLetterHead v-model="filter.letterhead" @onSelect="onSelectLetterHead" />
                    </div>
                    <div class="col-12 lg:col-6">
                        <label>{{ $t('Language') }} </label><br>
                        <ComSelect :clear="false" v-model="filter._lang" doctype="Language" optionLabel="language_name"
                            optionValue="name" :filters="[['enabled', '=', 1]]" />
                    </div>
                </div>
            </ComOverlayPanelContent>
        </OverlayPanel>
        <OverlayPanel v-if="isMobile" ref="showOpenFilter" class="mt-0" style="width:100%;max-height: 100vh;overflow-y: auto;">
            <ComOverlayPanelContent title="Filter" hideButtonOK="true" :hideButtonClose="false"
                @onCancel="onCloseFilter">
                <ComReportFilterOnly :filter="filter" :selectedReport="selectedReport" />
            </ComOverlayPanelContent>
        </OverlayPanel>
    </div>
    <div class="reactive border-bottom-1 w-full" style="height:20px;">
        <i @click="onShowfilter" :class="showFilter ? 'pi-chevron-up' : 'pi-chevron-down'"
            class="pi h-1rem text-sm cursor-pointer  w-full text-center" style="left:56%;margin-top:-15px;"></i>
        <hr class="mt-3" />
    </div>
</template>
<script setup>
import { ref, inject, onMounted } from "@/plugin"
import ComReportFilterOnly from "@/views/report/components/ComReportFilterOnly.vue";
const emit = defineEmits(['onFilter', 'onGetHeight'])
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const isMobile = ref(window.isMobile)
const setting = JSON.parse(localStorage.getItem("edoor_setting"))
const working_day = JSON.parse(localStorage.getItem("edoor_working_day"))
const user = JSON.parse(localStorage.getItem("edoor_user"))
const property = setting.property
const moment = inject("$moment")
const showFilter = ref(true)
const showOpenFilter = ref()
const showCustomReport = ref()
const props = defineProps({
    selectedReport: Object,
    filter: Object
})

function onShowfilter() {
    showFilter.value = !showFilter.value
    localStorage.setItem("edoor_show_filter", showFilter.value ? "1" : "0")
    emit("onGetHeight", showFilter)
}

const customReport = (event) => {
    showCustomReport.value.toggle(event);
}
const openFilter = (event) => {
    showOpenFilter.value.toggle(event)
}
const onCloseCustomReport = () => {
    showCustomReport.value.hide()
}
const onCloseFilter = () => {
    showOpenFilter.value.hide()
}
const showAdvanceSearch = ref()
const advanceFilter = (event) => {
    showAdvanceSearch.value.toggle(event);
}

const filter = ref({
    _lang: user.language || "en",
    start_date: moment.utc(window.current_working_date).toDate(),
    end_date: moment.utc(window.current_working_date).toDate(),
    order_by: "Last Update On",
    audit_order: "Last Update On",
    is_active_reservation: "1",
    show_summary: "1",
    sort_order: "ASC",
    filter_date_by: "Arrival Date",
    summary_filter: "Business Source",
    group_by_ledger_type: "0",
    show_cash_count: "1",
    show_cash_float: "1",
    row_group: "Date",
  

})
function onSelectLetterHead(l) {
    filter.value.letterhead = l
}

const onSelectStartDate = (date) => {
    if (moment(date).isSame(moment(filter.value.end_date).format("yyyy-MM-DD")) || moment(date).isAfter(filter.value.end_date)) {
    
        filter.value.end_date = moment(date).add(0, 'days').toDate();
    }
}

function onSearch() {
    let f = {}

    const filter_option = props.selectedReport.filter_option + ",_lang,letterhead"
    if (filter_option) {
        filter_option.split(",").forEach(r => {

            f[r.trim()] = filter.value[r.trim()]

        })
    }
 
    
    if (f.start_date) {
        f.start_date = moment( moment.utc(moment(f.start_date).format("YYYY-MM-DD")).toDate()).format("YYYY-MM-DD")
    }

    if (f.end_date) {
        f.end_date = moment( moment.utc(moment(f.end_date).format("YYYY-MM-DD")).toDate()).format("YYYY-MM-DD")
    }
    
    window.report_filter = filter.value
 
    emit("onFilter", f)
 
}

onMounted(() => {
    onSearch()
})
</script>