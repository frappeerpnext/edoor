<template>
    <div class="w-full">
        <div>
              
        <div class="flex w-full mt-2" v-for="(language, index) in languages" :key="index">
            <Button class="w-full surface-50" raised >
                <div class="bg-white p-1">
 <img style="width:30px;" :src="language.custom_flag" /> 
                </div>
           
            <p class="ms-3">{{ language.custom_language_name }}</p>  
            </Button>   
        </div>
       </div>
    </div>
</template>
<script setup>
import { inject, ref, getDocList, onMounted} from '@/plugin'
const languages = ref([])
onMounted(() => {
    getDocList('POS Translation', {
        fields: ['custom_language_name', 'custom_flag', 'name'],
        limit: 10000,
    })
    .then((doc) => {
        languages.value = doc
    })
    .catch((error) => {

    });
})
const selectedCountry = ref();
const countries = ref([
    { name: 'Australia', code: 'AU' },
    { name: 'Brazil', code: 'BR' },
    { name: 'China', code: 'CN' },
    { name: 'Egypt', code: 'EG' },
    { name: 'France', code: 'FR' },
    { name: 'Germany', code: 'DE' },
    { name: 'India', code: 'IN' },
    { name: 'Japan', code: 'JP' },
    { name: 'Spain', code: 'ES' },
    { name: 'United States', code: 'US' }
]);
</script>