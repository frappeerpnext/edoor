import { createApp, h } from "vue"
import LoadingModal from "@/components/ComLoading.vue"

let instance = null

export function setupLoading() {
  const div = document.createElement("div")
  document.body.appendChild(div)

  const app = createApp({
    render() {
      return h(LoadingModal, {
        ref: (el) => (instance = el)
      })
    }
  })

  app.mount(div)

  window.showLoading = async (message = "Loading...") => {
    instance.open(message)

    return {
      close() {
        instance.close()
      }
    }
  }
}