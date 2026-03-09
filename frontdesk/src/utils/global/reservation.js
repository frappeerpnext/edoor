import ReservationDetail from "@/views/reservation/ReservationDetail.vue"
import ComGroupAssignRoom from "@/views/reservation/components/form/ComGroupAssignRoom.vue"
import {i18n} from '@/i18n';
const { t: $t } = i18n.global;
 

export function viewReservationDetail(name){
    if (!window.has_reservation_detail_opened){
        const dialogRef = window.dialog.open(ReservationDetail, {
        data: {
            name: name
        },
        props: {
            header: $t('Reservation Detail'),
            style: {
                width: '80vw',
            },
            maximizable: true,
            modal: true,
            closeOnEscape: false,
            position: "top",
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        }
    });
    }else {
        window.open('/frontdesk/reservation-detail/' + name, '_blank')
    }
}


export function onOpenGroupAssignRoom(reservation) {
    const dialogRef = window.dialog.open(ComGroupAssignRoom, {
        data: {
            reservation: reservation
        },
        props: {
            header: $t("Group Assign Room") + " - " + reservation.name,
            contentClass: 'ex-pedd',
            style: {
                width: '80vw',
            },
            position:"top",
            modal: true,
            maximizable: true,
            closeOnEscape: false,
            breakpoints:{
                '960px': '80vw',
                '640px': '100vw'
            },
        },
        onClose: (options)=>{
            if(options.data){
                if(options.data=="open_reservation_detail"){
                    window.postMessage('view_reservation_detail|' + reservation.name , '*')
                }
            }
        }
    });
}