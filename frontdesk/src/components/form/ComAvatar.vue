<template>
    <div @click="onClick" class="w-full flex align-items-center justify-center text-color border-noround">
        <Avatar :size="size" :image="image" :icon="image ? '' : 'pi pi-user'" class="mr-2 bg-gray-300" shape="circle" />
        <div class="flex flex-column align">
            <slot></slot>
        </div>
    </div>
</template>
<script setup>
const emit = defineEmits('onClick')
const props = defineProps({
    image: String,
    size: {
        type: String,
        default: 'large'
    }
})

function onClick() {
    emit('onClick')
}
</script>
 