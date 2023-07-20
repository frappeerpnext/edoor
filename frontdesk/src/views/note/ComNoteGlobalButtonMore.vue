<template>
    <div> 
        <Button icon="pi pi-ellipsis-v text-lg text-700 more-btn-note" class="w-2rem h-2rem" text rounded aria-label="setting" aria-haspopup="true" aria-controls="manu_btn" @click="toggle" />
        <template v-if="data?.name">
            <Menu ref="show" :id="data?.name.replaceAll(' ', '')" :popup="true" style="min-width: 180px;">
                <template #end>
                    <button @click="onEdit()" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                        <i class="pi pi-pencil me-1"></i>
                        <span class="ml-2">Edit</span>
                    </button>
                </template>
            </Menu>
        </template>
    </div>
</template>
<script setup>
    import {ref} from 'vue'
    const props = defineProps({
        data: Object
    })
    const emit = defineEmits(['onEdit'])
    const show = ref()
    const toggle = (event) => {
        show.value.toggle(event);
    };
    function onEdit(){
        emit('onEdit', props.data.name)
    }
</script>
<style lang="">
    
</style>