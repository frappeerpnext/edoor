<template>

    <div> 
        <Button @click="onAuditTrail"> Audit Trail</Button>
    </div>
</template>
<script setup>
import {ref, updateDoc, getDoc, useDialog } from '@/plugin'
import ComAuditTrail from '../components/layout/components/ComAuditTrail.vue';
const dialog = useDialog()
 
function onAuditTrail(){
    const dialogRef = dialog.open(ComAuditTrail, {
        data: {
            doctype: 'Reservation Stay',
            docname: 'ST2023-0245'
        },
        props: {
            header: 'Audit Trail',
            style: {
                width: '75vw',
            },
            breakpoints: {
                '960px': '100vw',
                '640px': '100vw'
            },
            modal: true,
            maximizable: true,
        },
        onClose: (options) => {
            //
        }
    });
}
</script> 