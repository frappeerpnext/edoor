<template>

    <ComFilterInput :option="option" v-model:operator="operator" :hasFilter="selected"
        :operatorOptions="operatorOptions" v-model:listData="listData" @onLoadOptionData="getParentAccountCode">
       
        {{ option.label }}
        <template v-slot:filter-template>
        
            <InputText ref="searchInput" v-model="keyword" :placeholder="'Search ' + option.label" class="w-full"
                v-debounce="onSearchAccountCode"></InputText>

            <Listbox v-model="selected" v-if="keyword" :options="listData" :optionValue="option.optionValue"
                @change="onSelectOptionChange" 
                
                class="w-full md:w-56 filter_content_custom">
                <template #option="slotProps">
                    <Stack gap="2px">
                        <h1 class="font-bold">{{ slotProps.option.label || slotProps.option.value }}</h1>
                        <p v-if="slotProps.option.description">{{ slotProps.option.description }}</p>
                    </Stack>
                </template>
            </Listbox>

            <Tree v-else v-model:selectionKeys="selected" @nodeSelect="onSelect" selectionMode="single" :value="data"
                class="w-full md:w-30rem" @node-expand="onGetChildren" loadingMode="icon"></Tree>
                <Button @click="onClearSelection" :disabled="!selected" label="Clear Filter" severity="warning"
                class="w-full" />
            </template>
      
    </ComFilterInput>
</template>
<script setup>
import { ref, inject, watch, getDocumentList, getData } from "@/plugin"
import ComFilterInput from "@/components/document/components/ComFilterInput.vue"

import Tree from 'primevue/tree';

import { computed } from "vue"
const props = defineProps({
    option: Object,
    defaultValue: Object//[key,"operator","value"]
})

const emit = defineEmits()
const operator = ref("in")
const selected = ref()
const loading = ref(false)
const keyword = ref("")
const operatorOptions = [
    { label: "Equal", value: 'in', },
    { label: "Not Equal", value: 'not in' }
]
const data = ref([])
const listData = ref([])


watch(() => props.defaultValue, (newVal, oldVal) => {
    if (props.defaultValue) {
        if (newVal) {

        }
    } else {
        selected.value = null

    }

});


async function onSelect(node) {
    const res = await getData("utils.getChildrenOf", {
        doctype: props.option.options,
        parent: node.key,
        include_parent: true
    })
    
        emit("onFilter", [props.option.fieldname, operator.value, res.data])
    
}

async function onSelectOptionChange() {
    if (selected.value) {
        
        const res = await getData("utils.getChildrenOf", {
            doctype: props.option.options,
            parent: selected.value.value,
            include_parent: true
        })

        emit("onFilter", [props.option.fieldname, operator.value, res.data])

    } else {
        // clear filter
        emit("onFilter", [props.option.fieldname, "=", null])
    }

}

async function getParentAccountCode() {
    const res = await getDocumentList(props.option.options, {
        fields: ["name as `key`", "account_name as label", "is_group"],
        filters: [
            ["parent_account_code", '=', 'All Account Code']
        ]
    });
    data.value = res.data;
    data.value.forEach(r => {
        r.leaf = (r.is_group == 0)
    });

}

async function onGetChildren(parent) {

    if (!parent.children) {
        loading.value = true;
        const res = await getDocumentList(props.option.options, {
            fields: ["name as `key`", "account_name as label", "is_group"],
            filters: [
                ["parent_account_code", '=', parent.key],

            ],
            limit: 1000
        });
        parent.children = res.data;
        parent.children.forEach(r => {
            r.leaf = (r.is_group == 0)
        });

        loading.value = false;
    }
}



async function onSearchAccountCode() {
    if (keyword.value) {
        await onLoadOptionData()
    }
}

async function onLoadOptionData() {


    const searchParams = {
        doctype: props.option.options,
        txt: keyword.value,
        limit_page_length: 50,
    };
    const res = await getData("frappe.desk.search.search_link", searchParams, "");
    if (!res.error) {
        listData.value = res.data;
    }



}


function onClearSelection() {
    selected.value = null
    emit("onFilter", [props.option.fieldname, operator.value, null])
}


</script>