<template>
   
    <ComFilterInput :option="option" @onSearch="onSearch" v-model:operator="operator"
        :hasFilter="selected || selectedMultiple || selectedTimespan || startDate || endDate"
        :operatorOptions="operatorOptions">

        <slot>{{ $t(option.label) }}</slot>
       
        <template v-slot:filter-template>
            <template v-if="['=', '>=', '!=', '>', '<', '<='].includes(operator)">

                <Button class="border-none" label="Current Audit Date" @click="onCurrentAuditDate" />
                <Calendar v-model="selected" :selectOtherMonths="true" @date-select="onSearch" :manualInput="false"
                    inline />

                <Button @click="onClearSelection" :disabled="!selected" :label="$t('Clear Filter')" severity="warning"
                    class="w-full mt-2" />

            </template>
            <template v-else-if="['not in', 'in'].includes(operator)">
                <Calendar v-model="selectedMultiple" :selectOtherMonths="true" inline selectionMode="multiple"
                    :manualInput="false" @date-select="onSearchDateMultiple" />

                <Button @click="onClearSelection" :disabled="!selectedMultiple" :label="$t('Clear Filter')" severity="warning"
                    class="w-full mt-2" />

            </template>
            <template v-else-if="operator == 'Between'">
                 <div style="max-width: 250px;">
                <Stack row>
                    <Calendar v-model="startDate" dateFormat="dd-mm-yy" :selectOtherMonths="true" :manualInput="true"
                        :placeholder="$t('Start Date')" />
                    <Calendar v-model="endDate" dateFormat="dd-mm-yy" :selectOtherMonths="true" :manualInput="true"
                        :placeholder="$t('End Date')" />
                </Stack>
                <div  v-if="option?.showYearSelection" class="mt-2">
<strong>Or Select Year</strong>
                
                <div class="flex flex-wrap gap-2 mt-4 mb-4" >
                   
                    <Chip v-for="y in years" :label="y" @click="onSelectYear(y)" style="cursor: pointer;"></Chip>
                    
                </div>
                </div>
                <Stack row>

                    <Button :label="$t('Search')" @click="onSearchBetween" class="w-full border-none"></Button>

                    <Button :label="$t('Clear Filter')" severity="warning" class="w-full border-none" @click="onClearSelection"
                        :disabled="!startDate && !endDate"></Button>



                </Stack>
</div>

            </template>
            <template v-else-if="operator == 'timespan'">
                <Listbox v-model="selectedTimespan" :options="timespanOptions" @change="onSelectTimespan"
                    class="w-full md:w-56">
                    <template #option="slotProps">
                        <span>{{ slotProps.option.label }}</span>
                    </template>
                </Listbox>
                <Button @click="onClearSelection" :disabled="!selectedTimespan" label="Clear Filter" severity="warning"
                    class="w-full" />
            </template>
             
        </template>
    </ComFilterInput>
    
</template>
<script setup>
import { ref, inject, watch } from "@/plugin"
import ComFilterInput from "@/components/document/components/ComFilterInput.vue"
import { computed, onMounted } from "vue"
const props = defineProps({
    option: Object,
    defaultValue: Object//[key,"operator","value"]
})
const moment = inject("$moment")
const startDate = ref()
const endDate = ref()
const emit = defineEmits()
const operator = ref("Between")
const selected = ref()
const selectedTimespan = ref()
const selectedMultiple = ref()
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const years = ref([])
const operatorOptions = [
    { label: $t("Equal"), value: '=', },
    { label: $t("Not Equal"), value: '!=' },
    { label: $t("In"), value: 'in' },
    { label: $t("Not In"), value: 'not in' },
    { label: $t("Is"), value: 'is' },
    { label: ">", value: '>' },
    { label: "<", value: '<' },
    { label: ">=", value: '>=' },
    { label: "<=", value: '<=' },
    { label: $t("Between"), value: 'Between' },
    { label: $t("Timpspan"), value: 'timespan' },
]
const timespanOptions = [
    { "label": $t("Last Week"), "value": "last week" },
    { "label": $t("Last Month"), "value": "last month" },
    { "label": $t("Last Quarter"), "value": "last quarter" },
    { "label": $t("Last 6 Months"), "value": "last 6 months" },
    { "label": $t("Last Year"), "value": "last year" },
    { "label": $t("Yesterday"), "value": "yesterday" },
    { "label": $t("Today"), "value": "today" },
    { "label": $t("Tomorrow"), "value": "tomorrow" },
    { "label": $t("This Week"), "value": "this week" },
    { "label": $t("This Month"), "value": "this month" },
    { "label": $t("This Quarter"), "value": "this quarter" },
    { "label": $t("This Year"), "value": "this year" },
    { "label": $t("Next Week"), "value": "next week" },
    { "label": $t("Next Month"), "value": "next month" },
    { "label": $t("Next Quarter"), "value": "next quarter" },
    { "label": $t("Next 6 Months"), "value": "next 6 months" },
    { "label": $t("Next Year"), "value": "next year" }
]

