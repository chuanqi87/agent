<template>
  <div id="app" class="min-h-screen bg-gray-50">
    <!-- 导航栏 -->
    <nav class="bg-white shadow-sm border-b border-gray-200">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-semibold text-gray-900">AI Agent</h1>
          </div>
          <div class="flex items-center space-x-4">
            <router-link 
              to="/" 
              class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="$route.name === 'chat' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'"
            >
              💬 聊天
            </router-link>
            <router-link 
              to="/function-calling" 
              class="px-3 py-2 rounded-md text-sm font-medium transition-colors"
              :class="$route.name === 'function-calling' ? 'bg-blue-100 text-blue-700' : 'text-gray-500 hover:text-gray-700'"
            >
              🔧 Function Calling
            </router-link>
          </div>
        </div>
      </div>
    </nav>

    <!-- 主内容区域 -->
    <main class="flex-1">
      <router-view />
    </main>
  </div>
</template>

<script setup lang="ts">
// 根组件逻辑
</script>

<style>
/* 全局样式 */
</style> 