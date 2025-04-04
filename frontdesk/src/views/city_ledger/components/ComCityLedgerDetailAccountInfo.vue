<template>
            <Panel class="p-0" header="City Ledger Information" toggleable>
                <div class="-m-3">
                <table>
                        <tbody>
                        <ComStayInfoNoBox label="City Ledger Name" :value="data?.city_ledger_name" />
                        <ComStayInfoNoBox label="City Ledger Type" :value="data?.city_ledger_type" />
                        <ComStayInfoNoBox label="Business Source" :value="data?.business_source" />
                        <ComStayInfoNoBox label="Company Name" :value="data?.company_name" />
                        <ComStayInfoNoBox label="Phone Number" :value="data?.phone_number" />
                        <ComStayInfoNoBox label="Email" :value="data?.email_address" />
                        <ComStayInfoNoBox label="Address" :value="data?.address" />
                    </tbody>
                </table>
            </div>
         </Panel>
         <Panel class="mt-2" header="Bank Information" toggleable>
                <div class="-m-3">
                <table>
                        <tbody>
                            <ComStayInfoNoBox label="Bank Name" :value="data?.bank_name" />
                                <ComStayInfoNoBox label="Bank Account Number" :value="data?.bank_account_number" />
                                <ComStayInfoNoBox label="Bank Account Name" :value="data?.bank_account_name" />
                    </tbody>
                </table>
            </div>
         </Panel>
         <Panel class="mt-2" header="Contact Person Information" toggleable>
                <div class="-m-3">
                <table>
                        <tbody>
                            <ComStayInfoNoBox label="Contact Name" :value="data?.contact_name" />
                            <ComStayInfoNoBox label="Contact Phone Number" :value="data?.contact_phone_number" />
                    </tbody>
                </table>
            </div>
         </Panel>

    
</template>
<script setup>
import { ref, inject, useDialog, useConfirm ,postData } from '@/plugin'
const props = defineProps({
    data: Object,
})
</script>