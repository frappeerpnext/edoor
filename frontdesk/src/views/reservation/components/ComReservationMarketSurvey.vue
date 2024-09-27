<template>

<BlockUI :blocked="loading">
    <div class="card">
        <Fieldset  v-for="(s, index) in formModel.filter(item => !item.hidden)" :key="index" :legend="s.label" :toggleable="true" >
            <div class="grid">
               <div class="col-fixed mx-2" v-for="(c, col_index) in s.columns" :key="col_index">
            <div class="field" v-for="(f, f_index) in c.fields" :key="f_index" >
                    <ComFormInput v-if="!f?.hidden" :field="f" :model="doc"  />  
            </div>
        </div> 
            </div>
            
        </Fieldset>
    </div>
</BlockUI>    
  <hr class="my-3" />
  
  <div v-if="!hideSave" class="flex justify-content-end mb-3">
<Button type="button" label="Save" icon="pi pi-save" :loading="loading" @click="onSave" />
  </div>
  
</template>
<script setup>
import BlockUI from 'primevue/blockui';
    import {getApi,ref,onMounted,createUpdateDoc} from "@/plugin"
    import ComFormInput  from "@/components/form/ComFormInput.vue"
    const props = defineProps({
        reservation:String,
        hideSave:{
            default:false,
            type:Boolean
        }
    })
    const doc = ref({reservation:props.reservation})
    const meta = ref()
    const formModel = ref([])
    const loading = ref(false)

    function getMeta(){
        getApi("api.get_meta",{doctype:"Reservation Market Survey"},"epos_restaurant_2023.api.").then(result=>{
            meta.value= result.message
            formModel.value = meta.value.fields.filter(r=>r.fieldtype =='Section Break')
            formModel.value.forEach((s,index)=>{
                
                s.columns = getColumnsBySectionBreak(s,index)
                
                

                s.columns.forEach(c =>{
                    c.fields = getFields(c)
                })

            })
        })
    }

    
    function getColumnsBySectionBreak(section, index){
        const start_index = section.idx
        let end_index =1000
        if (index<formModel.value.length-1) {
            end_index = formModel.value[index+1].idx
        }

       let columns = []
        let totalColumns = meta.value.fields.filter(r=>r.idx>start_index && r.idx < end_index && r.fieldtype =='Column Break')
        
        if (totalColumns.length>0){
            totalColumns.forEach((c,index)=>{
                const column = {start_index:c.idx}
                column.end_index = getColumnEndIndex(totalColumns, index,end_index)
                columns.push(column)
                
            })

            // ADD FIRST COLUMN
            columns.unshift({
                    start_index: section.idx,
                    end_index: columns[0].start_index
                })
        }else {
            columns.push({start_index:start_index, end_index: end_index})
        }

       return columns

    }

    
    function getColumnEndIndex(columns,index,section_end_index){

        let end_index = 0
        if (index<columns.length-1){
            end_index = columns[index+1].idx
        }else {
            end_index = section_end_index
        }
        return end_index
    }

    function getFields(column){
        const fields =   meta.value.fields.filter(r=>r.idx>column.start_index && r.idx<column.end_index)
        
        return fields
    }

    function onSave(){
        loading.value = true
        createUpdateDoc("Reservation Market Survey",doc.value).then(new_doc=>{
            doc.value = new_doc
            loading.value = false
        }).catch(err=>{
            loading.value = false
        })
    }

    function getMarketSurveyDoc(){
        getApi("reservation_market_survey.get_doc", {reservation:props.reservation} ,"edoor.edoor.doctype.reservation_market_survey.").then(result=>{
            doc.value = result.message
        })
    }
    onMounted(()=>{
        getMeta()
        getMarketSurveyDoc()

    })
</script>