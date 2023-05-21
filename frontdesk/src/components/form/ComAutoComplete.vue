<template>
    <div>
        <AutoComplete
                :data-value="value"
                v-model="selected" 
                completeOnFocus
                :suggestions="options"
                optionLabel="label"
                @complete="search"
                @item-select="onSelected"
                @clear="onClear"
                @blur="onBlur"
                @focus="onFocus"
                :placeholder="placeholder">
                <template #option="slotProps">
                    <template v-if="slotProps.option.description == addNewKey || slotProps.option.description == AdvancedSearchKey">
                        <div v-if="slotProps.option.description == addNewKey">
                            <div class="font-bold text-blue-600"><i class="pi pi-plus"></i> {{ addNewTitle || 'Add New' }}</div>
                        </div>
                        <div v-if="slotProps.option.description == AdvancedSearchKey">
                            <div class="font-bold text-blue-600"><i class="pi pi-search"></i> Advanced Search</div>
                        </div>
                    </template>
                    <div v-else>
                        <div v-if="slotProps.option.label">
                            <div class="font-bold">{{ slotProps.option.label }}</div>
                            <div class="text-sm" style="max-width: 250px; white-space: pre-line;" v-if="slotProps.option.description">{{ slotProps.option.description }}</div>
                        </div>
                    </div>
                </template> 
        </AutoComplete> 
    </div>
</template>
<script setup>
import {ref, inject, computed,useToast,useDialog} from '@/plugin'
import Search from './ComAdvancedSearch.vue';
const props = defineProps({
    doctype:String,
    modelValue: [String, Number],
    filters: [Object, String],
    isAddNew: {
        type: Boolean,
        default: false
    },
    isAdvancedSearch: {
        type: Boolean,
        default: false
    },
    placeholder: String,
    addNewTitle: String
}) 
let value = computed({
    get(){  
        if(props.modelValue){
            call.get('frappe.desk.search.get_link_title',{doctype:props.doctype,docname: props.modelValue}).then((result) => {
                selected.value = result.message || props.modelValue
                return props.modelValue
            })
        }else{
            selected.value = ''
            return ''
        }
        
    },
    set(newValue){
        call.get('frappe.desk.search.get_link_title',{doctype:props.doctype,docname: newValue}).then((result) => {
            selected.value = result.message || ''
        })
        return newValue
    }
})
const emit = defineEmits(['update:modelValue', 'onAddNew','onSelected'])
const frappe = inject('$frappe')
const call = frappe.call();
const options = ref([])
const addNewKey = '#add#new'
const AdvancedSearchKey = '#advanced#search'
const keyword = ref('')
let selected = ref('')
const toast = useToast()

const dialog = useDialog();
 
const search = (event) => {
    keyword.value = event.query
    if (!event.query.trim().length) {
        getData('')
    } else {
        getData(event.query)
    } 
        
}
const onSelected = (event) => {
    if(event.value.description == addNewKey){
        //selected.value = ''
        //console.log(keyword.value)
        // alert(keyword.value)
    }
    if(event.value.description == AdvancedSearchKey){
        selected.value = ''
        onAdvancedSearch()
    }
    else{
        value.value = event.value.value
        emit('onSelected', event.value)
        emit('update:modelValue', event.value.value)
    }
    
}
async function getData(keyword){
    let apiParams = {doctype:props.doctype,txt: keyword}
    if(props.filters){
        apiParams.filters = JSON.parse(JSON.stringify(props.filters))
    }
    await call.get('frappe.desk.search.search_link',apiParams).then((result) => {
            options.value = result.results
            options.value = options.value.map(r=>r.label == '' || r.label == null ? {...r, label: r.value}: r)
            if(props.isAddNew){
                options.value.push({
                    "value": "",
                    "label": "New",
                    "description": addNewKey
                })
            }
            if(props.isAdvancedSearch){
                options.value.push({
                    "value": "",
                    "label": "Advanced Search",
                    "description": AdvancedSearchKey
                })
            }
            return options.value
        })
        .catch((error) => {
            toast.add({ severity: 'error', summary: error.httpStatusText, detail: error.message, life: 3000 });
            return []
        });
}
function onClear(){
    getData('')
    emit('onSelected', {})
    emit('update:modelValue', '')
}

function getLinkTitle(name){
    call.get('frappe.desk.search.get_link_title',{doctype:props.doctype,docname: name}).then((result) => {
        selected.value = result.message || ''
        return selected.value
    })
    .catch((error) => {
        toast.add({ severity: 'error', summary: error.httpStatusText, detail: error.message, life: 3000 });
    });
}
function onBlur(){
    if(!selected.value.value || (selected.value.value && (selected.value.value != props.modelValue))){
        //selected.value = '';
    }
}
function onFocus(){
    if(options.value.length == 0){
        getData('')
    }
    
}

function onAdvancedSearch() {
    dialog.open(Search, {
        props: {
            header: 'Select ' + props.doctype,
            keyword: keyword.value,
            doctype: props.doctype,
            style: {
                width: '50vw',
            },
            breakpoints: {
                '960px': '75vw',
                '640px': '90vw'
            },
            modal: true
        },
        onClose(options) {
            value.value = (options.data)
            console.log(value)
            emit('onSelected', {
                "value": options.data,
                "label": value.value,
                "description": ''
            }) 
            emit('update:modelValue', options.data)
        }
    });
}

</script>
<style lang="">
    
</style>