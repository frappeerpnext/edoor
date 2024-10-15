<template>
   
    <div class="mt-2 view-table-iframe">
        <ComPrintFormatSortOrderOption :print_format="filters.print_format" @onSelected="onSelectSortOrder" />
        <div v-html="html" class="view_table_style min_table_ui_height "></div>
        
    </div>
</template>


<script setup>
import { inject, ref, onMounted, computed, getApi,watch } from '@/plugin'
import ComPrintFormatSortOrderOption from '@/views/dashboard/components/ComPrintFormatSortOrderOption.vue';

const props = defineProps({
    filters: Object
})
import { i18n } from '@/i18n';
const { t: $t } = i18n.global;
const property = JSON.parse(localStorage.getItem("edoor_property"))
const html = ref("")
const param = ref({})
const moment = inject("$moment")
const gv = inject("$gv")
const order_by = ref("")
const order_by_type = ref("ASC")

watch(() => props.filters, (newValue, oldValue) => {
    LoadData()
})


function onSelectSortOrder(sort_order_options) {
    order_by.value = sort_order_options.order_by
    order_by_type.value = sort_order_options.order_by_type
    LoadData()
}
function LoadData() {
    param.value.doc = decodeURIComponent("Business Branch")
    param.value.name = decodeURIComponent(property.name)
    param.value.format = decodeURIComponent(gv.getCustomPrintFormat(props.filters.print_format))
    param.value._lang = localStorage.getItem("lang") || "en"
    param.value.letterhead = decodeURIComponent("No Letterhead")
    param.value.no_letterhead = 1
    param.value.show_toolbar = 0
    param.value.can_view_rate = window.can_view_rate
    param.value.view = "ui"
    param.value.date = props.filters.selected_date
    param.value.settings = decodeURIComponent("%7B%7D")
    param.value.refresh = (Math.random() * 16)
    param.value.order_by = order_by.value
    param.value.order_by_type = order_by_type.value
    if (props.filters.action) (
        param.value.action = props.filters.action
    )



    getApi("epos_restaurant_2023.www.printview.get_html_and_style", param.value, "").then(result => {
        html.value = result.message.html

    }).catch(err => {

    })
}
onMounted(() => {

    LoadData()
})



</script>