<template>
    <ComDocumentList @onFilter="onFilter" 
     apiUrl="reservation.get_reservation_pickup"
      title="Reservation Pickup" 
       :options="options"
    showGridlines >
    </ComDocumentList>
</template>
<script setup>
import {inject ,ref,getYearOption,getMothOptions,getDaysInMonth} from "@/plugin"

const moment = inject("$moment")
 
const options = ref({
    filterOptions:[
        {fieldname:"month", fieldtype:"Select",options:getMothOptions(),label:"Month", default:moment(window.current_working_date).month()+1},
        {fieldname:"year", fieldtype:"Select",options:getYearOption(),label:"year",default:moment(window.current_working_date).year()}
    ],
    columns:getColumns(moment(window.current_working_date).month()+1,moment(window.current_working_date).year()),
    filters: [['property', '=', window.property_name]]
})
const filter= ref({})
  


function getColumns(month,year){
    let cols = [
        {field:"row_group",header:"Stays",action:"view_reservation_stay_detail",},
        
    ]
    getDaysInMonth(month,year).forEach(d=>{
        cols.push({field:d.value.toString(),header:d.value + " " +  d.label ,header_class:"text-center"})
    })
    
    return cols;
}

function onFilter(f){
   options.value.columns = getColumns(3,2025)
}


</script>