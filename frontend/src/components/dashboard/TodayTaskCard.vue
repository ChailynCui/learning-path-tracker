<template>
  <section class="panel-card card">
    <h3>今日任务：学习 1 个 Chapter</h3>
    <p v-if="task.path_title">
      {{ task.path_title }} · {{ task.unit_title }}
    </p>
    <p v-else>今天还没有任务，先创建一条学习路线。</p>
    <p v-if="task.unit_count > 1" class="tip">今日任务包含 {{ task.unit_count }} 章，请进入详情逐章完成。</p>
    <div class="actions">
      <el-button type="primary" :disabled="!task.path_id" @click="$emit('continue', task.path_id)">
        继续学习
      </el-button>
      <el-button :disabled="!task.path_id || !task.unit_id || task.unit_count > 1" @click="$emit('complete', task)">
        标记完成
      </el-button>
    </div>
  </section>
</template>

<script setup>
defineProps({
  task: {
    type: Object,
    default: () => ({})
  }
});

defineEmits(["continue", "complete"]);
</script>

<style scoped>
.card {
  padding: 18px 20px;
  margin-bottom: 16px;
  border-left: 5px solid var(--brand);
  background:
    linear-gradient(145deg, rgba(255, 255, 255, 0.98), rgba(226, 240, 255, 0.6));
}
h3 {
  margin: 0 0 8px;
  font-size: 24px;
  letter-spacing: -0.2px;
}
p {
  margin: 0;
  color: var(--muted);
  font-size: 16px;
}
.tip {
  margin-top: 8px;
  font-size: 13px;
}
.actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
</style>
