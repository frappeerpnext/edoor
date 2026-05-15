import ComTaskDetail from "@/views/channel_managers/task/ComTaskDetail.vue"
import ComTaskLisk from "@/views/channel_managers/task/ComTaskLisk.vue"
import ComViewSyncData from "@/views/channel_managers/components/ComViewSyncData.vue"
import ComViewChangeDataLog from "@/components/ComViewChangeDataLog.vue"
import ComViewAvailabilityDataDialog from "@/components/availability/ComViewAvailabilityData.vue"
import ComReportServerModal  from "@/components/ComReportServerModal.vue";

export async function viewChannelManagerTaskDetail(title,docname){
    const result = await app.utils.openDialog(ComTaskDetail,title,{
        data: {
            docname: docname
        }
    })
    return result
}

export async function viewChannelManagerTaskList(title){
    const result = await app.utils.openDialog(ComTaskLisk,title)
    return result
}

export async function viewChannelManagerSyncLogData(title,docname){
    const result = await app.utils.openDialog(ComViewSyncData,title,{
        data: {
            docname: docname
        }
    })
    return result
}

export async function viewDataChangeLog(title,docname){
    const result = await app.utils.openDialog(ComViewChangeDataLog,title,{
        data: {
            docname: docname
        }
    })
    return result
}

export async function viewAvailabilityData(title,params={}){
    const result = await app.utils.openDialog(ComViewAvailabilityDataDialog,title,{
        data:  params
    })
    return result
}

export async function viewReport(report_path,report_title,params){
    let data = {
        report_path: report_path,
        params:params
    }
    const result = await app.utils.openDialog(
        ComReportServerModal,
        report_title,
        {
            data:data,
            props: {
               
                style: {
                    width: '90vw',
                    
                },
                position: "top",
                modal: true,
               
                closeOnEscape: true,
                breakpoints:{
                    '960px': '80vw',
                    '640px': '100vw'
                },

            },
        }

    ) 
}