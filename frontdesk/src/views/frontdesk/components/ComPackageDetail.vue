<template>
    
    <ComDialogContent @onClose="onClose()" :hideButtonOK="true"   :hideButtonClose="False" :hideIcon="false" :loading="loading">
   
        <div class="grid">
            <div class="col-6">
                <table>
                    <tr>
                        <th colspan="2" class="py-2 mt-1 border-1 bg-slate-200 font-medium text-center">
                            {{ $t('Reservation Stay Detail') }}
                            </th>
                    </tr>
                    <ComStayInfoNoBox label="Rate Type" :value="data?.rate_type.name" />

                    <ComStayInfoNoBox label="Account Code" :value="data?.account_code.account_code_name" />
                    <ComStayInfoNoBox label="Tax Rule" :value="data?.account_code.tax_rule" />
                    

                </table>
            </div>
            <div class="col-6">
            </div>
            <div class="p-2 surface-100 col-12">
                <span class="text-lg line-height-4 font-bold mb-2">  Package
                </span>
          
            <DataTable :value="data?.account_code.packages" class="w-full">                
            <Column field="account_code"  header="Account Code"></Column>
            <Column field="posting_rule" header="Posting Rule"></Column>   
            <Column field="charge_rule" header="Charge Rule"></Column>
            <Column field="rate" headerClass="text-end" bodyClass="text-end" header="Rate"></Column>
            <Column field="adult_rate" header="Adult Rate"></Column> 
            <Column field="child_rate" header="Child Rate"></Column> 
        </DataTable>
    </div>
        </div>


        
        <hr/>
        {{ dialogRef.data.room_type_rate  }}
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