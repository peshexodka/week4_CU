import { onBeforeUnmount, onMounted, ref } from 'vue'

export function useChartWidth(initialWidth) {
  const plot = ref(null)
  const width = ref(initialWidth)
  let observer

  onMounted(() => {
    observer = new ResizeObserver(([entry]) => {
      if (entry.contentRect.width > 0) width.value = entry.contentRect.width
    })
    observer.observe(plot.value)
  })
  onBeforeUnmount(() => observer?.disconnect())

  return { plot, width }
}
