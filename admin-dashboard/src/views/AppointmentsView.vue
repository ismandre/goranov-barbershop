<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-6 gap-4">
      <h1 class="text-2xl lg:text-3xl font-bold text-gray-900">Termini</h1>
      <button @click="loadAppointments" class="btn btn-secondary w-full sm:w-auto">
        <svg class="w-5 h-5 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        Osvježi
      </button>
    </div>

    <!-- Filters -->
    <div class="card mb-6">
      <h2 class="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <svg class="w-5 h-5 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
        </svg>
        Filteri
      </h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        <div>
          <label class="label text-base">Datum</label>
          <input v-model="filters.date" type="date" class="input text-base" />
        </div>
        <div>
          <label class="label text-base">Status</label>
          <select v-model="filters.status" class="input text-base">
            <option value="">Svi statusi</option>
            <option value="pending">Na čekanju</option>
            <option value="confirmed">Potvrđeno</option>
            <option value="completed">Završeno</option>
            <option value="cancelled">Otkazano</option>
            <option value="no_show">Nije se pojavio</option>
          </select>
        </div>
        <div class="flex items-end">
          <button @click="applyFilters" class="btn btn-primary w-full text-base py-3">
            Primijeni
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="card text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="text-gray-500 mt-4">Učitavanje...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="appointments.length === 0" class="card text-center py-12">
      <svg class="w-20 h-20 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
      </svg>
      <p class="text-gray-500 text-lg">Nema termina</p>
      <p class="text-gray-400 text-sm mt-2">Pokušajte promijeniti filtere</p>
    </div>

    <!-- Mobile View - Cards -->
    <div v-else class="lg:hidden space-y-4">
      <div
        v-for="appointment in appointments"
        :key="appointment.id"
        class="card"
      >
        <!-- Status Badge -->
        <div class="flex justify-between items-start mb-3">
          <span :class="`badge badge-${appointment.status} text-sm`">
            {{ getStatusLabel(appointment.status) }}
          </span>
          <span class="text-xs text-gray-500">{{ formatDate(appointment.booked_at) }}</span>
        </div>

        <!-- Customer Info -->
        <div class="mb-4">
          <div class="flex items-center mb-2">
            <svg class="w-5 h-5 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            <span class="font-semibold text-gray-900">{{ appointment.customer_name || 'Nepoznato' }}</span>
          </div>
          <div class="flex items-center text-gray-600">
            <svg class="w-5 h-5 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
            </svg>
            <span>{{ appointment.customer_phone }}</span>
          </div>
        </div>

        <!-- DateTime Info -->
        <div class="mb-4 p-3 bg-gray-50 rounded-lg">
          <div class="flex items-center mb-1">
            <svg class="w-5 h-5 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span class="font-medium text-gray-900">{{ formatDate(appointment.start_time) }}</span>
          </div>
          <div class="flex items-center text-gray-700">
            <svg class="w-5 h-5 text-gray-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{{ formatTime(appointment.start_time) }} - {{ formatTime(appointment.end_time) }}</span>
          </div>
        </div>

        <!-- Status Update -->
        <div>
          <label class="label text-sm mb-2">Promijeni status</label>
          <select
            :value="appointment.status"
            @change="updateStatus(appointment.id, $event.target.value)"
            class="input text-base w-full"
          >
            <option value="pending">Na čekanju</option>
            <option value="confirmed">Potvrđeno</option>
            <option value="completed">Završeno</option>
            <option value="cancelled">Otkazano</option>
            <option value="no_show">Nije se pojavio</option>
          </select>
        </div>
      </div>
    </div>

    <!-- Desktop View - Table -->
    <div v-else class="card hidden lg:block">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Klijent</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Datum i vrijeme</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Status</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Rezervirano</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase tracking-wider">Akcija</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="appointment in appointments" :key="appointment.id" class="hover:bg-gray-50">
              <td class="px-6 py-4">
                <div>
                  <div class="text-sm font-semibold text-gray-900">{{ appointment.customer_name || 'Nepoznato' }}</div>
                  <div class="text-sm text-gray-500">{{ appointment.customer_phone }}</div>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900">{{ formatDate(appointment.start_time) }}</div>
                <div class="text-sm text-gray-500">{{ formatTime(appointment.start_time) }} - {{ formatTime(appointment.end_time) }}</div>
              </td>
              <td class="px-6 py-4">
                <span :class="`badge badge-${appointment.status}`">
                  {{ getStatusLabel(appointment.status) }}
                </span>
              </td>
              <td class="px-6 py-4 text-sm text-gray-500">
                {{ formatDate(appointment.booked_at) }}
              </td>
              <td class="px-6 py-4">
                <select
                  :value="appointment.status"
                  @change="updateStatus(appointment.id, $event.target.value)"
                  class="text-sm border-gray-300 rounded-md"
                >
                  <option value="pending">Na čekanju</option>
                  <option value="confirmed">Potvrđeno</option>
                  <option value="completed">Završeno</option>
                  <option value="cancelled">Otkazano</option>
                  <option value="no_show">Nije se pojavio</option>
                </select>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/api/admin'

const appointments = ref([])
const loading = ref(false)
const filters = ref({
  date: '',
  status: ''
})

onMounted(() => {
  loadAppointments()
})

async function loadAppointments() {
  loading.value = true
  try {
    const params = {}
    if (filters.value.date) params.date = filters.value.date
    if (filters.value.status) params.status = filters.value.status

    const response = await adminAPI.getAppointments(params)
    appointments.value = response.data
  } catch (error) {
    console.error('Failed to load appointments:', error)
  } finally {
    loading.value = false
  }
}

function applyFilters() {
  loadAppointments()
}

async function updateStatus(appointmentId, newStatus) {
  try {
    await adminAPI.updateAppointmentStatus(appointmentId, newStatus)
    await loadAppointments()
  } catch (error) {
    console.error('Failed to update status:', error)
    alert('Greška pri ažuriranju statusa')
  }
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('hr-HR', {
    weekday: 'short',
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

function formatTime(dateString) {
  const date = new Date(dateString)
  return date.toLocaleTimeString('hr-HR', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getStatusLabel(status) {
  const labels = {
    'pending': 'Na čekanju',
    'confirmed': 'Potvrđeno',
    'completed': 'Završeno',
    'cancelled': 'Otkazano',
    'no_show': 'Nije se pojavio'
  }
  return labels[status] || status
}
</script>
