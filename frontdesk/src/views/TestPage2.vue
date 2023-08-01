<template>
    <div>
        <TestPage :list="msg" :test="test"  ref="input">
            <template v-slot="slotProps">
                <div class="text-red-400">{{ slotProps.data }}</div>
            </template>
        </TestPage>
        <Button v-my-directive type="button" @click="updateLocation">trueFalse : {{!trueFalse}}</Button> 
    </div>
</template>
<script setup> 
import {ref, onMounted, provide } from 'vue'
import TestPage from './TestPage.vue'
var msg = ref(['A','B','C'])
const trueFalse = ref(true)
const input = ref()
const location = ref(false)

function updateLocation() {
  location.value = !location.value
}

provide('location',{
    location,
    updateLocation
})
const vMyDirective = {
  beforeMount: (para) => {
    // do something with the element
    para.style.color = "white";
    para.style.backgroundColor = "black";
    para.style.padding = "10px";
    para.style.width = "250px";
    para.style.textAlign = "center";
    para.setAttribute('data-id','test')
  }
}
 
function onClick(){
    test.value = 'ww'
}
 

</script>
<style scoped>

</style>