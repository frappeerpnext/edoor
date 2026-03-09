<template>
    <div> 
        <div class="flex items-center justify-end">
            <div class="res_btn_st">
                <Button :class="class" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded :aria-controls="data.name.replaceAll(' ', '')" icon="pi pi-ellipsis-v" @click="toggle"></Button>
            </div>
            <Menu ref="show" :id="data.name.replaceAll(' ', '')" :popup="true" style="min-width: 180px;">
                <template #start>
                    <button @click="$emit('onDownload', data)" icon="pi pi-check" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                        {{ $t('Download') }}
                        
                    </button>
                    <button @click="$emit('onEdit',$event, data)" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                       {{ $t('Edit') }} 
                    </button>
                    <button @click="$emit('onDelete', data)" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                       {{ $t('Delete') }} 
                    </button>
                </template>
            </Menu>
        </div> 
    </div>
</template>
<script setup>
import { ref } from 'vue'
import {i18n} from '@/i18n';
const { t: $t } = i18n.global; 
const props = defineProps({
    data: {
        type: Object
    }
})
const emit = defineEmits(['onDownload','onEdit','onDelete'])
const show = ref()
const toggle = (event) => {
    show.value.toggle(event);
};
 
</script>
<style lang="">
    
</style>