<template>
    <div class="min-h-folio-cus mt-3">
        <DataTable  :value="data" tableStyle="min-width: 80rem" paginator :rows="20"
      :rowsPerPageOptions="[20, 50, 100]">
                <Column field="account_code" :header="$t('Account Code')" bodyClass="text-center" headerClass="text-center">
                    <template #body="slotProps">
                        <span>{{ slotProps.data.account_code }}</span>
                    </template>
                </Column>
                <Column field="posting_rule" :header="$t('Posting Rule')" bodyClass="text-center" headerClass="text-center">
                    <template #body="slotProps">
                        <span>{{ slotProps.data.posting_rule }}</span>
                    </template>
                </Column>
                <Column field="charge_rule" :header="$t('Charge Rule')" bodyClass="text-center" headerClass="text-center">
                    <template #body="slotProps">
                        <span>{{ slotProps.data.charge_rule }}</span>
                    </template>
                </Column>
                <Column field="rate" :header="$t('Rate')" bodyClass="text-right" headerClass="text-right">
                    <template #body="slotProps">
                        <CurrencyFormat :value="slotProps.data.rate" />
                    </template>
                </Column>
                <Column field="adult_rate" :header="$t('Adult Rate')" bodyClass="text-right" headerClass="text-right">
                    <template #body="slotProps">
                        <CurrencyFormat :value="slotProps.data.adult_rate" />
                    </template>
                </Column>
                <Column field="child_rate" :header="$t('Child Rate')" bodyClass="text-right" headerClass="text-right">
                    <template #body="slotProps">
                        <CurrencyFormat :value="slotProps.data.child_rate" />
                    </template>
                </Column>
                <Column header="">
                    <template #body="slotProps">
                        <div v-if="slotProps.data.name">
                            <div class="res_btn_st">
                            <Button class="h-2rem w-2rem" style="font-size: 1.5rem" text rounded icon="pi pi-ellipsis-v"
                                @click="toggle"></Button>
                        </div>
                        <Menu :model="menus" :popup="true" ref="show" style="min-width: 180px;">
                            <template #end>
                                <template v-if="isEdit">
                                    <button
                                        class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                                        {{$t('Edit')}}
                                    </button>
                                </template>
                                <template v-if="isDelete">
                                    <button 
                                        class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                                        {{$t('Delete')}} 
                                    </button>
                                </template>
                            </template>
                        </Menu>
                        </div>
                    </template>
                </Column>
                </DataTable>
    </div>
</template>
<script setup>
import {ref,inject} from "@/plugin"
import {i18n} from '@/i18n';

const { t: $t } = i18n.global;
const gv = inject("$gv")
const rs =inject("$reservation_stay")
const data = rs.reservationStay?.inclusion_items
const props = defineProps({
    data: Object,
    isEdit: {
        type: Boolean,
        default: true
    },
    isDelete: {
        type: Boolean,
        default: true
    }
})
const show = ref()
const loading = ref()
const opDelete = ref(false)
const toggle = (event) => {
    show.value.toggle(event)
}
function onEdit(){

}
function onOpenDelete() {
   
   
}

</script>