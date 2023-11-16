<template>
 
 
 
        <Timeline :value="events"  class="customized-timeline">
            <template #marker="slotProps">
                <template v-if="slotProps.item.date">
                    <h1 v-if="slotProps.item.date=='Today' || slotProps.item.date=='Yesterday'"><strong>{{ slotProps.item.date }}</strong></h1>
                    <h1 v-else><strong><ComTimeago :date="slotProps.item.date"/></strong></h1>
                </template>
             
                <span v-else class="flex w-2rem h-2rem align-items-center justify-content-center text-red border-circle z-1 shadow-1" :style="{ backgroundColor: slotProps.item.color }">
                    <i :class="slotProps.item.custom_icon"></i>
                </span>
              
            </template>
            <template #content="slotProps" >
                <Card class="mt-3" v-if="!slotProps.item.date">
                    <template #title>
                       {{slotProps.item.subject}}
                    </template>
                    
                    <template #content>
                        <div class="grid">
                            <div class="ms-3">
                                <ComAvatar size="xlarge" :label="slotProps.item.comment_by" :image="slotProps.item.custom_comment_by_photo" />
                                <div>
                                    <span>
                                        {{ slotProps.item.comment_by }}  
                                    </span>
                                </div>
                            </div>
                            <div>
                        {{ slotProps.item.custom_comment_by_photo }} | 
                        {{ slotProps.item.comment_by }} |
                        <div v-html="slotProps.item.content">

                        </div> 
                    </div>
                        {{ slotProps.item.content }}
                    </div>
                    </template>
                </Card>
            </template>
        </Timeline>
 
   
</template>
<script setup>
import {ref, computed,inject} from "@/plugin"
import Timeline from 'primevue/timeline';
import ComAvatar from '@/components/form/ComAvatar.vue';
const working_date = ref(window.current_working_date)
const moment = inject("$moment")
const props = defineProps({
    data:Object
})
const events = computed (()=>{
    if(props.data){ 

    const dates =  [...new Set(props.data.map(r=>r.custom_posting_date))]
    if (dates.length>0){
        let data = []
        dates.forEach(d=>{
            if (d==working_date.value){
                data.push({date:"Today"})
            }
             else if(d==moment(working_date.value).subtract(1, 'days').format('YYYY-MM-DD')){
                data.push({date:"Yesterday"})
               
            }
            else {
                data.push({date:d})

            }
            data = [...data, ...props.data.filter(r=>r.custom_posting_date==d)]

          
  
        })
        return data 
    }
    return []
    }
    return []
})

 


</script>