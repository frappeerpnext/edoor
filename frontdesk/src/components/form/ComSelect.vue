<template> 
    <Dropdown :showClear="clear" :style="{ 'min-width': width }"
        v-model="selected" :filter="isFilter" :options="dataOptions" :optionLabel="option.label" :optionValue="option.value"
        @update:modelValue="onUpdate" :placeholder="placeholder" />
</template>
<script setup>
import { useToast, ref, inject, reactive, computed, watch,onMounted } from '@/plugin'
const emit = defineEmits(['update:modelValue', 'onSelected', 'onSelectedValue'])
const props = defineProps({
    doctype: String,
    placeholder: String,
    modelValue: [String, Number],

    optionLabel: {
        type: String,
        default: ''
    },
    optionValue: {
        type: String,
        default: ''
    },
    filters: {
        type: [String, Object],
        default: {}
    },
    isFilter: {
        type: Boolean,
        default: false
    },
    options: Array,
    extraFields: {
        type: [String, Array],
        default: []
    },
    width: {
        type: String,
        default: '140px'
    },
    clear: {
        type: Boolean,
        default: true
    },
    groupFilterField: {
        type: String,
        default: ''
    },
    groupFilterValue: {
        type: [String, Number, Boolean],
        default: null
    }
})
const toast = useToast();
const frappe = inject('$frappe')
const db = frappe.db();
const call = frappe.call();
const data = ref([])
let dataOptions = ref([])
let selected = computed({
    get() {
        return props.modelValue
    },
    set(newValue) {
        return newValue
    }
})
 
onMounted(() => {
    watch(()=>props.groupFilterValue,(newValue, oldValue)=>{
        if(newValue != null){
            dataOptions.value = data.value.filter(r => r[props.groupFilterField] == newValue)
        }else{
            dataOptions.value = data.value
        }
        onUpdate('')
    })
})


let option = reactive({
    label: 'value',
    value: 'value'
})
// check custom field
let customs = props.extraFields
if (typeof customs == 'string') {
    customs = props.extraFields.split(",")
}
if (props.doctype) {
    
    if (props.optionLabel == '' && props.optionValue == '' && props.groupFilterField == '' && customs.length == 0) {
        onSearchLink()
    }
    else {
        
        onDocList()
    }
} else {
    data.value = props.options
    option.label = props.optionLabel
    option.value = props.optionValue
    dataOptions.value = data.value
}

function onSearchLink() {
    let apiParams = { doctype: props.doctype, txt: '', page_length: 1000 }
    if (props.filters) {
        apiParams.filters = JSON.parse(JSON.stringify(props.filters))
    }
    call.get('frappe.desk.search.search_link', apiParams).then((result) => {
        data.value = result.results
        dataOptions.value = data.value
    })
        .catch((error) => {
            toast.add({ severity: 'error', summary: error.httpStatusText, detail: error.message, life: 3000 });
            return []
        });
}
function onDocList() {
    let fields = []
    option.label = props.optionLabel
    option.value = props.optionValue
    if (props.optionLabel != props.optionValue) {
        fields.push(props.optionLabel, props.optionValue)
    }
    if (customs.length > 0) {
        customs.forEach(r => {
            fields.push(r)
        })
    }
    if (props.groupFilterField) {
        fields.push(props.groupFilterField)
    }
    db.getDocList(props.doctype, { filters: props.filters, fields: fields, limit: 1000 }).then((r) => {
        data.value = r
        dataOptions.value = data.value
    }).catch((error) => {
        toast.add({ severity: 'error', summary: error.httpStatusText, detail: error.message, life: 3000 });
        data.value = []
    });
}
function onUpdate(r) {
    const obj = data.value.find(d => d[option.value] == r)
    console.log(r)
    emit('onSelectedValue', r)
    emit('onSelected', obj)
    emit('update:modelValue', r)
}

</script>