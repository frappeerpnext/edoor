<template>
    <div> 
        <div class="flex items-center justify-end">
            <div class="res_btn_st">
                <Button :class="class" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded :aria-controls="data.name.replaceAll(' ', '')" icon="pi pi-ellipsis-v" @click="toggle"></Button>
            </div>
            <Menu ref="show" :model="menus" :id="data.name.replaceAll(' ', '')" :popup="true" style="min-width: 180px;">
                <template #end> 
                        <button class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            No Show
                        </button>
                        <button class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            Cancel
                        </button>
                </template>
            </Menu>
        </div>
    </div>
</template>
<script setup>
import {ref} from 'vue'
const props = defineProps({
    data: Object,
    class: String
})
const emit = defineEmits('onSelected')
const show = ref()
const toggle = (event) => {
    show.value.toggle(event);
};
function onSelected(room,status){
    show.value.hide()
    emit('onSelected',room,status)
}
</script>
<style>
    .res_btn_st button{
        padding: unset !important;
    }
</style>