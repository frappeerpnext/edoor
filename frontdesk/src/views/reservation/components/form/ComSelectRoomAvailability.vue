<template> 
    <Dropdown v-model="roomId" :showClear="showClear" filter :options="options" optionValue="name" @change="onSelect($event)" optionLabel="room_number" placeholder="Select Room" class="w-full" />
</template>
<script setup>
    import {ref,inject,computed,getApi, watch} from '@/plugin'
    const property = JSON.parse(localStorage.getItem("edoor_property"))
    const emit = defineEmits(['update:modelValue', 'onSelected'])
    const props = defineProps({
        modelValue: String,
        startDate: String,
        endDate: String,
        roomType:String,
        except:String,
        exceptField:{
            type: String,
            default: ''
        },
        exceptValue:{
            type: String,
            default: ''
        },
        showClear:{
            type:Boolean,
            default: false
        }
    })
    const isWatchWork = ref(false)
    const moment = inject('$moment')
    const gv = inject('$gv')
    const data = ref([])
    let roomId = ref(props.modelValue)
    const options = computed(()=>{
        const tempData = ref(data.value)
        if(props.roomType){
            if(props.except){
                const excepts = props.except.split(',')
                if(excepts.length > 0){
                    excepts.forEach((ex)=>{
                        tempData.value = tempData.value.filter((r)=>r.name != ex || r.name == roomId.value)
                    })
                    
                }
            }
            
            return tempData.value.filter((r)=>r.room_type_id == props.roomType) 
        }
        return []
    })
 
    watch(()=> [props.roomType], ([newValue],[oldValue])=>{
        if(oldValue != undefined && newValue != oldValue){
            roomId.value = null
            emit('update:modelValue', null)
            emit('onSelected', {})
        }
           
    })
    watch(()=> [props.startDate,props.endDate], ([newStartDate,newEndDate],[oldStartDate,oldEndDate])=>{
        if(newStartDate != oldStartDate || newEndDate != oldEndDate){
            isWatchWork.value = true
            getRoom(newStartDate, newEndDate)
        }
           
    })
    const getRoom = (start_date,end_date) => { 
        const filter = ref({
            property: property.name,
            start_date: moment(start_date).format("yyyy-MM-DD"),
            end_date: moment(end_date).format("yyyy-MM-DD")
        })
        if(props.exceptField && props.exceptValue){
           filter.value.exception = {
                field: props.exceptField,
                value: props.exceptValue
            } 
        }
       
        getApi("reservation.check_room_availability", filter.value)
        .then((result) => { 
           
            data.value = result.message; 
        })
    }
    if(!isWatchWork.value && props.startDate && props.endDate){
        getRoom(property.name, props.startDate, props.endDate, props.rateType,props.businessSource)
    }
    function onSelect(p){
        const selected = data.value.find((r)=>r.name == p.value)
        emit('update:modelValue', p.value)
        emit('onSelected', selected)
    } 
</script>
