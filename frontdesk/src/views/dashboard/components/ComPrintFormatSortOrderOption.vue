<template>
 
    <template v-if="doc && doc?.show_sort_order_option && sortOrderFields && sortOrderFields.length>0">
        <div class="grid ps-2 pt-3 pb-3">
            <div class="col-fix">
 <ComSelect  v-model="order_by"  placeholder="Sort Order Field"
                            @onSelected="onSelectFilter" :options='sortOrderFields'  optionLabel="label" optionValue="fieldname"    />
            </div>
            <div class="col-fix">
  <ComSelect class="ml-2" v-model="order_by_type"   placeholder="Sort Order Type"
                            @onSelected="onSelectFilter" :options='["ASC","DESC"]' :clear="false" />               
            </div>
        </div>
          

                           


    </template>

</template>
<script setup>
import { ref, onMounted,  getDoc } from "@/plugin"
    const props = defineProps({
        print_format:String,

    })
const doc = ref({})
const sortOrderFields = ref([])
const order_by = ref("")
const order_by_type = ref("ASC")

const emit = defineEmits(['onSelected'])

function onSelectFilter (){
    emit("onSelected",{order_by:order_by.value, order_by_type:order_by_type.value})
}

onMounted(() => {
   
    getDoc("Print Format",decodeURIComponent(props.print_format)).then((result)=>{
          
        doc.value = result
        
        if(doc.value?.short_order_field==""){
            sortOrderFields.value =  []
        }else {
            sortOrderFields.value =  JSON.parse( doc.value?.short_order_field)
        }
    })
})
</script>