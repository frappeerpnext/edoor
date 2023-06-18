<template>
    <Dropdown v-model="roomTypeId" :options="data" optionValue="name" @change="onSelectRoomType($event)" optionLabel="room_type" placeholder="Select Room Type" class="w-full" />
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
        }
    })
    const moment = inject('$moment')
    const gv = inject('$gv')
    const data = ref([])
    let roomTypeId = ref(props.modelValue)
    watch(()=> [props.startDate,props.endDate, props.rateType, props.businessSource], ([newStartDate,newEndDate,newRateType,newBusinessSource],[oldStartDate,oldEndDate,oldRateType,oldBusinessSource])=>{
        console.log(newEndDate)
        console.log(newRateType)
        console.log(newBusinessSource)
        getRoomType(property.name, newStartDate, newEndDate, newRateType,newBusinessSource)
    })
    // watch(()=> props.startDate, (newValue, oldValue)=>{
        
    //     if (oldValue !== undefined && newValue !== oldValue){
    //         console.log(1)
    //         getRoomType(property.name, newValue, props.endDate, props.rateType, props.businessSource)
    //     }
    // })
    // watch(()=> props.endDate, (newValue, oldValue)=>{ 
        
    //     if (oldValue !== undefined && newValue !== oldValue){
    //         console.log(2)
    //         getRoomType(property.name, props.startDate, newValue, props.rateType, props.businessSource)
    //     }
    // })
    // watch(()=> props.rateType, (newValue, oldValue)=>{ 
    //     if (oldValue !== undefined && newValue !== oldValue){
    //         console.log(3)
    //         getRoomType(property.name, props.startDate, props.endDate, newValue, props.businessSource)
    //     }
    // })
    // watch(()=> props.businessSource, (newValue, oldValue)=>{
        
    //     if (oldValue !== undefined && newValue !== oldValue){
    //         console.log('new 4',newValue)
    //         console.log('old 4',oldValue)
    //         getRoomType(property.name, props.startDate, props.endDate, props.rateType, newValue)
    //     }
    // })
    const getRoomType = (property, start_date,end_date,rate_type=null, business_source=null) => {
        getApi("reservation.check_room_type_availability", {
            property: property,
            start_date: moment(start_date).format("yyyy-MM-DD"),
            end_date: moment(end_date).format("yyyy-MM-DD"),
            rate_type: rate_type,
            business_source: business_source
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
    // onMounted(()=>{
    //     getRoomType(property.name, props.startDate, props.endDate, props.rateType, props.businessSource)
    // })
</script>