<template>
   
        <span :class="statusAddiClass?statusAddiClass:''" v-if="status=='Open'" class=" line-height-2 py-1 px-3 text-green-700 font-medium border-round-lg bg-green-200 me-1 uppercase ">
          {{ $t('Open') }}
            
        </span>
        <span v-else :class="statusAddiClass?statusAddiClass:''" class="border-round-lg line-height-2 py-1 px-3 text-black font-medium bg-gray-200 me-1 uppercase">
           {{ $t('Close') }} 
        </span>
        <!-- <Chip label="Close" v-else class="bg-red-500"/> -->

</template>
<script setup>
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
    const props =defineProps({
        status:{
            type:String,
            default:"Open"
        },
        statusAddiClass:String
    }
    )
</script>