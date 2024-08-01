// src/directives/v-interact.js
import interact from 'interactjs';

export default {
  mounted(el, binding) {
    const options = binding.value || {};

    if (options.draggable) {
      interact(el).draggable({
        listeners: {
          move(event) {
            const { target, dx, dy } = event;
            const x = (parseFloat(target.getAttribute('data-x')) || 0) + dx;
            const y = (parseFloat(target.getAttribute('data-y')) || 0) + dy;

            target.style.transform = `translate(${x}px, ${y}px)`;

            target.setAttribute('data-x', x);
            target.setAttribute('data-y', y);
          },
        },
      });
    }

    if (options.resizable) {
      interact(el).resizable({
        edges: { left: true, right: true, bottom: true, top: true },
        listeners: {
          move(event) {
            const { target, rect, deltaRect } = event;

            target.style.width = `${rect.width}px`;
            target.style.height = `${rect.height}px`;

            target.style.transform = `translate(${deltaRect.left}px, ${deltaRect.top}px)`;
          },
        },
      });
    }
  },
};
