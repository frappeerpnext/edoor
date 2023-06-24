<template> 
<div class="min-h-folio-cus">
  <Button label="Edit Rate" serverity="waring" @click="onEditRate"/>
  <Button label="Edit Ratexx" serverity="waring" @click="onEditRoomRate"/>
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
            <Column footerStyle="text-align:right">
              <template #footer> 
              <CurrencyFormat :value="getTotal('discount_amount')"/>
            </template>
            </Column>
            <Column footerStyle="text-align:right">
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
</div>

<Dialog v-model:visible="visible" modal header="Edit Rate" :style="{ width: '50vw' }">
  Stay Number: {{ rs.reservationStay?.name }} <br>
  Room: {{ rs.reservationStay?.rooms }} <br>
  Room Type: {{ rs.reservationStay?.room_types }} <br>
  Guest code: {{ rs.guest?.name }} <br>
  Guest name: {{ rs.guest.customer_name_en }} <br>
  Phone: {{ rs.guest.phone_number }} <br>
  Pax: {{ rs.reservationStay?.adult }}/{{ rs.reservationStay?.child }}<br>
 
  <hr/>
  <div v-if="selected.length>0">

    <InputNumber class="w-full"  v-model="doc.rate" />
    <ComSelect v-model="doc.rate_type" doctype="Rate Type"  :clear="false" />
    <ComSelect v-model="doc.discount_type" :options="['Percent','Amount']" :clear="false" />
    <Checkbox v-model="doc.rate_include_tax" :binary="true" trueValue="Yes" falseValue="No" /> Rate Incldue Tax
    <InputNumber class="w-full"  v-model="doc.discount" />
    <InputNumber class="w-full"  v-model="doc.discount_amount" />
    <Checkbox v-model="doc.tax_1_rate" :binary="true" trueValue="Yes" falseValue="No" />
    <InputNumber class="w-full"  v-model="doc.tax_1_rate" />
    <Checkbox v-model="doc.tax_2_rate" :binary="true" trueValue="Yes" falseValue="No" />
    <InputNumber class="w-full"  v-model="doc.tax_2_rate" />
    <Checkbox v-model="doc.tax_3_rate" :binary="true" trueValue="Yes" falseValue="No" />
    <InputNumber class="w-full"  v-model="doc.tax_3_rate" />
    <InputNumber class="w-full"  v-model="doc.total_rate" />
    <InputNumber class="w-full"  v-model="doc.note" />
    
    {{ doc }}
  </div>
</Dialog>

</template>
<script setup>
import { inject, ref,getDocList,useDialog} from '@/plugin';
import ComEditReservationRoomRate from './ComEditReservationRoomRate.vue';
const rs = inject('$reservation_stay')
const data = ref([])
const selected = ref([])
const moment = inject("$moment")
const gv = inject('$gv')
const dialog = useDialog();
const visible = ref(false)
const getTotal = ref((column_name) => {
  if (data.value.length ==0){
    return 0
  }else{
    return data.value.reduce((n, d) => n + d[column_name], 0)
  }
});

const doc = ref({})

getDocList('Reservation Room Rate',{
filters: [['reservation_stay', '=', rs.reservationStay.name]],
fields: ["*"],
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
  if(selected.value.length>0){
  visible.value = true

    doc.value = JSON.parse(JSON.stringify(selected.value[0]))
  }
  
}

function onEditRoomRate() {

const dialogRef = dialog.open(ComEditReservationRoomRate, {
  data: {
           reservation_stay: rs.reservationStay,

        },
        props: {
            header: 'Edit Room Rate ',
            style: {
                width: '50vw',
            },

            modal: true
        },
        
})
}

</script>
<style>
.p-datatable .p-column-header-content{
display : contents!important;
}
</style>