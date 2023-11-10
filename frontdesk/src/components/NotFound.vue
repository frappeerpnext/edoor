<template>
    <div class="w-full text-center mt-28">
        <div class="m-auto flex items-center flex-col">
            <div class="mb-2 flex justify-center items-center w-10rem h-10rem border-circle text-500">
             <ComIcon icon="NotDisturb" style="width: 100px;"></ComIcon>
            </div>
            <span class="text-3xl text-500">
Sorry, page you looking for is not found.
            </span>
        </div>
    </div>
</template>   
<script setup>
import {useRoute, useRouter,} from "@/plugin"
const route = useRoute()
const router = useRouter()
console.log(route) 
</script>