<template>
    <div class="flex justify-content-between align-items-center flex-wrap wp-btn-post-in-stay-folio mb-3">
        <div>
            <Button v-for="(d, index) in setting?.account_group" :key="index" @click="onAddFolioTransaction(d)"
                class="conten-btn mr-1">Post {{ d.account_name }}</Button>
        </div>
        <div>
          
            <SplitButton class="spl__btn_cs sp mr-1" label="Print" icon="pi pi-print" :model="more_item_folio_stay" />
            <SplitButton class="spl__btn_cs sp" label="Mores" icon="pi pi-list" :model="more_item_folio_stay" />
            <Button type="button" label="Toggle" @click="toggle" aria-haspopup="true" aria-controls="folio_menu" />
            <Menu ref="folio_menu" id="folio_menu"   :popup="true">
                <template #end>
                    <button @click="toggle"  class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                        <i class="pi pi-sign-out" />
                        <span class="ml-2">Mark as Master Folio</span>
                    </button>
                    
                
                    <button @click="toggle" v-if="rs.selectedFolio?.status =='Open'"  class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                        <i class="pi pi-sign-out" />
                        <span class="ml-2">Close Folio</span>
                    </button>
                    
                    <button @click="toggle" v-if="rs.selectedFolio?.status =='Closed'" class="w-full p-link flex align-items-center p-2 pl-4 text-color hover:surface-200 border-noround">
                        <i class="pi pi-sign-out" />
                        <span class="ml-2">Open Folio</span>
                    </button>

                </template>
            </Menu>

        </div>
    </div>
</template>
<script setup>

import ComAddFolioTransaction from "@/views/reservation/components/ComAddFolioTransaction.vue"
import { useDialog } from 'primevue/usedialog';
import { useConfirm } from "primevue/useconfirm";
import { inject, ref, computed, useToast } from '@/plugin';
import ComNote from '@/components/form/ComNote.vue';
import Menu from 'primevue/menu';
const dialog = useDialog();
const confirm = useConfirm();
const frappe = inject('$frappe');
const call = frappe.call();
const db = frappe.db();
const toast = useToast();
const rs = inject("$reservation_stay")


const setting = JSON.parse(localStorage.getItem("edoor_setting"))

const folio_menu = ref();
 

const toggle = (event) => {
    folio_menu.value.toggle(event);
};

const more_item_folio_stay = ref([
    {
        label: 'Set as Master Folio',
        icon: 'pi pi-refresh',
         
    },
    {
        label: 'Delete Folio',
        icon: 'pi pi-times',
        command: () => {
            const dialogRef = dialog.open(ComNote, {
                props: {
                    header: "Delete Folio - " + rs.selectedFolio.name,
                    style: {
                        width: '350',
                    },
                    modal: true
                },
                onClose: (options) => {
                    const data = options.data;
                    if (data != undefined) {
                        call
                            .delete('edoor.api.utils.delete_doc', { doctype: "Reservation Folio", name: rs.selectedFolio.name, note: data })
                            .then((result) => {
                                rs.onLoadReservationFolios().then(() => {
                                    if (rs.folios.length > 0) {
                                        rs.onLoadFolioTransaction(rs.folios[0].name)
                                    }

                                    rs.loading = false;
                                    toast.add({ severity: 'success', summary: "Delete Folio", detail: "Delete Folio successfully", life: 3000 })
                                })
                            })

                    }
                }
            })
        }

    },
    {
        label: 'Close Folio',
        icon: 'pi pi-external-link',
 
        command: () => {
            confirm.require({
                target: event.currentTarget,
                message: 'Are you sure you want to close folio?',
                icon: 'pi pi-exclamation-triangle',
                accept: () => {
                    db.updateDoc('Reservation Folio', rs.selectedFolio.name, {
                        status: 'Closed',
                    })
                        .then((doc) => {

                            rs.selectedFolio.status =doc.status;
                            toast.add({ severity: 'info', summary: 'Close Folio', detail: 'Close Folio successfully', life: 3000 });

                        })

                },
                
            })
        }
    },
    {
        label: 'Open Folio',
        icon: 'pi pi-external-link',
       
        command: () => {
            confirm.require({
                target: event.currentTarget,
                message: 'Are you sure you want to open folio?',
                icon: 'pi pi-exclamation-triangle',
                accept: () => {
                    db.updateDoc('Reservation Folio', rs.selectedFolio.name, {
                        status: 'Open',
                    })
                        .then((doc) => {
                            rs.selectedFolio.status =doc.status;
                            toast.add({ severity: 'info', summary: 'Open Folio', detail: 'Open Folio successfully', life: 3000 });

                        })

                },
               
            })
        }
    },
    {
        label: 'Upload',
        icon: 'pi pi-upload',
    }
]);


function onAddFolioTransaction(account_code) {

    const dialogRef = dialog.open(ComAddFolioTransaction, {
        data: {
            folio_number: rs.selectedFolio.name,
            account_group: account_code.name,
            balance: rs.totalDebit - rs.totalCredit
        },
        props: {
            header: 'Post ' + account_code.account_name,
            style: {
                width: '50vw',
            },

            modal: true
        },
        onClose: (options) => {
            const data = options.data;

            if (data) {
                rs.onLoadFolioTransaction(rs.selectedFolio)
            }

        }
    })
}



</script>