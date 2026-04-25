import ComTaskDetail from "@/views/channel_managers/task/ComTaskDetail.vue"
import ComTaskLisk from "@/views/channel_managers/task/ComTaskLisk.vue"

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
