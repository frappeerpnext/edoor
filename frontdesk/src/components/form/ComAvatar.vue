<template> 
    <div class="w-full flex align-items-center text-color border-noround" :class="align">
        <Avatar v-if="!fileName" :size="size" :image="image" :icon="image ? '' : 'pi pi-user'" class="mr-2 bg-gray-300" shape="circle" :style="{borderColor:colorStatus}" />
        <template v-else>
            <Avatar v-if="icon" :size="size" :icon="icon" class="mr-2 !bg-transparent" shape="circle" :style="{borderColor:colorStatus}" />
            <Avatar v-else :size="size" :image="image" class="mr-2 bg-gray-300" shape="circle" :style="{borderColor:colorStatus}" />
        </template>
        <div class="flex flex-column align" v-if="$slots.default">
            <slot name="default"></slot>
        </div>
    </div>
</template>
<script setup>
import {computed,ref,onMounted} from 'vue'
const emit = defineEmits('onClick')
const props = defineProps({
    colorStatus: String,
    image: String,
    size: {
        type: String,
        default: 'large'
    },
    fileName: {
        type: String,
        default: '' 
    },
    align:{
        type: String,
        default: 'justify-center'
        
    }
})
const icon = ref()
const extension = ref('')
onMounted(() => {
    if(props.fileName){
        extension.value = props.fileName.substring(props.fileName.lastIndexOf(".") + 1);
        console.log(extension.value)
        if(extension.value == 'pdf'){
            icon.value = 'pi pi-file-pdf'
        }else if(extension.value == 'doc' || extension.value == 'docx'){
            icon.value = 'pi pi-file-word'
        }
        else if(extension.value == 'xlsx' || extension.value == 'xls'){
            icon.value = 'pi pi-file-excel'
        }
    }
})
</script>
<style scoped>
.avatar-guest .p-avatar{
    border: 2px solid ;
}
</style>
 