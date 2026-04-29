<template>
  <div>
    <h1 class="text-2xl lg:text-3xl font-bold text-gray-900 mb-6">Kalendar</h1>

    <!-- Calendar Controls -->
    <div class="card mb-6">
      <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div class="flex items-center justify-between sm:justify-start sm:space-x-4">
          <button @click="previousWeek" class="btn btn-secondary p-3">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <h2 class="text-base sm:text-lg lg:text-xl font-semibold text-gray-900 text-center">
            {{ formatWeekRange(currentWeekStart) }}
          </h2>
          <button @click="nextWeek" class="btn btn-secondary p-3">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>
        <button @click="goToToday" class="btn btn-primary text-base py-3 w-full sm:w-auto">
          Danas
        </button>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="card text-center py-12">
      <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      <p class="text-gray-500 mt-4">Učitavanje...</p>
    </div>

    <!-- Mobile View - List -->
    <div v-else class="lg:hidden space-y-3">
      <div
        v-for="(date, index) in currentWeek"
        :key="index"
        class="card"
        :class="{ 'border-2 border-primary-500': isToday(date) }"
      >
        <div class="flex items-center justify-between mb-3 pb-3 border-b">
          <div>
            <div class="text-sm text-gray-600">{{ getDayName(date) }}</div>
            <div class="text-xl font-bold text-gray-900">{{ date.getDate() }} {{ getMonthName(date) }}</div>
          </div>
          <div v-if="isToday(date)" class="text-xs font-semibold text-primary-600 bg-primary-50 px-3 py-1 rounded-full">
            Danas
          </div>
        </div>

        <!-- Appointments for this day -->
        <div v-if="getAppointmentsForDate(date).length > 0" class="space-y-2 mb-3">
          <div
            v-for="appointment in getAppointmentsForDate(date)"
            :key="appointment.id"
            class="p-3 rounded-lg cursor-pointer"
            :class="{
              'bg-green-50 border border-green-200': appointment.status === 'confirmed',
              'bg-yellow-50 border border-yellow-200': appointment.status === 'pending',
              'bg-blue-50 border border-blue-200': appointment.status === 'completed',
              'bg-red-50 border border-red-200': appointment.status === 'cancelled' || appointment.status === 'no_show'
            }"
            @click="showAppointmentDetails(appointment)"
          >
            <div class="flex items-center justify-between mb-1">
              <span class="font-semibold text-gray-900">{{ formatTime(appointment.start_time) }}</span>
              <span :class="`badge badge-${appointment.status} text-xs`">
                {{ getStatusLabel(appointment.status) }}
              </span>
            </div>
            <div class="text-sm text-gray-600">{{ appointment.customer_phone }}</div>
            <div v-if="appointment.customer_name" class="text-sm text-gray-800">{{ appointment.customer_name }}</div>
          </div>
        </div>

        <!-- Available slots for this day -->
        <div v-if="getAvailableSlotsForDate(date).length > 0" class="space-y-2">
          <div class="text-xs font-semibold text-gray-500 uppercase">Slobodni termini</div>
          <div class="flex flex-wrap gap-2">
            <div
              v-for="slot in getAvailableSlotsForDate(date)"
              :key="`slot-${slot.id}`"
              class="px-3 py-1 rounded bg-gray-100 text-gray-700 text-sm"
            >
              {{ formatTime(slot.start_time) }}
            </div>
          </div>
        </div>

        <!-- No appointments or slots -->
        <div v-if="getAppointmentsForDate(date).length === 0 && getAvailableSlotsForDate(date).length === 0" class="text-center py-4 text-gray-400">
          Nema termina
        </div>
      </div>
    </div>

    <!-- Desktop View - Calendar Grid -->
    <div v-else class="card hidden lg:block overflow-x-auto">
      <div class="grid grid-cols-7 gap-px bg-gray-200 min-w-[800px]">
        <!-- Day headers -->
        <div v-for="(day, index) in weekDaysShort" :key="day" class="bg-gray-50 p-3 text-center">
          <div class="text-sm font-semibold text-gray-900">{{ day }}</div>
        </div>

        <!-- Calendar cells -->
        <div
          v-for="(date, index) in currentWeek"
          :key="index"
          class="bg-white min-h-[180px] p-3"
          :class="{ 'bg-blue-50 border-2 border-blue-300': isToday(date) }"
        >
          <div class="flex items-center justify-between mb-2">
            <div class="text-sm font-semibold text-gray-900">{{ date.getDate() }}</div>
            <div v-if="isToday(date)" class="text-xs font-semibold text-blue-600">Danas</div>
          </div>

          <div class="space-y-1">
            <!-- Appointments -->
            <div
              v-for="appointment in getAppointmentsForDate(date)"
              :key="appointment.id"
              class="text-xs p-2 rounded cursor-pointer hover:opacity-80 transition-opacity"
              :class="{
                'bg-green-100 text-green-800 border border-green-200': appointment.status === 'confirmed',
                'bg-yellow-100 text-yellow-800 border border-yellow-200': appointment.status === 'pending',
                'bg-blue-100 text-blue-800 border border-blue-200': appointment.status === 'completed',
                'bg-red-100 text-red-800 border border-red-200': appointment.status === 'cancelled' || appointment.status === 'no_show'
              }"
              @click="showAppointmentDetails(appointment)"
            >
              <div class="font-semibold">{{ formatTime(appointment.start_time) }}</div>
              <div class="truncate">{{ appointment.customer_phone }}</div>
            </div>

            <!-- Available slots -->
            <div
              v-for="slot in getAvailableSlotsForDate(date)"
              :key="`slot-${slot.id}`"
              class="text-xs p-2 rounded bg-gray-100 text-gray-600"
            >
              <div>{{ formatTime(slot.start_time) }}</div>
              <div class="text-xs opacity-75">Dostupno</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Appointment Details Modal -->
    <div
      v-if="selectedAppointment"
      class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4"
      @click="selectedAppointment = null"
    >
      <div class="bg-white rounded-lg p-6 max-w-md w-full" @click.stop>
        <div class="flex justify-between items-start mb-6">
          <h3 class="text-xl font-bold text-gray-900">Detalji termina</h3>
          <button @click="selectedAppointment = null" class="text-gray-400 hover:text-gray-600 p-2">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div class="space-y-4">
          <div class="p-4 bg-gray-50 rounded-lg">
            <label class="text-sm font-semibold text-gray-600 block mb-1">Klijent</label>
            <p class="text-lg font-semibold text-gray-900">{{ selectedAppointment.customer_phone }}</p>
            <p v-if="selectedAppointment.customer_name" class="text-gray-600">
              {{ selectedAppointment.customer_name }}
            </p>
          </div>

          <div class="p-4 bg-gray-50 rounded-lg">
            <label class="text-sm font-semibold text-gray-600 block mb-1">Datum i vrijeme</label>
            <p class="text-lg font-semibold text-gray-900">{{ formatDate(selectedAppointment.start_time) }}</p>
            <p class="text-gray-600">
              {{ formatTime(selectedAppointment.start_time) }} - {{ formatTime(selectedAppointment.end_time) }}
            </p>
          </div>

          <div class="p-4 bg-gray-50 rounded-lg">
            <label class="text-sm font-semibold text-gray-600 block mb-2">Status</label>
            <span :class="`badge badge-${selectedAppointment.status} text-sm`">
              {{ getStatusLabel(selectedAppointment.status) }}
            </span>
          </div>

          <div v-if="selectedAppointment.notes" class="p-4 bg-gray-50 rounded-lg">
            <label class="text-sm font-semibold text-gray-600 block mb-1">Napomena</label>
            <p class="text-gray-900">{{ selectedAppointment.notes }}</p>
          </div>
        </div>

        <div class="mt-6 flex flex-col sm:flex-row gap-3">
          <button @click="selectedAppointment = null" class="btn btn-secondary flex-1 py-3">
            Zatvori
          </button>
          <router-link to="/appointments" class="btn btn-primary flex-1 text-center py-3">
            Svi termini
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminAPI } from '@/api/admin'

