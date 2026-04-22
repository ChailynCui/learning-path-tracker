<template>
  <div class="app-shell">
    <header class="top-nav">
      <h1>Learning Path Tracker</h1>
      <nav>
        <RouterLink to="/">Dashboard</RouterLink>
        <RouterLink to="/paths/new">创建路线</RouterLink>
        <RouterLink to="/archives">归档</RouterLink>
      </nav>
    </header>
    <main class="main-content">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
}

.top-nav {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 30px;
  backdrop-filter: blur(16px);
  background: rgba(255, 255, 255, 0.76);
  border-bottom: 1px solid var(--line);
}

.top-nav h1 {
  font-family: "Space Grotesk", sans-serif;
  margin: 0;
  font-size: 32px;
  letter-spacing: -0.2px;
}

nav {
  display: flex;
  gap: 10px;
  padding: 6px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.72);
}

a {
  color: var(--ink);
  text-decoration: none;
  font-weight: 600;
  padding: 10px 16px;
  border-radius: 999px;
  transition: 0.2s ease;
}

a.router-link-active {
  background: var(--brand);
  color: white;
  box-shadow: 0 6px 16px rgba(15, 118, 110, 0.26);
}

a:hover {
  background: rgba(15, 118, 110, 0.08);
}

.main-content {
  max-width: 1140px;
  margin: 0 auto;
  padding: 28px 20px 56px;
}

@media (max-width: 700px) {
  .top-nav {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
    padding: 14px 16px;
  }

  .top-nav h1 {
    font-size: 28px;
  }
}
</style>
