<template>
    <div>
        <label :for="id" class="block" :class="classLabel" v-if="label">{{ label }}</label>
        <Calendar :id="id" class="w-full" :placeholder="placeholder" v-model="value" :timeOnly="true" dateFormat="HH:mm:ss" @update:modelValue="onUpdated"/>
    </div>
</template>
<script setup>
    import {onMounted,watch , ref, inject} from 'vue'
    const props = defineProps({
        modelValue: [String],
        label:String,
        classLabel:String,
        placeholder:String,
        id: {
            type: String,
            default: 'id_' + String(Math.random()).slice(2)
        }
    })
    const emit = defineEmits(['update:modelValue'])
    const moment = inject('$moment')
    const value = ref()
    onMounted(() => {
        value.value = convertTimeToDatatime(props.modelValue)
        watch(() => props.modelValue, (newValue, oldValue) => {
            if (newValue != null) { 
                value.value = convertTimeToDatatime(newValue)
                
            }
        })
    })
    function onUpdated(datatime){
        var time = moment(datatime).format('HH:mm:ss')
        emit('update:modelValue',time )
    }
    const convertTimeToDatatime = (time) =>{
        var cdt = moment(time, 'HH:mm');
        return cdt.toDate()
    }
</script>
<style lang="">
    
</style>