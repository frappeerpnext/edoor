<template>
    <Dropdown v-model="roomId" :options="options" optionValue="name" @change="onSelect($event)" optionLabel="room_number" placeholder="Select Room" class="w-full" />
</template>
<script setup>
    import {ref,inject,computed,onMounted,getApi, watch} from '@/plugin'
    const property = JSON.parse(localStorage.getItem("edoor_property"))
    const emit = defineEmits(['update:modelValue', 'onSelected'])
    const props = defineProps({
        modelValue: String,
        startDate: String,
        endDate: String,
        roomType:String,
        except:String
    })
    const moment = inject('$moment')
    const gv = inject('$gv')
    const data = ref([])
    const options = computed(()=>{
        if(props.roomType){
            if(props.except){
                data.value = data.value.filter((r)=>r.name != props.except)
            }
            return data.value.filter((r)=>r.room_type_id == props.roomType) 
        }
        return []
    })
    let roomId = ref(props.modelValue)
    watch(()=> [props.startDate,props.endDate], ([newStartDate,newEndDate],[oldStartDate,oldEndDate])=>{
        if(newStartDate != oldStartDate || newEndDate != oldEndDate)
            getRoom(newStartDate, newEndDate)
    })
    const getRoom = (start_date,end_date) => { 
        getApi("reservation.check_room_availability", {
            property: property.name,
            start_date: moment(start_date).format("yyyy-MM-DD"),
            end_date: moment(end_date).format("yyyy-MM-DD")
        })
        .then((result) => { 
            data.value = result.message; 
        })
    }
    function onSelect(p){
        const selected = data.value.find((r)=>r.name == p.value)
        emit('update:modelValue', p.value)
        emit('onSelected', selected)
    } 
</script>
