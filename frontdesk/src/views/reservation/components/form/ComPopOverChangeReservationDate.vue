<template>
   <ComOverlayPanelContent title=" Change Reservation" width="50rem">
    
        <div class="grid py-2">
            <div class="col-6">
                <label>Arrival Date</label>
                <Calendar hideOnDateTimeSelect  :selectOtherMonths="true" showIcon   @update:modelValue="onStartDate" dateFormat="dd-mm-yy" class="w-full"/>
            </div>
            <div class="col-6">
                <label>Arrival Time</label>
                <Calendar selectOtherMonths class="w-full"  timeOnly />
            </div>
            <div class="col-6">
                <label>Departure Date</label>
                <Calendar selectOtherMonths hideOnDateTimeSelect showIcon  :selectOtherMonths="true"  @update:modelValue="onEndDate" dateFormat="dd-mm-yy" class="w-full"/>
            </div>
            <div class="col-6">
                <label>Departure Time</label>
                <Calendar selectOtherMonths class="w-full"  timeOnly /> 
            </div>
            <div class="col-6">
                <label>Nights</label>
                <InputNumber  @update:modelValue="onNight($event)" inputId="stacked-buttons" showButtons :min="1" class="w-full nig_in-put"/>
            </div>
        </div>
    
   </ComOverlayPanelContent>
</template>
<script setup>

</script>