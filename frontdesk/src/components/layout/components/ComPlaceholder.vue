<template>
    <div v-if="loading">
        <div class="p-6 text-center" :class="classColor">
            <div><i class="pi pi-spin pi-spinner" style="font-size:60px"></i></div>
            <div class="text-sm italic">Loading...</div>
        </div>
    </div>
    <template v-else>
        <template v-if="isNotEmpty">
            <slot name="default"></slot>
        </template>
        <template v-else>
            <template v-if="isPlaceholder">
                <slot name="empty"></slot>
            </template>
            <div v-else>
                <div class="p-6 text-center" :class="classColor">
                    <div><img :src="iconNoData" style="width: 150px; margin: 0 auto;"></div>
                    <div class="mt-2 text-sm italic">{{ text }}</div>
                </div>
            </div>
        </template>
    </template>
</template>
<script setup>
import iconNoData from '@/assets/svg/icon-no-notic-r-comment.svg'
const props = defineProps({
    isNotEmpty: Boolean,
    isPlaceholder: Boolean,
    icon: {
        type: String,
        default: 'pi-inbox'
    },
    iconSize: {
        type: String,
        default: '60px'
    },
    text: {
        type: String,
        default: 'Data Empty'
    },
    loading: {
        type: Boolean,
        default: false
    },
    classColor: {
        type: String,
        default: 'text-gray-400'
    }
})
</script>
<style lang="">
    
</style>