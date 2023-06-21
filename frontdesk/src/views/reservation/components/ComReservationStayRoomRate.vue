<template> 

 <Button label="Edit Rate" serverity="waring" @click="onEditRate"/>

<DataTable
v-model:selection="selected" :value="data" tableStyle="min-width: 80rem"
paginator :rows="20" :rowsPerPageOptions="[20, 50, 100]"
>
<Column selectionMode="multiple" headerStyle="width: 3rem"></Column>

<Column field="date" header="Date">
<template #body="slotProps">
<span>{{ gv.dateFormat(slotProps.data?.date) }}</span>
</template>
</Column>

<Column field="room_number" header="Room">
<template #body="slotProps">
{{ slotProps.data.room_number }} - {{ slotProps.data.room_type }}
</template>
</Column>

<Column field="rate_type" header="Rate Type" ></Column>

<Column field="rate" header="Rate" bodyStyle="text-align:right" headerStyle="text-align:right"  >
<template #body="{ data }"> 
<Button class="p-0 link_line_action1" link>
<CurrencyFormat :value="data.rate"/>
</Button>
</template>

</Column>

<Column field="discount_amount" header="Disount Amount" bodyStyle="text-align:right" headerStyle="text-align:right" >
<template #body="{ data }"> 
<Button class="p-0 link_line_action1" link>
<CurrencyFormat :value="data.discount_amount"/>
</Button>
</template>
</Column>

<Column field="total_tax" header="Total Tax" bodyStyle="text-align:right" headerStyle="text-align:right"  >
<template #body="{ data }"> 
<Button class="p-0 link_line_action1" link>
<CurrencyFormat :value="data.total_tax"/>
</Button>
</template>
</Column>

<Column field="total_amount" header="Total Amount" bodyStyle="text-align:right" headerStyle="text-align:right" >
<template #body="{ data }"> 
<Button class="p-0 link_line_action1" link>
<CurrencyFormat :value="data.total_amount"/>
</Button>
</template>
</Column>
  <ColumnGroup type="footer">
      <Row>
          <Column footer="Total:" :colspan="4" footerStyle="text-align:right"/>
          <Column footerStyle="text-align:right">
            <template #footer> 
            <CurrencyFormat :value="getTotal('rate')"/>
           </template>
          </Column>
          <Column :footer="getTotal('discount_amount')" footerStyle="text-align:right">
            <template #footer> 
            <CurrencyFormat :value="getTotal('discount_amount')"/>
          </template>
          </Column>
          <Column :footer="getTotal('total_tax')" footerStyle="text-align:right">
            <template #footer> 
            <CurrencyFormat :value="getTotal('total_tax')"/>
          </template>
          </Column>
          <Column footerStyle="text-align:right">
            <template #footer> 
            <CurrencyFormat :value="getTotal('total_amount')"/>
          </template>
          </Column>
      </Row>
  </ColumnGroup>
</DataTable>
<Dialog v-model:visible="visible" modal header="Edit Rate" :style="{ width: '50vw' }">
  {{ selected }}
   </Dialog>

</template>
<script setup>
import { inject, ref,getDocList,} from '@/plugin';
const rs = inject('$reservation_stay')
const data = ref([])
const selected = ref([])
const moment = inject("$moment")
const gv = inject('$gv')
const visible = ref(false)
const getTotal = ref((column_name) => {

if (data.value.length ==0){
return 0
}else{
return data.value.reduce((n, d) => n + d[column_name], 0)
}
});

getDocList('Reservation Room Rate',{
filters: [['reservation_stay', '=', rs.reservationStay.name]],
fields: [
  'date',
  'room_number',
  'room_type',
  'rate_type',
  'rate',
  'discount_amount',
  'total_tax',
  'total_amount',
],
orderBy: {
  field: 'date',
  order: 'asc',
},
})
.then((doc) => {
data.value = doc
})
.catch((error) => console.error(error));

function onEditRate() {
  
  visible.value = true
}

</script>
<style>
.p-datatable .p-column-header-content{
display : contents!important;
}
</style>