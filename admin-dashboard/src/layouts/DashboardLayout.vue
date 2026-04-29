<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Mobile Header -->
    <header class="lg:hidden fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-50">
      <div class="flex items-center justify-between p-4">
        <h1 class="text-lg font-bold text-gray-900">💈 Goranov</h1>
        <button
          @click="mobileMenuOpen = !mobileMenuOpen"
          class="p-2 text-gray-600 hover:text-gray-900"
        >
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path v-if="!mobileMenuOpen" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </header>

    <!-- Sidebar / Mobile Menu -->
    <aside
      class="fixed inset-y-0 left-0 w-64 bg-white border-r border-gray-200 transform transition-transform duration-200 ease-in-out z-40"
      :class="{
        'lg:translate-x-0': true,
        '-translate-x-full': !mobileMenuOpen,
        'translate-x-0': mobileMenuOpen
      }"
    >
      <div class="flex flex-col h-full">
        <!-- Logo -->
        <div class="p-6 border-b border-gray-200 mt-16 lg:mt-0">
          <h1 class="text-xl font-bold text-gray-900">💈 Goranov</h1>
          <p class="text-sm text-gray-600">Frizerski salon</p>
        </div>

        <!-- Navigation -->
        <nav class="flex-1 p-4 space-y-2">
          <router-link
            to="/"
            @click="closeMobileMenu"
            class="nav-item"
            :class="{ 'nav-item-active': $route.name === 'Dashboard' }"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            <span class="text-base">Početna</span>
          </router-link>

          <router-link
            to="/appointments"
            @click="closeMobileMenu"
            class="nav-item"
            :class="{ 'nav-item-active': $route.name === 'Appointments' }"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
            <span class="text-base">Termini</span>
          </router-link>

          <router-link
            to="/calendar"
            @click="closeMobileMenu"
            class="nav-item"
            :class="{ 'nav-item-active': $route.name === 'Calendar' }"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span class="text-base">Kalendar</span>
          </router-link>

          <router-link
            to="/availability"
            @click="closeMobileMenu"
            class="nav-item"
            :class="{ 'nav-item-active': $route.name === 'Availability' }"
          >
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="text-base">Dostupnost</span>
          </router-link>
        </nav>

        <!-- User menu -->
        <div class="p-4 border-t border-gray-200">
          <div class="flex items-center justify-between">
            <div class="flex items-center space-x-3">
              <div class="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center text-white font-medium text-lg">
                {{ admin?.username?.[0]?.toUpperCase() || 'A' }}
              </div>
              <span class="text-sm font-medium text-gray-700">{{ admin?.username || 'Admin' }}</span>
            </div>
            <button
              @click="handleLogout"
              class="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
              title="Odjavi se"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </aside>

    <!-- Mobile Menu Overlay -->
    <div
      v-if="mobileMenuOpen"
      @click="closeMobileMenu"
      class="fixed inset-0 bg-black bg-opacity-50 z-30 lg:hidden"
    ></div>

    <!-- Main content -->
    <main class="lg:ml-64 pt-16 lg:pt-0 p-4 lg:p-8">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const mobileMenuOpen = ref(false)

const admin = computed(() => authStore.admin)

onMounted(() => {
  if (!authStore.admin) {
    authStore.loadAdminInfo()
  }
})

function handleLogout() {
  authStore.logout()
  router.push('/login')
}

function closeMobileMenu() {
  mobileMenuOpen.value = false
}
</script>

<style scoped>
.nav-item {
  @apply flex items-center space-x-3 px-4 py-3 text-gray-700 rounded-lg hover:bg-gray-100 transition-colors;
  min-height: 48px; /* Touch-friendly size */
}

.nav-item-active {
  @apply bg-primary-50 text-primary-700 font-semibold;
}
</style>
