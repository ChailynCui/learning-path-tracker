<template>
  <section class="panel-card wrap">
    <div class="head">
      <div>
        <h2>{{ path.title }}</h2>
        <div class="meta">
          <span class="tag">{{ path.type === "tutorial" ? "教程学习" : "开源项目学习" }}</span>
          <span class="tag status">{{ path.status === "completed" ? "已完成" : "进行中" }}</span>
        </div>
      </div>
      <div class="progress-mini">
        <strong>{{ path.completed_units }}/{{ path.total_units }}</strong>
        <small>章节进度</small>
      </div>
    </div>

    <a v-if="path.source_url" :href="path.source_url" target="_blank" rel="noreferrer" class="source-link">
      打开项目仓库
    </a>
    <p v-else class="source-empty">来源链接：未填写</p>
  </section>
</template>

<script setup>
defineProps({
  path: {
    type: Object,
    required: true
  }
});
</script>

<style scoped>
.wrap {
  padding: 18px;
  background: linear-gradient(150deg, rgba(255, 255, 255, 0.98), rgba(15, 118, 110, 0.06));
}
h2 {
  margin: 0;
  font-size: 30px;
  line-height: 1.12;
}

.head {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: flex-start;
}

.meta {
  margin-top: 10px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.tag {
  font-size: 12px;
  color: var(--muted);
  border-radius: 999px;
  border: 1px solid rgba(25, 52, 65, 0.14);
  background: rgba(255, 255, 255, 0.72);
  padding: 4px 10px;
}

.status {
  color: #0b5f58;
  border-color: rgba(15, 118, 110, 0.32);
  background: rgba(15, 118, 110, 0.11);
}

.progress-mini {
  text-align: right;
  min-width: 100px;
}

.progress-mini strong {
  display: block;
  font-family: "Space Grotesk", sans-serif;
  font-size: 28px;
  line-height: 1;
}

.progress-mini small {
  color: var(--muted);
}

.source-link,
.source-empty {
  margin-top: 14px;
}

.source-link {
  display: inline-flex;
  color: #0b5f58;
  font-weight: 600;
  text-decoration: none;
  border-bottom: 1px dashed rgba(11, 95, 88, 0.44);
}

.source-link:hover {
  color: #0f766e;
}

.source-empty {
  color: var(--muted);
}

@media (max-width: 640px) {
  h2 {
    font-size: 25px;
  }

  .head {
    flex-direction: column;
  }

  .progress-mini {
    text-align: left;
  }
}
</style>
