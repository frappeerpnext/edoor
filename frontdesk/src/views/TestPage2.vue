<template>
    <div>
        <TestPage :list="msg" :test="test"  ref="input">
            <template v-slot="slotProps">
                <div class="text-red-400">{{ slotProps.data }}</div>
            </template>
        </TestPage>
        <Button type="button" @click="onClick">click</Button>
    </div>
</template>
<script setup> 
import {ref, onMounted} from 'vue'
import TestPage from './TestPage.vue'
var msg = ref(['A','B','C'])
const test = ref('v')
const input = ref()

function onClick(){
    test.value = 'ww'
}
onMounted(() => {
    console.log(input)
})
</script>
<style scoped>

</style>