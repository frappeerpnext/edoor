<template>
    <div class="w-full flex align-items-center justify-center text-color border-noround">
        <Avatar :size="size" :image="image" :icon="image ? '' : 'pi pi-user'" class="mr-2 bg-gray-300" shape="circle" :style="{borderColor:colorStatus}" />
        <div class="flex flex-column align" style="width:98px;" v-if="$slots.default">
            <slot name="default"></slot>
        </div>
    </div>
</template>
<script setup>
const emit = defineEmits('onClick')
const props = defineProps({
    colorStatus: String,
    image: String,
    size: {
        type: String,
        default: 'large'
    }

})


// function onClick() {
//     emit('onClick')
// }
</script>
<style scoped>
.avatar-guest .p-avatar{
    border: 2px solid ;
}
</style>
 