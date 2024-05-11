<template>
    
    <ComDialogContent @onClose="onClose()" :hideButtonOK="true"   :hideButtonClose="False" :hideIcon="false" :loading="loading">
   
        <div class="grid">
            <div class="col-6">
                <table>
                    <ComStayInfoNoBox label="Rate Type" :value="data?.rate_type.name" />
                    <ComStayInfoNoBox label="Account Code" :value="data?.account_code.account_code_name" />
                </table>
            </div>
            <div class="col-6">
                <table>
                    <ComStayInfoNoBox label="Tax Rule" :value="data?.account_code.tax_rule" />
                </table>
            </div>
            <div class="p-2 surface-100 col-12 border-round-lg">
                <span class="text-lg line-height-4 font-bold mb-2 ">  Package
                </span>
            <DataTable :value="data?.account_code.packages" class="w-full">                
                <Column field="account_code" :header="$t('Account Code')" bodyClass="text-center" headerClass="text-center">
                    <template #body="slotProps">
                        <span @click="onEdit(slotProps.data)" >{{ slotProps.data.account_code }}-{{ slotProps.data.account_name }}</span>
                    </template>
                </Column>
            <Column field="posting_rule" header="Posting Rule" bodyClass="text-center" headerClass="text-center"></Column>   
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
        </DataTable>
    </div>
        </div>
    </ComDialogContent>

</template>
<script setup>
import {ref,inject,onMounted,getApi} from "@/plugin"
const dialogRef = inject("dialogRef");
const data = ref()
const loading = ref(false)
function onClose(){
    dialogRef.value.close();
}
onMounted(()=>{
    loading.value = true
    getApi("utils.get_package_detail",{
        rate_type:dialogRef.value.data.rate_type,
        date:dialogRef.value.data.date,
        property: window.property_name,
        business_source:dialogRef.value.data.business_source
    }).then(result=>{
        data.value = result.message
        loading.value = false
    }).catch(err=>{
        loading.value = false
    })
})


</script>