<template>
  <section class="panel-card block">
    <h4>核心知识点</h4>
    <pre>{{ archive.key_points || "1. 章节脉络\n2. 关键实现\n3. 复盘节奏" }}</pre>
    <h4>最难的部分</h4>
    <p>{{ archive.difficult_parts || "在每章总结中持续记录并回看。" }}</p>
    <h4>已掌握的部分</h4>
    <p>{{ archive.mastered_parts || "能复述核心概念与流程。" }}</p>
  </section>
</template>

<script setup>
defineProps({
  archive: { type: Object, required: true }
});
</script>

<style scoped>
.block {
  padding: 16px;
}
pre,
p {
  margin: 0 0 12px;
  color: var(--muted);
  white-space: pre-wrap;
}
h4 {
  margin: 0 0 6px;
}
</style>
