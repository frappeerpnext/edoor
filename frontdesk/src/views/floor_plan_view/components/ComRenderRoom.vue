<template>
    <Vue3DraggableResizable
                    :initW="110"
                    :initH="120"
                    v-model:x="position.x"
                    v-model:y="position.y"
                    v-model:w="size.width"
                    v-model:h="size.height"
                    v-model:active="active"
                    :draggable="true"
                    :resizable="true"
                    @drag-end="dragEndHandle"
                    @resizing="handleResizing"
                >
                    {{room.name}}
                </Vue3DraggableResizable>
                {{wrapperWidth}}
</template>
<script setup>
import {ref,inject,useToast} from "@/plugin"
const props = defineProps({
    room:Object,
    wrapperWidth:Number
})
const active = ref(true)

const position = ref({})
const size = ref({})

function dragEndHandle(t) {
    
    const height = document.getElementById("floor-plan-wrapper").clientHeight;

    if (position.value.x < 0){
        position.value.x=0
    }
    if (position.value.y < 0){
        position.value.y=0
    }
    
}

</script>