watch(() => props.defaultValue, (newVal, oldVal) => {
    if (props.defaultValue) {
        if (newVal) {
            operator.value = newVal[1]
            if (operator.value == 'Between') {
                startDate.value = moment(newVal[2][0]).toDate()
                endDate.value = moment(newVal[2][1]).toDate()
            }
            else if (['=', '>=', '!=', '>', '<', '<='].includes(operator.value)) {
                if (newVal[2] == 'current_working_date') {
                    selected.value = moment(window.current_working_date).toDate()
                } else {
                    selected.value = moment(newVal[2]).toDate()
                }

            } else if (['not in', 'in'].includes(operator.value)) {
                if (newVal[2]) {
                    selectedMultiple.value = newVal[2].map(d => moment(d).toDate())
                }
            } else if (operator.value == 'timespan') {
                selectedTimespan.value = newVal[2]
            }
        }
    } else {
        selected.value = null
        selectedMultiple.value = null
        startDate.value = null
        endDate.value = null
        selectedTimespan.value = null
    }

});

const getDisplayLabel = computed(() => {
    if (operator.value == "=" && selected.value) {
        return moment(selected.value).format("DD-MM-YYYY")
    }
    return props.option.label
})

function onSearch() {

    if (selected.value) {
        if (['set', 'not set'].includes(selected.value)) {
            emit("onFilter", [props.option.fieldname, operator.value, selected.value])
        } else {
            emit("onFilter", [props.option.fieldname, operator.value, moment(selected.value).format("YYYY-MM-DD")])
        }

    }
}

function onSelectTimespan() {


    emit("onFilter", [props.option.fieldname, operator.value, selectedTimespan.value.value])

}
function onCurrentAuditDate() {


    emit("onFilter", [props.option.fieldname, operator.value, "current_working_date"])

}



function onSearchBetween() {

    if (startDate.value && endDate.value) {
        if(props.option.maxSelectDate ){
            if(  moment(endDate.value).diff(moment(startDate.value), 'days') > props.option.maxSelectDate)
        {
            app.showWarning("Selection is limited to a maximum range of 366 days. Please choose a date range that does not exceed one year.")
            return
        }
        }
        
        emit("onFilter", [props.option.fieldname, operator.value, [
            moment(startDate.value).format("YYYY-MM-DD"),
            moment(endDate.value).format("YYYY-MM-DD")
        ]])
    }
}

function onSearchDateMultiple() {

    if (selectedMultiple.value) {
        emit("onFilter", [props.option.fieldname, operator.value,
        selectedMultiple.value.map(d => moment(d).format("YYYY-MM-DD"))])
    }
}

function onClearSelection() {
    selected.value = null
    selectedMultiple.value = null
    startDate.value = null
    endDate.value = null
    selectedTimespan.value = null
    emit("onFilter", [props.option.fieldname, operator.value, null])
}

function onSelectYear(y){
    emit("onFilter", [props.option.fieldname, "Between", [
            y+"-01-01",
            y+"-12-31"
        ]])
}


onMounted(async()=>{
    const res =await app.getApi("utils.get_property_year_operation")
    if(res.data){
        years.value = res.data
    }
    
})

</script>