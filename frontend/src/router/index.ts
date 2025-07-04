import { createRouter, createWebHistory } from 'vue-router'
import Chat from '../views/Chat.vue'
import FunctionCallingDemo from '../views/FunctionCallingDemo.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      name: 'chat',
      component: Chat
    },
    {
      path: '/function-calling',
      name: 'function-calling',
      component: FunctionCallingDemo
    }
  ]
})

export default router 