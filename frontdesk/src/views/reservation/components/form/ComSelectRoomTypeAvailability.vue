<template> 
    <Dropdown v-model="roomTypeId" :showClear="showClear" :options="data" showClear optionValue="name" @change="onSelectRoomType($event)" optionLabel="room_type" placeholder="Select Room Type" class="w-full" />
</template>
<script setup>
    import {ref,inject,computed,onMounted,getApi, watch} from '@/plugin'
    const property = JSON.parse(localStorage.getItem("edoor_property"))
    const emit = defineEmits(['update:modelValue', 'onSelected'])
    const props = defineProps({
        modelValue: String,
        startDate: String,
        endDate: String, 
        rateType: {
            type: String,
            default: null
        },
        businessSource: {
            type: String,
            default: null
        },
        showClear:{
            type:Boolean,
            default: false
        }
    })
    const moment = inject('$moment')
    const gv = inject('$gv')
    const data = ref([])
    let roomTypeId = ref('')
    watch(()=> [props.startDate,props.endDate, props.rateType, props.businessSource], ([newStartDate,newEndDate,newRateType,newBusinessSource],[oldStartDate,oldEndDate,oldRateType,oldBusinessSource])=>{
        getRoomType(property.name, newStartDate, newEndDate, newRateType,newBusinessSource)
    })
    const getRoomType = (property, start_date,end_date,rate_type=null, business_source=null) => {
        roomTypeId.value = props.modelValue
        getApi("reservation.check_room_type_availability", {
            property: property,
            start_date: moment(start_date).format("yyyy-MM-DD"),
            end_date: moment(end_date).format("yyyy-MM-DD"),
            rate_type: rate_type,
            business_source: business_source,
            room_type_id: roomTypeId.value
        })
        .then((result) => {
            data.value = result.message;
        }).catch((error) => {
            gv.showErrorMessage(error)
        })
    }
    function onSelectRoomType(p){
        const selected = data.value.find((r)=>r.name == p.value)
        emit('update:modelValue', p.value)
        emit('onSelected', selected)
    } 
   
</script>