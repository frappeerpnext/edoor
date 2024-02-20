<template>
    <div class="grid px-2  mb-3 mt-3">
                    <div :class="(index === summary.length - 1) ? 'bg-green-50 border-green-edoor' : 'bg-white'"
                        class="col-12 md:col md:mx-1 my-1 rounded-lg shadow-charge-total border"  v-for="(s, index) in summary"
                        :key="index">
                        <div class="flex justify-content-between">

                            <span  class="text-500  text-sm text-end">
                                <span class="white-space-nowrap" v-if="s.label == 'Opening Balance'">
                                    Balance From {{ moment(start_date).subtract(1, 'days').format("DD-MM-YYYY") }}    
                                </span>
                                <span class="white-space-nowrap" v-if="s.label == 'Ending Balance'">
                                    Balance of {{ moment(end_date).format("DD-MM-YYYY") }}    
                                </span>
                               </span>
                             <span class="text-600 uppercase text-sm text-end white-space-nowrap">{{ s.label }}</span>
                       
                        </div>
                        <div class="flex justify-end">
                        <span
                            class="text-xl line-height-2 font-semibold text-end">
                            <span>{{ s.value }}</span></span>
                        </div>
                           
                        </div> 
                      
                    <!-- <ComBoxSummaryBalanceTransaction v-if="summary" label="Audit Date" :value='moment(start_date).format("DD-MM-YYYY")' :class="'bg-purple-50 border-purple-300 md:mx-1 my-1'"  /> -->
                </div>
</template>
<script setup>
import { inject, getDoc, ref } from '@/plugin';
const moment = inject("$moment")
import ComBoxSummaryBalanceTransaction from '@/views/city_ledger/components/ComBoxSummaryBalanceTransaction.vue' 
const props = defineProps({
    summary: Object,
    start_date:Date,
    end_date:Date
})

</script>