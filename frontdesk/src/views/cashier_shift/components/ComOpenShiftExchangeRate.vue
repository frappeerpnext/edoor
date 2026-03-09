<template lang="">
    <div class="absolute top-1/4" style="right:10px;">
        <Button v-if="item.exchange_rate!=1" @click="toggleExchangeRate" icon="pi pi-question text-xs" class="float-left w-1rem h-1rem -ms-1 surface-border" severity="secondary" rounded outlined aria-label="Exchange Rate" />
        <OverlayPanel ref="opExchangeRate">
            <ComOverlayPanelContent hideButtonOK style="min-width:15rem;" title="Exchange Rate" :hideFooter="true">
                <div>
                    
                    <Message :closable="false">Excahnge Rate: {{ item.exchange_rate }} {{item.currency}}</Message>
                </div>
            </ComOverlayPanelContent>
        </OverlayPanel>
    </div>
</template>
<script setup>
import {ref} from 'vue'
const props = defineProps({
    item:Object
})
const opExchangeRate = ref()
const toggleExchangeRate = ($event) => {
    opExchangeRate.value.toggle($event)
}
</script>
<style lang="">
    
</style>