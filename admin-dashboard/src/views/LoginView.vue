<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-primary-100 px-4">
    <div class="card max-w-md w-full">
      <div class="text-center mb-8">
        <div class="text-5xl mb-3">💈</div>
        <h1 class="text-2xl lg:text-3xl font-bold text-gray-900">Goranov</h1>
        <p class="text-gray-600 mt-2">Frizerski salon</p>
      </div>

      <form @submit.prevent="handleLogin" class="space-y-5">
        <div>
          <label class="label text-base">Korisničko ime</label>
          <input
            v-model="username"
            type="text"
            class="input text-base"
            placeholder="barber"
            required
            autocomplete="username"
          />
        </div>

        <div>
          <label class="label text-base">Lozinka</label>
          <input
            v-model="password"
            type="password"
            class="input text-base"
            placeholder="••••••••"
            required
            autocomplete="current-password"
          />
        </div>

        <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
          {{ error }}
        </div>

        <button
          type="submit"
          class="btn btn-primary w-full text-base py-3"
          :disabled="loading"
        >
          <span v-if="loading" class="flex items-center justify-center">
            <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Prijava u tijeku...
          </span>
          <span v-else>Prijavi se</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const username = ref('barber')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  loading.value = true
  error.value = ''

  try {
    await authStore.login(username.value, password.value)
    router.push('/')
  } catch (err) {
    error.value = err.response?.data?.detail || 'Prijava neuspješna. Provjerite korisničko ime i lozinku.'
  } finally {
    loading.value = false
  }
}
</script>
