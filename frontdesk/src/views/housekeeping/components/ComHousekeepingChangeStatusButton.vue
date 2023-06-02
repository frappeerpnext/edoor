<template>
    <div> 
        <div class="flex items-center justify-end">
            <Button class="border-noround-right border-y-none border-left-none" :style="{backgroundColor:data.status_color}">
                {{ data.housekeeping_status }}
            </Button>
            <Button class="border-noround-left border-none opacity-80" :style="{backgroundColor:data.status_color}" :aria-controls="data.name.replaceAll(' ', '')" icon="pi pi-angle-down" @click="toggle"></Button>
            <Menu ref="show" :id="data.name.replaceAll(' ', '')" :popup="true" style="min-width: 180px;">
                <template #end>
                    <template v-for="(item, index) in housekeeping_status" :key="index">
                        <button @click="onSelected(data.name, item.status)" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            <span class="ml-2">{{ item.status }}</span>
                        </button>
                    </template>
                </template>
            </Menu>
        </div>
    </div>
</template>
<script setup>
import {ref} from 'vue'
const props = defineProps({
    data: Object
})
const emit = defineEmits('onSelected')
const edoor_setting = JSON.parse(localStorage.getItem('edoor_setting'))
const housekeeping_status = ref(edoor_setting.housekeeping_status)
const options = ref([])
const show = ref()
if(housekeeping_status.value.length > 0){
    housekeeping_status.value.forEach(h => {
        options.value.push({
            label: h.status,
            command: (r) => {
                onSelected(r)
            }
        })
    });
}
const toggle = (event) => {
    show.value.toggle(event);
};
function onSelected(room,status){
    show.value.hide()
    emit('onSelected',room,status)
    

}
</script>
<style lang="">
    
</style>