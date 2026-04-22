<template>
  <article class="panel-card path-card">
    <div class="head">
      <h4>{{ route.title }}</h4>
      <span>{{ route.type === "tutorial" ? "教程学习" : "开源项目学习" }}</span>
    </div>
    <el-progress :percentage="route.progress" />
    <p>下一章：{{ route.next_unit || "已完成" }}</p>
    <p>进度：{{ route.completed_units }} / {{ route.total_units }}</p>
    <el-button size="small" @click="$emit('detail', route.id)">进入详情</el-button>
  </article>
</template>

<script setup>
defineProps({
  route: {
    type: Object,
    required: true
  }
});

defineEmits(["detail"]);
</script>

<style scoped>
.path-card {
  padding: 16px;
  display: grid;
  gap: 8px;
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.95), rgba(255, 247, 234, 0.66));
}
.head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}
h4 {
  margin: 0;
  font-size: 23px;
}

span {
  font-size: 12px;
  font-weight: 700;
  color: #6b4f14;
  background: rgba(246, 220, 163, 0.45);
  border-radius: 999px;
  padding: 5px 10px;
}
p {
  margin: 0;
  color: var(--muted);
}
</style>
