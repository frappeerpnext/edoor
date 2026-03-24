<template>
    <div class="h-full">
        <ComPanel :titleClass="'text-2xl'" class="sys-date h-17rem md:h-full ">
            <div class="flex justify-content-between align-items-center p-2">
                <div class="line-height-1">
                    <div class="text-6xl">{{ data || 0 }}</div>
                    <p class="font-semibold">{{ title || ''}}</p>
                </div>
                <div class="p-3 rounded-xl" style="background: rgb(169 170 255);">
                    <i :class="icon || 'pi-box'" class="pi text-3xl text-white"></i>
                </div>
            </div>
        </ComPanel>
    </div>
</template>
<script setup>
 const props = defineProps({
    title: String,
    data: Object,
    icon: String
})
</script>