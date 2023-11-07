import { doc, folioNumberFilter, checkbox1, checkbox2 } from "./ComAddFolioTransaction.vue";

// const areCheckboxesMutuallyExclusive = computed(() => {
//   return checkbox1.value !== checkbox2.value;
// });
export function onFilterFolioNumber(checkbox: { value: boolean; }) {
if (doc.value.select_folio_in_reservation_stay == 1) {
folioNumberFilter.value.reservation_stay = doc.value.reservation_stay;
} else {
delete folioNumberFilter.value.reservation_stay;
}

if (checkbox.value) {
if (checkbox === checkbox1) {
checkbox2.value = false;
} else {
checkbox1.value = false;
}
}
}
