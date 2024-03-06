<template>
    <div :class="class">
        <tippy :content="tooltip || doctype">
        <MultiSelect :class="mClass" display="chip" v-if="isMultipleSelect" :showClear="clear" :style="{ 'min-width': width , 'max-width':maxWidth }" v-model="selected"
            :filter="isFilter" :options="dataOptions" :optionLabel="option.label" :optionValue="option.value"
            @update:modelValue="onUpdate" :placeholder="$t(placeholder ?? '')" :maxSelectedLabels="maxSelectedLabels"/>

            <Dropdown 
            class="w-full" v-else 
            :showClear="clear" 
            :style="{ 'min-width': width , 'max-width':maxWidth }"
            v-model="selected" :filter="isFilter"
            :options="dataOptions" 
            :optionLabel="option.label" 
            :optionValue="option.value" 
            @update:modelValue="onUpdate"
            :placeholder="$t(placeholder ?? '')"
        >
        </Dropdown>
       
    </tippy>
    </div>
</template>
<script setup>
import { useToast, ref, inject, reactive, computed, watch, onMounted,getDocList } from '@/plugin'
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const emit = defineEmits(['update:modelValue', 'onSelected', 'onSelectedValue'])
const props = defineProps({
    doctype: String,
    placeholder: String,
    modelValue: [String, Number, Array],
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
        default: '100%'
    },
    maxWidth: {
        type: String,
        default: '100%'
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
    },
    isMultipleSelect: {
        type: Boolean,
        default: false
    },
    default: {
        type: Boolean,
        default: false
    }, 
    class: String,
    tooltip:String,
    maxSelectedLabels: {
        type: Number,
        default: 3
    },
    mClass: String
})
const toast = useToast();
const frappe = inject('$frappe')
const db = frappe.db();
const call = frappe.call();
const data = ref([])
let dataOptions = ref([])
let selected = computed({
    get() {
        return props.modelValue || null
    },
    set(newValue) {
        return newValue
    }
})

onMounted(() => {
    
    watch(() => props.groupFilterValue, (newValue, oldValue) => {
        if (newValue != null) {
            if (props.isMultipleSelect && Array.isArray(newValue)) {
                dataOptions.value = []
                newValue.forEach(n => {
                    dataOptions.value = dataOptions.value.concat(data.value.filter(r => r[props.groupFilterField] == n))
                })

            }
            else {
                dataOptions.value = data.value.filter(r => r[props.groupFilterField] == newValue)
            }

        } else {
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
        data.value = result.message
        dataOptions.value = data.value
        if (props.default && data.value && data.value.length > 0) {

            selected.value = data.value[0]
         
        }

    })
        .catch((error) => {
            
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
    getDocList(props.doctype, { filters: props.filters, fields: fields, limit: 1000 }).then((r) => {
        data.value = r
        dataOptions.value = data.value
        if (props.default && data.value && data.value.length > 0) {

            selected.value = data.value[0]
           
        }

    }).catch((error) => {
        
        data.value = []
    });
}
function onUpdate(r) {
    let result = null
    if (props.isMultipleSelect) {
        result = []
        if (r.length > 0) {
            r.forEach(n => {
                result = result.concat(data.value.find(r => r[option.value] == n))
            })
        } else {
            result = data.value.find(d => d[option.value] == r)
        }

    } else {
        result = data.value.find(d => d[option.value] == r)
    }
    emit('update:modelValue', r)
    emit('onSelectedValue', result)
    emit('onSelected', r)
    
}

</script> 
