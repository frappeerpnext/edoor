<template>
   <div class="grid w-full mt-1" >
            <div class="col-6">
                <div class="shadow-2 p-3 surface-50 rounded">
                    <div class="line-height-1">
                    <h3 class="text-lg font-medium">Summary</h3>
                    <div>Reservation : {{ data.daily_reservation }}</div>
                    </div>
                    <div class="flex mb-2">
                        <div class="col-2 line-height-1 border-right-1" style="color: rgb(236, 134, 75);">
                            <h3 class="text-2xl font-medium">{{data.arrival}}</h3>
                            <span>Arrival</span>
                        </div>
                        <div class="col-2 line-height-1 border-right-1" style="color: #50ac58;">
                            <h3 class="text-2xl font-medium">{{data.total_in_house}}</h3>
                            <span>In House</span>
                        </div>
                        <div class="col-2 line-height-1 border-right-1" style="color:rgb(79, 79, 79);">
                            <h3 class="text-2xl font-medium">{{data.departure - data.departure_remaining}}</h3>
                            <span>Checked Out</span>
                        </div>
                        <div class="col-2 line-height-1 border-right-1" style="color: rgb(130, 130, 5);">
                            <h3 class="text-2xl font-medium">{{data.total_no_show}}</h3>
                            <span>No Show</span>
                        </div>
                        <div class="col-2 line-height-1 border-right-1" style="color:rgb(237, 99, 150);">
                            <h3 class="text-2xl font-medium">{{data.total_cancelled}}</h3>
                            <span>Cancelled</span>
                        </div>
                        <div class="col-2 line-height-1" style="color:rgb(255, 0, 0);">
                            <h3 class="text-2xl font-medium">{{data.total_void}}</h3>
                            <span>Void</span>
                        </div>
                    </div>
                    <div  class="w-full " >
                    <div style="height: 2px;" class=" w-full surface-ground flex">
                    <div style="background-color: rgb(236, 134, 75);" :style="{width:(data.arrival / totalres) * 100 + '%' }"></div> 
                    <div style="background-color: #50ac58" :style="{width:(data.total_in_house / totalres ) * 100 + '%' }"></div>
                    <div style="background-color: rgb(130, 130, 5);" :style="{width:(data.departure / totalres ) * 100 + '%' }"></div>   
                    <div style="background-color: rgb(236, 134, 75);" :style="{width:(data.total_no_show / totalres) * 100 + '%' }"></div> 
                    <div style="background-color: rgb(237, 99, 150);" :style="{width:(data.total_cancelled / totalres ) * 100 + '%' }"></div>
                    <div style="background-color: rgb(255, 0, 0)" :style="{width:(data.total_void / totalres ) * 100 + '%' }"></div>    
                    </div> 
                    </div>
                </div>
            </div>
            <div class="col-4">
                <div class="shadow-2 p-3 surface-50 rounded">
                    <div class="line-height-1">
                    <h3 class="text-lg font-medium">Occupancy</h3>
                    <div>Total Room : {{ data.total_room }}</div>
                    </div>
                    <div class="flex mb-2 color-text">
                        <div class="col-4 line-height-1 border-right-1 occupy" >
                            <h3 class="text-2xl font-medium">{{data.total_room_occupy}}</h3>
                            <div class="flex">
<span>Occupy - {{ data.occupancy }}%</span>
                            </div>
                        </div>
                        <div class="col-4 line-height-1 border-right-1 vacant">
                            <h3 class="text-2xl font-medium">{{data.total_room_vacant}}</h3>
                            <span>Vacant Room</span>
                        </div>
                        <div class="col-4 line-height-1 block">
                            <h3 class="text-2xl font-medium">{{data.total_room_block}}</h3>
                            <span>Room Block</span>
                        </div>
                        
                    </div>
                    <div  class="w-full background-color" >
                    <div style="height: 2px;" class=" w-full surface-ground flex">
                    <div class="occupy" :style="{width:(data.total_room_occupy / data?.total_room) * 100 + '%' }"></div> 
                    <div class="vacant" :style="{width:(data.total_room_vacant / data?.total_room ) * 100 + '%' }"></div>
                    <div class="block" :style="{width:(data.total_room_block / data?.total_room ) * 100 + '%' }"></div>    
                    </div> 
                    </div>
                </div>
            </div>
            <div class="col-2">
                <div class="shadow-2 p-3 surface-50 rounded">
                    <div class="line-height-1">
                    <h3 class="text-lg font-medium">Transportation</h3>
                    <div>Total : {{totalupandoff}}</div>
                    </div>
                    <div class="flex mb-2 color-text">
                        <div class="col-6 line-height-1 border-right-1 pick_up" >
                            <h3 class="text-2xl font-medium">{{data.pick_up}}</h3>
                            <div class="flex">
<span>Pickup </span>
                            </div>
                        </div>
                        <div class="col-6 line-height-1 drop_off">
                            <h3 class="text-2xl font-medium">{{data.drop_off}}</h3>
                            <span>Drop Off</span>
                        </div>
                    </div>
                    <div  class="w-full background-color" >
                    <div style="height: 2px;" class=" w-full surface-ground flex">
                    <div class="pick_up" :style="{width:(data.pick_up / totalupandoff) * 100 + '%' }"></div> 
                    <div class="drop_off" :style="{width:(data.drop_off / totalupandoff ) * 100 + '%' }"></div>
                    </div> 
                    </div>
                </div>
            </div>
    </div>  
</template>
    <script setup>
    import { inject } from '@/plugin';
    const moment = inject("$moment")
    const props = defineProps({
        data:Object
    })
    let totalres = props?.data.arrival + props?.data.total_in_house + props?.data.departure + props?.data.total_cancelled + props?.data.total_no_show + props?.data.total_void
    let totalupandoff = props?.data.pick_up + props?.data.drop_off 
    if (totalupandoff === 0) {
        totalupandoff = 1;
      }

</script>
<style scoped>
.color-text .occupy {
  color: #50ac58;
}
.background-color .occupy {
  background-color: #50ac58;
}
.color-text .vacant {
  color: rgb(236, 134, 75);
}
.background-color .vacant {
  background-color: rgb(236, 134, 75);
}
.color-text .block {
  color: black;
}
.background-color .block {
  background-color: black;
}
.color-text .pick_up {
  color: #50ac58;
}
.background-color .pick_up {
  background-color:#50ac58;
}
.color-text .drop_off {
  color: black;
}
.background-color .drop_off {
  background-color:black;
}
</style>
