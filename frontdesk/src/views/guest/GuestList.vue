<template>
    <ComHeader colClass="col-6" isRefresh @onRefresh="Refresh()">
           <template #start>
               <div class="text-xl md:text-2xl"> {{ $t('Guest Profile') }} </div>
           </template>
       </ComHeader>
<ComIframeContainer pageName="Guest Profile"  :defaultFilter="'property=' + property_name"/>
</template>
<script setup>
import {ref} from "@/plugin"
import ComIframeContainer from "@/components/ComIframeContainer.vue"
const property_name = ref(window.property_name)
</script>