<template> 
    <div>   
        <div class="flex items-center justify-end">
            <div class="res_btn_st">
                <Button :class="class" class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded icon="pi pi-ellipsis-v" @click="toggle"></Button>
            </div>
            <Menu ref="show" :popup="true" style="min-width: 180px;">
                <template #end>
                        <button @click="onEdit" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            {{$t("Edit")}}
                        </button> 
                        <button v-if="!data.is_verify" @click="onMarkAsVerify" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            {{$t("Mark as Verify")}}
                        </button> 
                        <button v-else @click="onMarkAsVerify" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            {{$t("Unmark as Verify")}}
                        </button> 
                        <button @click="onDelete" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                            {{$t("Delete")}}
                        </button> 
                        
                </template>
            </Menu>
        </div>
    </div>
    
</template>
<script setup>
import {ref} from '@/plugin'
import { i18n } from '@/i18n';
const { t: $t } = i18n.global;
const show = ref()
const emit = defineEmits(['onEdit', 'onDelete'])
const props = defineProps({
    data:Object
})

const onEdit = () => {
    show.value.hide()
    emit('onEdit')
}

const onDelete = () => {
    show.value.hide()
    emit('onDelete')
}

const onMarkAsVerify = () => {
    show.value.hide()
    emit('onMarkAsVerify')
}


const toggle = (event) => {
    show.value.toggle(event);
};
</script>
<style>
    .res_btn_st button{
        padding: unset !important;
    }
</style>