<template>
    <Button  :class="'content_btn_b adjBtnRefresh block text-left w-13rem ' + (currentRoute==routeName?'active bg-primary':'')" @click="onOpenRoute">
        <div class="text-4xl">{{dataLength}}</div>
        <div>{{$t(title)}}</div>
    </Button>
</template>
<script setup>
    const props = defineProps({
        routeName: String,
        dataLength: String,
        title: String,
        currentRoute: String
    })
    const emit = defineEmits(['onOpenRoute'])

    const onOpenRoute = () => {
        emit('onOpenRoute')
    }
</script>