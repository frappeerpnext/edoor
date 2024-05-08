<template>
    <Vue3DraggableResizable
        :initW="initRoomSize.width"
        :initH="initRoomSize.height"
        v-model:x="room.floor_view.x"
        v-model:y="room.floor_view.y"
        v-model:w="size.width"
        v-model:h="size.height"
        v-model:active="active"
        :draggable="resizeable"
        :resizable="resizeable"
        @drag-end="dragEndHandle"
    >
                <div :style="{ background: room.status_color, height: 100 + '%'}">
                  {{room.name}}                 
                </div>
                    
                </Vue3DraggableResizable>
</template>
<script setup>
import {ref,inject,useToast,onMounted} from "@/plugin"
const props = defineProps({
    room:Object,
    resizeable:Boolean
})
const active = ref(false)
const size = ref({})
const initRoomSize = ref({})
const wrapperHeight = ref(0)
const wrapperWidth = ref(0)

function dragEndHandle(t) {
    
    // const height = document.getElementById("floor-plan-wrapper").clientHeight;

    // if (position.value.x < 0){
    //     position.value.x=0
    // }
    // if (position.value.y < 0){
    //     position.value.y=0
    // }
    
}

onMounted (()=>{
    wrapperWidth.value = document.getElementById("floor-plan-wrapper").clientWidth
    wrapperHeight.value = document.getElementById("floor-plan-wrapper").clientHeight
    initRoomSize.value.width = props.room.floor_view.width / 100 * wrapperWidth.value
    initRoomSize.value.height = props.room.floor_view.height / 100 * wrapperHeight.value
})

</script>
<style>
</style>