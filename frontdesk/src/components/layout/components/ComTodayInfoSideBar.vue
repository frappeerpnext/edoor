<template>
    <div class="flex flex-col justify-content-between align-items-center h-full">
        <div>
            <div class="flex justify-content-center align-items-center flex-col py-3 px-2 gap-4 -ms-2">
                <div class="relative">
                    <Button class="border-1 relative p-1" severity="info" style="background: rgb(169 170 255 / 43%)">
                        <ComIcon icon="iconArrivalGuest" height="30px" />
                    </Button>
                    <div class="absolute badge-today-info">
                        <Badge class="flex justify-content-center" value="8" severity="info"></Badge>
                    </div>
                </div>
                <div class="relative">
                    <Button class="bg-transparent border-0 p-1 relative">
                        <ComIcon icon="iconDepartureGuest" height="30px" />
                    </Button>
                    <div class="absolute badge-today-info">
                        <Badge class="flex justify-content-center" value="2" severity="info"></Badge>
                    </div>
                </div>
                <div class="relative">
                    <Button class="bg-transparent border-0 p-1 relative">
                        <ComIcon icon="iconStayOverGuest" height="30px" />
                    </Button>
                    <div class="absolute badge-today-info">
                        <Badge class="flex justify-content-center" value="5" severity="info"></Badge>
                    </div>
                </div>
            </div>
        </div>
        <div class="mb-5">
            <hr class="border-1 mb-1"/>
            <Button class="bg-transparent border-0 p-1 relative">
                <ComIcon icon="iconSetting" height="30px"/>
            </Button>
        </div>
    </div>
</template>
<script setup>

import ComIcon from '../../ComIcon.vue';

</script>