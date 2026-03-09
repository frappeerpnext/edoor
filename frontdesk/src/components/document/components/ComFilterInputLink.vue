<template>

    <ComFilterInput 
        	:option="option"
             @onSearch="onSearch" v-model:operator="operator" v-model:keyword="keyword"
        :operatorOptions="operatorOptions" v-model:listData="listData"
        v-model:selected="selected"
        @onLoadOptionData="onLoadOptionData" 
        @onFilter="onFilter"
        :hasFilter="selected" 
        :optionValue="optionValue">
        {{ $t(option.label) }}
        <template #bottom>
            <Button @click="onClearFilter" :disabled="!selected" :label="$t('Clear Filter')" severity="warning"
                class="w-full mt-4" />
        </template>
    </ComFilterInput>


</template>
<script setup>
import { ref, getData, watch } from "@/plugin"
import ComFilterInput from "@/components/document/components/ComFilterInput.vue"
const props = defineProps({
    option: Object,
    defaultValue: Object,//[key,"operator","value"],
    operator: {
        type: String,
        default: '='
    },
    optionValue: {
        type: String,
        default: "value"

    }
})
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
const emit = defineEmits()
const operator = ref(props.operator)
const keyword = ref("")
const operatorOptions = [
    { label: $t("Equal"), value: '=', },
    { label: $t("Contain"), value: 'like', prefix: '%', sufix: '%' },
    { label: $t("Not Equal"), value: '!=' },
    { label: $t("In"), value: 'in' },
    { label: $t("Not In"), value: 'not in' },
    { label: $t("Is"), value: 'is' },
]
const selected = ref()
const listData = ref([])
watch(() => props.defaultValue, (newVal, oldVal) => {
    if (props.defaultValue) {
        if (newVal) {
            operator.value = newVal[1]
            selected.value = newVal[2];

        }
    } else {
        keyword.value = "";
        selected.value = null
    }
});


function onSearch() {
    
    if (operator.value != 'is') {

        onLoadOptionData()

    } else {
    
        emit("onFilter", [props.option.fieldname, operator.value, selected.value])
    }


}

function onFilter() {
    
    if (!selected.value) {
        emit("onFilter", [props.option.fieldname, operator.value, null])
    } else {
        if (Array.isArray(selected.value)) {
            emit("onFilter", [props.option.fieldname, operator.value, selected.value.map(r => r)])
        } else {
           
            emit("onFilter", [props.option.fieldname, operator.value, selected.value])
        }
    }



}

function onClearFilter() {
    selected.value = null
  
    emit("onFilter", [props.option.fieldname, operator.value, ""])
}

async function onLoadOptionData() {

    if ((typeof props.option.options) == "string") {
        const searchParams = {
            doctype: props.option.options,
            txt: keyword.value,
            limit_page_length: 50,
        };
        const res = await getData("frappe.desk.search.search_link", searchParams, "");
        if (!res.error) {
            listData.value = res.data;
        }
    } else {
        listData.value = props.option.options
    }




}




</script>