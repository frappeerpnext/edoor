<template>
  <div @contextmenu="onOpenMenu" style="height: 100%; width: 100%">
    <template v-if="room.element">
      <div
        style="height: 100%; width: 100%"
        class="floor-plan-element"
        @click="toggle"
        v-html="room.element"
      ></div>
    </template>
    <template v-else>
      <div class="room-floor-plan h-full w-full text-lg">
      {{ room.room_type_alias }} - {{ room.room_number }}
      </div>
    </template>
  </div>

  <ContextMenu ref="menu" :model="contextMenuItems" />

  <OverlayPanel
    ref="op"
    class="style_panel bg-white p-4 rounded-lg shadow-lg max-w-md w-full"
  >
    <InputText type="text" v-model="elementStyle.elementText" />

    <p>
      TextTransform:
      <ComSelect
        v-model="elementStyle.textTransform"
        :options="['none', 'uppercase', 'lowercase', 'capitalize']"
      />
    </p>

    <p>
      Text Effect:
      <ComSelect
        v-model="elementStyle.textEffect"
        :options="['none', 'rotate']"
      />
    </p>
    <p v-if="elementStyle.textEffect === 'rotate'">
      Rotate Degree
      <Slider
        v-model="elementStyle.rotateDegree"
        :min="0"
        :max="360"
        class="w-56"
      />
    </p>

    <p>
      Font Size
      <Slider
        v-model="elementStyle.fontSize"
        :min="10"
        :max="30"
        class="w-56 my-2"
      />
    </p>
    <p>
      Text Color:
      <div class="w-3rem h-3rem rounded-lg border-1" style="border-color: #a0bde0;"
      @click="toggleColor($event , 'color')" :style="{ background: elementStyle.color }"></div>
    </p>
    <p>
      Background Color:
      <div class="w-3rem h-3rem rounded-lg border-1" style="border-color: #a0bde0;"
      @click="toggleColor($event , 'background')" :style="{ background: elementStyle.background }"></div>
    </p>
    <p>
      Border Color:
      <div class="w-3rem h-3rem rounded-lg border-1" style="border-color: #a0bde0;"
      @click="toggleColor($event , 'borderColor')" :style="{ background: elementStyle.borderColor }"></div>
    </p>
    <p class="my-2">
      Border Width:
      <Slider
        v-model="elementStyle.borderWidth"
        :min="1"
        :max="10"
        class="w-56"
      />
    </p>
    <p>
      Justify Content:
      <ComSelect
        v-model="elementStyle.justifyContent"
        :options="['left', 'center', 'right', 'start', 'end']"
      />
    </p>
    <p>
      Align Items:
      <ComSelect
        v-model="elementStyle.alignItems"
        :options="['start', 'center', 'end']"
      />
    </p>

    <OverlayPanel ref="overlay">
            <ComColorPicker v-if="overlayName == 'color'" v-model="elementStyle.color" />
            <ComColorPicker v-if="overlayName == 'background'" v-model="elementStyle.background" />
            <ComColorPicker v-if="overlayName == 'borderColor'" v-model="elementStyle.borderColor" />
    </OverlayPanel>
  </OverlayPanel>
</template>

<script setup>
import { ref, watch, defineEmits, defineProps } from "vue";
import { i18n } from "@/i18n";
import ContextMenu from "primevue/contextmenu";
import ColorPicker from "primevue/colorpicker";
import Slider from "primevue/slider";

const op = ref();
const overlayName = ref("");
const emit = defineEmits(["onDelete"]);
const { t: $t } = i18n.global;

const props = defineProps({
  room: Object,
});
const overlay = ref();
const toggleColor = ($event,NameEvent) => {
    overlayName.value = NameEvent
    overlay.value.toggle($event);
}
const menu = ref();
const elementStyle = ref({
  color: "000000",
  background: "ffffff",
  borderColor: "000000",
  justifyContent: "center",
  fontSize: 10,
  alignItems: "center",
  borderWidth: 1,
  rotateDegree: 0,
  textEffect: "none",
  textTransform: "none",
  elementText: "",
});

let element = null;

const toggle = (event) => {
  const activeElement = document.querySelector(
    ".drv-active .floor-plan-element div"
  );
  if (activeElement) {
    element = activeElement;
    const computedStyles = window.getComputedStyle(element);

    Object.keys(elementStyle.value).forEach((key) => {
      if (key === "color" || key === "background" || key === "borderColor") {
        elementStyle.value[key] = computedStyles[key].replace("#", "");
      } else if (key === "borderWidth" || key === "fontSize") {
        elementStyle.value[key] = computedStyles[key].replace("px", "");
      } else if (key === "rotateDegree") {
        elementStyle.value[key] =
          computedStyles.transform.match(/rotate\((\d+)deg\)/)?.[1] || 0;
      } else if (key !== "elementText") {
        elementStyle.value[key] = computedStyles[key];
      }
    });
    elementStyle.value.elementText = element.textContent;
    op.value.toggle(event);
  }
};

const contextMenuItems = ref([
  {
    label: $t("Send to Back"),
    icon: "pi pi-angle-double-down",
    command: () => {
      if ((props.room.z_index || 0) > 0) {
        props.room.z_index -= 1;
      }
    },
  },
  {
    label: $t("Bring to Front"),
    icon: "pi pi-angle-double-up",
    command: () => {
      props.room.z_index = (props.room.z_index || 0) + 1;
    },
  },
]);

if (props.room.element) {
  contextMenuItems.value.push({
    label: $t("Delete"),
    icon: "pi pi-trash",
    command: () => {
      props.room.is_deleted = 1;
    },
  });
}

watch(elementStyle.value, () => {
  console.log(elementStyle.value.color)
  if (element) {
    Object.keys(elementStyle.value).forEach((key) => {
      if (key === "borderWidth" || key === "fontSize") {
        element.style[key] = `${elementStyle.value[key]}px`;
      } else if (key === "rotateDegree") {
        element.style.transform = `rotate(${elementStyle.value[key]}deg)`;
      } else if (key === "elementText") {
        element.textContent = elementStyle.value[key];
      } else {
        element.style[key] = elementStyle.value[key];
      }
    });
    props.room.element = element.outerHTML;
  }
});

const onOpenMenu = (event) => {
  menu.value.show(event);
};
</script>
