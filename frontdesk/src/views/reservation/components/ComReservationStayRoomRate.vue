<template>
  <div class="min-h-folio-cus mt-3">

    <Button label="Edit Rate" class="conten-btn mr-1 mb-3" serverity="waring" @click="onEditRoomRate()" />
 
    <DataTable v-model:selection="selectedRoomRates" :value="data" tableStyle="min-width: 80rem" paginator :rows="20"
      :rowsPerPageOptions="[20, 50, 100]">
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
      
      <Column field="rate_type" header="Rate Type"></Column>
        <Column field="rate" header="Rate" bodyStyle="text-align:right" headerStyle="text-align:right">
          <template #body="{ data }">
            <Button class="p-0 link_line_action1" link>
            
              <CurrencyFormat :value="data.rate" />
              
            </Button>
          </template>
      </Column>

      <Column field="discount_amount" header="Disount Amount" bodyStyle="text-align:right" headerStyle="text-align:right">
        <template #body="{ data }">
          <Button class="p-0 link_line_action1" link @click="onEditRoomRate(data)">
            <CurrencyFormat :value="data.discount_amount" />
          </Button>
        </template>
      </Column>

      <Column field="total_tax" header="Total Tax" bodyStyle="text-align:right" headerStyle="text-align:right">
        <template #body="{ data }">
          <Button class="p-0 link_line_action1" link>
            <CurrencyFormat :value="data.total_tax" />
          </Button>
        </template>
      </Column>

      <Column field="total_amount" header="Total Amount" bodyStyle="text-align:right" headerStyle="text-align:right">
        <template #body="{ data }">
          <Button class="p-0 link_line_action1" link>
            <CurrencyFormat :value="data.total_rate" />
          </Button>
        </template>
      </Column>
      <ColumnGroup type="footer">
        <Row>
          <Column footer="Total:" :colspan="3" footerStyle="text-align:right" />
          <Column >
            <template #footer>
              {{ data.length }} Room Night(s)
            </template>
          </Column>
          <Column footerStyle="text-align:right">
            <template #footer>
              <CurrencyFormat :value="getTotal('rate')" />
            </template>
          </Column>
          <Column footerStyle="text-align:right">
            <template #footer>
              <CurrencyFormat :value="getTotal('discount_amount')" />
            </template>
          </Column>
          <Column footerStyle="text-align:right">
            <template #footer>
              <CurrencyFormat :value="getTotal('total_tax')" />
            </template>
          </Column>
          <Column footerStyle="text-align:right">
            <template #footer>
              <CurrencyFormat :value="getTotal('total_rate')" />
            </template>
          </Column>
        </Row>
      </ColumnGroup>
    </DataTable>
  </div>
 
</template>
<script setup>
import { inject, ref, getDocList, useDialog } from '@/plugin';
import ComEditReservationRoomRate from './ComEditReservationRoomRate.vue';

const rs = inject('$reservation_stay')
const data = ref([])
const selectedRoomRates = ref([])
const moment = inject("$moment")
const gv = inject('$gv')
const dialog = useDialog();
const visible = ref(false)


const getTotal = ref((column_name) => {
  if (data.value.length == 0) {
    return 0
  } else {
    return data.value.reduce((n, d) => n + d[column_name], 0)
  }
});

const doc = ref({})

getDocList('Reservation Room Rate', {
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

 

function onEditRoomRate(room_rate = null) {
 
  const dialogRef = dialog.open(ComEditReservationRoomRate, {
      data: {
        selected_room_rate:room_rate,
        selected_room_rates:selectedRoomRates.value,
        reservation_stay:rs.reservationStay
        },
      props: {
        header: 'Edit Room Rate ',
        style: {
          width: '50vw',
        },

        modal: true
      },
      onClose: (options) => {
        const result = options.data;
        
        if(result){
            data.value = result
        }
    }

    })

}

</script>
<style>
.p-datatable .p-column-header-content {
  display: contents !important;
}
</style>