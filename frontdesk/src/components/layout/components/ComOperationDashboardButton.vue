<template>
 
    <Button  :class="'op_menu block text-left w-13rem ' + (currentRoute==routeName?'op_active_menu':'')" @click="onOpenRoute">
        <div class="flex justify-content-between">
            <div>
                <ComIcon :icon="icon" height="30px"/>
            </div>
            <div>
                <div class="text-2xl font-semibold line-height-1 text-right">{{dataLength}}</div>
                <div>{{$t(title)}}

                 
                </div>
            </div>
            
        </div>
    </Button>
</template>
<script setup>
    const props = defineProps({
        routeName: String,
        dataLength: String,
        title: String,
        currentRoute: String,
        icon: String
    })
    const emit = defineEmits(['onOpenRoute'])

    const onOpenRoute = () => {
        emit('onOpenRoute')
    }
</script>
<style>
.op_active_menu{
    background: var(--bg-btn-color) !important;
    color: #fff !important;
}
.op_menu { 
    background:rgb(169 170 255);
    border: 0;
}
</style>