const weekDaysShort = ['Ned', 'Pon', 'Uto', 'Sri', 'Čet', 'Pet', 'Sub']
const currentWeekStart = ref(getStartOfWeek(new Date()))
const appointments = ref([])
const availableSlots = ref([])
const loading = ref(false)
const selectedAppointment = ref(null)

const currentWeek = computed(() => {
  const week = []
  for (let i = 0; i < 7; i++) {
    const date = new Date(currentWeekStart.value)
    date.setDate(date.getDate() + i)
    week.push(date)
  }
  return week
})

onMounted(() => {
  loadCalendarData()
})

async function loadCalendarData() {
  loading.value = true
  try {
    const [apptResponse, slotsResponse] = await Promise.all([
      adminAPI.getAppointments(),
      adminAPI.getSlots({ available_only: true })
    ])

    appointments.value = apptResponse.data
    availableSlots.value = slotsResponse.data
  } catch (error) {
    console.error('Failed to load calendar data:', error)
  } finally {
    loading.value = false
  }
}

function getStartOfWeek(date) {
  const d = new Date(date)
  const day = d.getDay()
  const diff = d.getDate() - day
  return new Date(d.setDate(diff))
}

function previousWeek() {
  const newDate = new Date(currentWeekStart.value)
  newDate.setDate(newDate.getDate() - 7)
  currentWeekStart.value = newDate
  loadCalendarData()
}

function nextWeek() {
  const newDate = new Date(currentWeekStart.value)
  newDate.setDate(newDate.getDate() + 7)
  currentWeekStart.value = newDate
  loadCalendarData()
}

function goToToday() {
  currentWeekStart.value = getStartOfWeek(new Date())
  loadCalendarData()
}

function isToday(date) {
  const today = new Date()
  return date.toDateString() === today.toDateString()
}

function isSameDay(date1, date2) {
  return date1.toDateString() === date2.toDateString()
}

function getAppointmentsForDate(date) {
  return appointments.value.filter(appointment => {
    const appointmentDate = new Date(appointment.start_time)
    return isSameDay(appointmentDate, date)
  })
}

function getAvailableSlotsForDate(date) {
  return availableSlots.value.filter(slot => {
    const slotDate = new Date(slot.start_time)
    return isSameDay(slotDate, date)
  }).slice(0, 5)
}

function showAppointmentDetails(appointment) {
  selectedAppointment.value = appointment
}

function formatWeekRange(startDate) {
  const start = new Date(startDate)
  const end = new Date(startDate)
  end.setDate(end.getDate() + 6)

  return `${start.toLocaleDateString('hr-HR', { day: 'numeric', month: 'short' })} - ${end.toLocaleDateString('hr-HR', { day: 'numeric', month: 'short', year: 'numeric' })}`
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('hr-HR', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric'
  })
}

function formatTime(dateString) {
  const date = new Date(dateString)
  return date.toLocaleTimeString('hr-HR', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

function getDayName(date) {
  return date.toLocaleDateString('hr-HR', { weekday: 'long' })
}

function getMonthName(date) {
  return date.toLocaleDateString('hr-HR', { month: 'long' })
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
