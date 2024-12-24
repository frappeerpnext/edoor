<template>
    <Button  :class="class" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded :aria-controls="data.name.replaceAll(' ', '')" icon="pi pi-ellipsis-v" @click="toggle"></Button>
    <Menu ref="show" :model="menus" :id="data.name.replaceAll(' ', '')" :popup="true" style="min-width: 180px;">
        <template #end>
                <button @click="onChangeStay(data)"  class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                    {{ $t('Change Stay') }}
                    
                </button> 
                <button  v-if="data?.room_id"  @click="onUnassignRoom(data)" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                    {{ $t('Unassign room') }} 
                </button>
                <button @click="onOpenDeleted(data)" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                    {{ $t('Delete') }}
                    
                </button>
                
        </template>
    </Menu>
</template>
<script setup>
import { ref } from '@/plugin';
const props = defineProps({
    data:Object
})
const show = ref()
const toggle = (event) => {
    show.value.toggle(event);
};
</script>