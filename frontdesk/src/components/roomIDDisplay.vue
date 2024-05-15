<template>
    <div>
        <div> 
            <span v-for="(i, index) in item" :key="index">
                <div class="inline" v-if="index < 3">
                    <div class="rounded-xl px-2 me-1 inline text-white" style="background-color: #B5C18E;">
                    <span>{{ i }}  
                    </span>
                    </div>
                </div>
            </span>
            <span v-if="item.length > 3"  
                class="inline rounded-xl px-2 bg-purple-cs w-auto ms-1 cursor-pointer">
                {{item.length - 3}} Mores
            </span>
        </div>
    </div>
</template>
<script setup> 
    const props = defineProps({
        item:Object
    })
</script>