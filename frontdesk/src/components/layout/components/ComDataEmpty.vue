<template>
    <div>
        <div v-if="loading != null || loading != false" class="p-6 text-center" :class="classColor" :style="{height: height}" >
            <div><img :src="iconNoData" style="width: 150px; margin: 0 auto;"></div>
            <div class="mt-2 text-sm italic">{{ text }}</div>
        </div>
        <div v-else>
            <div class="p-6 text-center" :class="classColor">
                <div><i class="pi pi-spin pi-spinner" style="font-size:60px"></i></div>
                <div class="text-sm italic">Loading... {{ loading }}</div>
            </div>
        </div>
    </div>
</template>
<script setup>
import iconNoData from '@/assets/svg/icon-no-notic-r-comment.svg'
const props = defineProps({
    isNotEmpty: Boolean,
    isPlaceholder: Boolean,
    loading: {
        type: Boolean,
        default: null
    },
    icon: {
        type: String,
        default: 'pi-inbox'
    },
    text: {
        type: String,
        default: 'Data Empty'
    },
    classColor: {
        type: String,
        default: 'text-gray-400'
    },
    height: {
        type: String,
        default: ''
    }
})
</script>
<style lang="">
    
</style>