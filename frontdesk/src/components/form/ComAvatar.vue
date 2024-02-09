<template>
    <div class="w-full flex align-items-center text-color border-noround" :class="align">
        <div class="flex" :class="{'cursor-pointer':isDisplayImage}" @click="onShowImage" v-if="!fileName">
            <template v-if="image">
                <Avatar v-if="isMobile" :size="size" :image="image" :icon="image ? '' : 'pi pi-user'" class="bg-gray-300 border-circle" shape="circle" :style="{borderColor:colorStatus}" />
                <Avatar v-else :size="size" :image="image" :icon="image ? '' : 'pi pi-user'" class="mr-2 bg-gray-300 border-circle" shape="circle" :style="{borderColor:colorStatus}" />
            </template>
            <Avatar v-else-if="label" :size="size" class="mr-2 bg-gray-300 border-circle" shape="circle" :label="getAbbreviation()"/>
            <div v-else class="mr-3 bg-gray-300 border-circle p-1 border-2" :style="{borderColor:colorStatus}">
                <ComIcon  icon="userProfile" ></ComIcon>
            </div>
        </div>
        <template v-else>
            <Avatar v-if="icon" :size="size" :icon="icon" class="mr-2 !bg-transparent" shape="circle" :style="{borderColor:colorStatus}" />
            <div :class="{'cursor-pointer':isDisplayImage}"  @click="onShowImage" v-else>
                <Avatar :size="size" :image="image" class="mr-2 bg-gray-300" shape="circle" :style="{borderColor:colorStatus}" />
            </div>
        </template>
        <div class="flex flex-column align" v-if="$slots.default">
            <slot name="default"></slot>
        </div>
    </div>
    <Galleria v-model:visible="display" :value="displayImages"  :showThumbnailNavigators="false" :numVisible="1" containerStyle="max-width: 50%" :circular="true" :fullScreen="true" :showItemNavigators="false"  :showThumbnails="false">
        <template #item="slotProps">
            <img :src="slotProps.item.image" :alt="slotProps.item.alt" style="width: 100%; display: block" />
        </template>
    </Galleria>
</template>
<script setup>
import {ref,onMounted} from 'vue'
import Galleria from 'primevue/galleria';
 
const isMobile = ref(window.isMobile)
const emit = defineEmits('onClick')
const props = defineProps({
    colorStatus: String,
    image: String,
    label:String,
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
        
    },
    isDisplayImage:{
        type: Boolean,
        default: false
    }
})
const icon = ref()
const display = ref(false)
const displayImages = ref([])
const extension = ref('')
function onShowImage(){
    if(props.isDisplayImage){
        display.value = true
    }
}

function getAbbreviation(){
    if (props.label){
        const words = props.label.split(" ")
        let label = words[0][0]
        if (words.length>1){
            label = label + words[1][0]
        }
        return label
    }
    return ""
}

onMounted(() => {
    if(props.fileName){
        extension.value = props.fileName.substring(props.fileName.lastIndexOf(".") + 1);

        if(extension.value == 'pdf'){
            icon.value = 'pi pi-file-pdf'
        }else if(extension.value == 'doc' || extension.value == 'docx'){
            icon.value = 'pi pi-file-word'
        }
        else if(extension.value == 'xlsx' || extension.value == 'xls'){
            icon.value = 'pi pi-file-excel'
        }
    }
    if(props.isDisplayImage){
        displayImages.value.push({image: props.image,alt: props.fileName})
    }
})
</script>
<style scoped>
.avatar-guest .p-avatar{
    border: 2px solid ;
}
</style>
 