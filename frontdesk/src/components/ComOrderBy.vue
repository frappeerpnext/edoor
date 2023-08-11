<template>
<div>
    <div class="flex gap-2">
    <ComSelect optionLabel="label" optionValue="fieldname"
      placeholder="Sort By" v-model="data.order_by" :clear="false" @onSelected="onSelectOrderBy"
    :options="sortOptions" />
    
    <Button @click="onOrderTypeClick">
      <i v-if="data.order_type == 'desc'" class="pi pi-sort-numeric-down-alt me-2" /> 
    <i v-if="data.order_type == 'asc'" class="pi pi-sort-numeric-down me-2" />  
    {{data.order_type}}
    </Button>
    </div>
</div>
</template>
<script setup>
import {getApi,ref, onMounted} from "@/plugin"
const loading = ref(false)
const data= ref({order_by:"modified", order_type:"desc"})
const emit = defineEmits(['onOrderBy'])

const props = defineProps({
    doctype:String,
    
})
const state = JSON.parse(localStorage.getItem("page_state_" + props.doctype.toLowerCase().replaceAll(" ","_")))
if(state){
    data.value.order_by = state.order_by
    data.value.order_type = state.order_type
}

const sortOptions = ref([
    {"fieldname":"modified", label:"Last Update On"},
    {"fieldname":"creation", label:"Created On"},
    {"fieldname":"name", label:"ID"}
])

function onSelectOrderBy(d){
    data.value.order_by = d.fieldname
    emit("onOrderBy",data.value)
    


}

function onOrderTypeClick(){
    data.value.order_type = data.value.order_type=="desc"?"asc":"desc"
    emit("onOrderBy",data.value)
     

}
onMounted(()=>{
    loading.value = true
    getApi("frontdesk.get_meta",{doctype:props.doctype}).then((result)=>{
        result.message.fields.filter(x=>x.in_list_view==1  || x.bold==1).forEach(r=>{
            sortOptions.value.push({fieldname:r.fieldname, label:r.label})
        })
        
        
    })
})

</script>