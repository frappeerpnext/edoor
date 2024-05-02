<template>
    <div class="w-full mt-1">
        <ComOwnerDashboardKPI/>
    </div>    
    <div class="grid px-2 mt-2">
        <div class="col-12 bg-green-500">
    current chart
</div>        
<div class="col-6 p-0">
        <div class="col-12 p-0 h-auto bg-white">Payment</div>
        <div class="col-12 p-0 h-auto bg-red-500">Room Type</div>
</div>
<div class="col-6 h-auto bg-blue-500">
    <div class="h-full">
        Charge
    </div>
</div>
<div class="col-12 bg-green-500">
    room type
</div> 
<div class="col-6 bg-black">
    FB
</div> 
<div class="col-6 bg-pink-500">
    FBpayment
</div> 
<div class="col-12 bg-red-500">
    city
</div> 
<div class="col-12 bg-green-500">
    folio
</div> 
</div>
</template>
<script setup>

import ComOwnerDashboardKPI from '@/views/dashboard/components/ComOwnerDashboardKPI.vue' 

</script>