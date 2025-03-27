<template>

    <ComFilterInput :option="option" @onSearch="onSearch" v-model:operator="operator" v-model:keyword="selected"
        :operatorOptions="operatorOptions">
        {{ option.label }}

        <template v-slot:filter-template>
            <template v-if="['=', '>=', '!=', '>', '<', '<='].includes(operator)">
                <Calendar v-model="selected" :selectOtherMonths="true" @date-select="onSearch" :manualInput="false"
                    inline />
            </template>
            <template v-else-if="['not in', 'in'].includes(operator)">
                <Calendar v-model="selectedMultiple" :selectOtherMonths="true" inline selectionMode="multiple"
                    :manualInput="false" @date-select="onSearchDateMultiple" />
                <Button :disabled="!selectedMultiple" label="Clear Selection" @click="onClearSelection"></Button>
            </template>
            <template v-else-if="operator == 'Between'">
                <Stack row>
                    <Calendar v-model="startDate" dateFormat="dd-mm-yy" :selectOtherMonths="true" :manualInput="true"
                        placeholder="Start Date" />
                    <Calendar v-model="endDate" dateFormat="dd-mm-yy" :selectOtherMonths="true" :manualInput="true"
                        placeholder="End Date" />
                </Stack>
                <Stack row>
                    
                        <Button label="Search" @click="onSearchBetween" class="w-full"></Button>
                        
                        <Button label="Clear Filter" class="w-full" @click="onClearSelection"
                            :disabled="!startDate && !endDate"></Button>
                        


                </Stack>


            </template>
            <template v-else-if="operator == 'timespan'">
                <Listbox v-model="selectedTimespan" :options="timespanOptions" @change="onSelectTimespan"
                    class="w-full md:w-56">
                    <template #option="slotProps">
                        <span>{{ slotProps.option.label }}</span>
                    </template>
                </Listbox>
            </template>
        </template>
    </ComFilterInput>
</template>
<script setup>
import { ref, inject } from "@/plugin"
import ComFilterInput from "@/components/document/components/ComFilterInput.vue"
const props = defineProps({
    option: Object
})
const moment = inject("$moment")
const startDate = ref()
const endDate = ref()
const emit = defineEmits()
const operator = ref("Between")
const selected = ref()
const selectedTimespan = ref()
const selectedMultiple = ref()

const operatorOptions = [
    { label: "Equal", value: '=', },
    { label: "Not Equal", value: '!=' },
    { label: "In", value: 'in' },
    { label: "Not In", value: 'not in' },
    { label: "Is", value: 'is' },
    { label: ">", value: '>' },
    { label: "<", value: '<' },
    { label: ">=", value: '>=' },
    { label: "<=", value: '<=' },
    { label: "Between", value: 'Between' },
    { label: "Timpspan", value: 'timespan' },
]
const timespanOptions = [
    { "label": "Last Week", "value": "last week" },
    { "label": "Last Month", "value": "last month" },
    { "label": "Last Quarter", "value": "last quarter" },
    { "label": "Last 6 Months", "value": "last 6 months" },
    { "label": "Last Year", "value": "last year" },
    { "label": "Yesterday", "value": "yesterday" },
    { "label": "Today", "value": "today" },
    { "label": "Tomorrow", "value": "tomorrow" },
    { "label": "This Week", "value": "this week" },
    { "label": "This Month", "value": "this month" },
    { "label": "This Quarter", "value": "this quarter" },
    { "label": "This Year", "value": "this year" },
    { "label": "Next Week", "value": "next week" },
    { "label": "Next Month", "value": "next month" },
    { "label": "Next Quarter", "value": "next quarter" },
    { "label": "Next 6 Months", "value": "next 6 months" },
    { "label": "Next Year", "value": "next year" }
]


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

function onSearchBetween() {
    if (startDate.value && endDate.value) {
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
    selectedMultiple.value = []
    startDate.value = null
    endDate.value = null
    emit("onFilter", [props.option.fieldname, operator.value, null])
}


</script>