<template>
    
    <ComFilterInput :option="option" @onSearch="onSearch" v-model:operator="operator"
        :hasFilter="selected || selectedMultiple || selectedTimespan || startDate || endDate"
        :operatorOptions="operatorOptions">

        {{ option.label }}
        <template v-slot:filter-template>
            <template v-if="['=', '>=', '!=', '>', '<', '<='].includes(operator)">

                <Button class="border-none" label="Current Audit Date" @click="onCurrentAuditDate" />
                <Calendar v-model="selected" :selectOtherMonths="true" @date-select="onSearch" :manualInput="false"
                    inline />

                <Button @click="onClearSelection" :disabled="!selected" label="Clear Filter" severity="warning"
                    class="w-full mt-2" />

            </template>
            <template v-else-if="['not in', 'in'].includes(operator)">
                <Calendar v-model="selectedMultiple" :selectOtherMonths="true" inline selectionMode="multiple"
                    :manualInput="false" @date-select="onSearchDateMultiple" />

                <Button @click="onClearSelection" :disabled="!selectedMultiple" label="Clear Filter" severity="warning"
                    class="w-full mt-2" />

            </template>
            <template v-else-if="operator == 'Between'">
                <Stack row>
                    <Calendar v-model="startDate" dateFormat="dd-mm-yy" :selectOtherMonths="true" :manualInput="true"
                        placeholder="Start Date" />
                    <Calendar v-model="endDate" dateFormat="dd-mm-yy" :selectOtherMonths="true" :manualInput="true"
                        placeholder="End Date" />
                </Stack>
                <Stack row>

                    <Button label="Search" @click="onSearchBetween" class="w-full border-none"></Button>

                    <Button label="Clear Filter" severity="warning" class="w-full border-none" @click="onClearSelection"
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
                <Button @click="onClearSelection" :disabled="!selectedTimespan" label="Clear Filter" severity="warning"
                    class="w-full" />
            </template>
        </template>
    </ComFilterInput>
</template>
<script setup>
import { ref, inject, watch } from "@/plugin"
import ComFilterInput from "@/components/document/components/ComFilterInput.vue"
import { computed } from "vue"
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


</script>