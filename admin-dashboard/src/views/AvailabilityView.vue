<template>
  <div>
    <h1 class="text-2xl lg:text-3xl font-bold text-gray-900 mb-6">Dostupnost</h1>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
      <!-- Add Single Slot -->
      <div class="card">
        <h2 class="text-lg lg:text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <svg class="w-6 h-6 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Dodaj jedan termin
        </h2>
        <form @submit.prevent="addSingleSlot" class="space-y-4">
          <div>
            <label class="label text-base">Datum</label>
            <input v-model="newSlot.date" type="date" class="input text-base" required />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label text-base">Početak</label>
              <input v-model="newSlot.startTime" type="time" class="input text-base" required />
            </div>
            <div>
              <label class="label text-base">Kraj</label>
              <input v-model="newSlot.endTime" type="time" class="input text-base" required />
            </div>
          </div>

          <button type="submit" class="btn btn-primary w-full text-base py-3" :disabled="addingSlot">
            <span v-if="addingSlot" class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Dodavanje...
            </span>
            <span v-else>Dodaj termin</span>
          </button>
        </form>
      </div>

      <!-- Bulk Add Slots -->
      <div class="card">
        <h2 class="text-lg lg:text-xl font-semibold text-gray-900 mb-4 flex items-center">
          <svg class="w-6 h-6 mr-2 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
          </svg>
          Dodaj više termina
        </h2>
        <form @submit.prevent="addBulkSlots" class="space-y-4">
          <div>
            <label class="label text-base">Datum</label>
            <input v-model="bulkSlot.date" type="date" class="input text-base" required />
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="label text-base">Od sata</label>
              <input v-model.number="bulkSlot.startHour" type="number" min="0" max="23" class="input text-base" required />
            </div>
            <div>
              <label class="label text-base">Do sata</label>
              <input v-model.number="bulkSlot.endHour" type="number" min="0" max="23" class="input text-base" required />
            </div>
          </div>

          <div>
            <label class="label text-base">Trajanje termina</label>
            <select v-model.number="bulkSlot.duration" class="input text-base">
              <option :value="15">15 minuta</option>
              <option :value="30">30 minuta</option>
              <option :value="45">45 minuta</option>
              <option :value="60">60 minuta</option>
            </select>
          </div>

          <div class="bg-blue-50 border-2 border-blue-200 p-4 rounded-lg">
            <div class="flex items-start">
              <svg class="w-5 h-5 text-blue-600 mr-2 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p class="text-sm text-blue-800">
                Kreiraće se <strong>{{ calculateSlotsCount() }} termina</strong> od {{ bulkSlot.startHour }}:00 do {{ bulkSlot.endHour }}:00
              </p>
            </div>
          </div>

          <button type="submit" class="btn btn-primary w-full text-base py-3" :disabled="addingBulk">
            <span v-if="addingBulk" class="flex items-center justify-center">
              <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Dodavanje...
            </span>
            <span v-else>Dodaj {{ calculateSlotsCount() }} termina</span>
          </button>
        </form>
      </div>
    </div>

    <!-- Existing Slots -->
    <div class="card mt-6">
      <div class="flex flex-col lg:flex-row lg:justify-between lg:items-center mb-6 gap-4">
        <h2 class="text-lg lg:text-xl font-semibold text-gray-900 flex items-center">
          <svg class="w-6 h-6 mr-2 text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          Postojeći termini
        </h2>
        <div class="flex flex-col sm:flex-row gap-3">
          <label class="flex items-center px-4 py-2 bg-gray-50 rounded-lg">
            <input v-model="showOnlyAvailable" type="checkbox" class="mr-2 w-4 h-4" />
            <span class="text-sm font-medium">Samo slobodni</span>
          </label>
          <input v-model="filterDate" type="date" class="input text-sm" />
          <button @click="loadSlots" class="btn btn-secondary">
            <svg class="w-4 h-4 mr-2 inline" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Osvježi
          </button>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loadingSlots" class="text-center py-12">
        <div class="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        <p class="text-gray-500 mt-4">Učitavanje...</p>
      </div>

      <!-- Empty State -->
      <div v-else-if="slots.length === 0" class="text-center py-12">
        <svg class="w-20 h-20 mx-auto text-gray-300 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
        </svg>
        <p class="text-gray-500 text-lg">Nema termina</p>
        <p class="text-gray-400 text-sm mt-2">Dodajte nove termine gore</p>
      </div>

      <!-- Mobile View - Cards -->
      <div v-else class="lg:hidden space-y-3">
        <div
          v-for="slot in slots"
          :key="slot.id"
          class="p-4 border rounded-lg"
          :class="slot.is_booked ? 'bg-red-50 border-red-200' : 'bg-green-50 border-green-200'"
        >
          <div class="flex justify-between items-start mb-3">
            <div>
              <div class="text-sm text-gray-600">{{ formatDate(slot.start_time) }}</div>
              <div class="text-lg font-bold text-gray-900">
                {{ formatTime(slot.start_time) }} - {{ formatTime(slot.end_time) }}
              </div>
              <div class="text-sm text-gray-600 mt-1">{{ calculateDuration(slot.start_time, slot.end_time) }} min</div>
            </div>
            <span v-if="slot.is_booked" class="badge bg-red-100 text-red-800 text-sm">Zauzeto</span>
            <span v-else class="badge bg-green-100 text-green-800 text-sm">Slobodno</span>
          </div>
          <button
            v-if="!slot.is_booked"
            @click="deleteSlot(slot.id)"
            class="btn btn-danger w-full text-sm py-2"
          >
            Obriši termin
          </button>
          <div v-else class="text-center text-sm text-gray-500 py-2">
            Ne može se obrisati rezerviran termin
          </div>
        </div>
      </div>

      <!-- Desktop View - Table -->
      <div v-else class="overflow-x-auto hidden lg:block">
        <table class="w-full">
          <thead class="bg-gray-50 border-b border-gray-200">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">ID</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Datum i vrijeme</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Trajanje</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Status</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-700 uppercase">Akcija</th>
            </tr>
          </thead>
          <tbody class="bg-white divide-y divide-gray-200">
            <tr v-for="slot in slots" :key="slot.id" class="hover:bg-gray-50">
              <td class="px-6 py-4 text-sm text-gray-900">{{ slot.id }}</td>
              <td class="px-6 py-4">
                <div class="text-sm font-medium text-gray-900">{{ formatDate(slot.start_time) }}</div>
                <div class="text-sm text-gray-500">{{ formatTime(slot.start_time) }} - {{ formatTime(slot.end_time) }}</div>
              </td>
              <td class="px-6 py-4 text-sm text-gray-700 font-medium">
                {{ calculateDuration(slot.start_time, slot.end_time) }} min
              </td>
              <td class="px-6 py-4">
                <span v-if="slot.is_booked" class="badge bg-red-100 text-red-800">Zauzeto</span>
                <span v-else class="badge bg-green-100 text-green-800">Slobodno</span>
              </td>
              <td class="px-6 py-4">
                <button
                  v-if="!slot.is_booked"
                  @click="deleteSlot(slot.id)"
                  class="text-red-600 hover:text-red-800 text-sm font-semibold"
                >
                  Obriši
                </button>
                <span v-else class="text-gray-400 text-sm">Ne može se obrisati</span>
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

const newSlot = ref({
  date: '',
  startTime: '09:00',
  endTime: '09:30'
})

const bulkSlot = ref({
  date: '',
  startHour: 9,
  endHour: 17,
  duration: 30
})

const slots = ref([])
const loadingSlots = ref(false)
const addingSlot = ref(false)
const addingBulk = ref(false)
const showOnlyAvailable = ref(false)
const filterDate = ref('')

onMounted(() => {
  loadSlots()
  const today = new Date().toISOString().split('T')[0]
  newSlot.value.date = today
  bulkSlot.value.date = today
  filterDate.value = today
})

async function loadSlots() {
  loadingSlots.value = true
  try {
    const params = {}
    if (showOnlyAvailable.value) params.available_only = true
    if (filterDate.value) params.date = filterDate.value

    const response = await adminAPI.getSlots(params)
    slots.value = response.data
  } catch (error) {
    console.error('Failed to load slots:', error)
  } finally {
    loadingSlots.value = false
  }
}

async function addSingleSlot() {
  addingSlot.value = true
  try {
    const startDateTime = `${newSlot.value.date}T${newSlot.value.startTime}:00`
    const endDateTime = `${newSlot.value.date}T${newSlot.value.endTime}:00`

    await adminAPI.createSlot({
      start_time: startDateTime,
      end_time: endDateTime
    })

    alert('Termin uspješno dodan!')
    await loadSlots()
  } catch (error) {
    console.error('Failed to add slot:', error)
    alert('Greška pri dodavanju termina: ' + (error.response?.data?.detail || error.message))
  } finally {
    addingSlot.value = false
  }
}

async function addBulkSlots() {
  addingBulk.value = true
  try {
    const slotsToCreate = []
    let currentHour = bulkSlot.value.startHour
    let currentMinute = 0

    while (currentHour < bulkSlot.value.endHour ||
           (currentHour === bulkSlot.value.endHour && currentMinute === 0)) {
      const startTime = `${currentHour.toString().padStart(2, '0')}:${currentMinute.toString().padStart(2, '0')}`

      currentMinute += bulkSlot.value.duration
      if (currentMinute >= 60) {
        currentHour += Math.floor(currentMinute / 60)
        currentMinute = currentMinute % 60
      }

      if (currentHour > bulkSlot.value.endHour) break

      const endTime = `${currentHour.toString().padStart(2, '0')}:${currentMinute.toString().padStart(2, '0')}`

      slotsToCreate.push({
        start_time: `${bulkSlot.value.date}T${startTime}:00`,
        end_time: `${bulkSlot.value.date}T${endTime}:00`
      })
    }

    for (const slot of slotsToCreate) {
      await adminAPI.createSlot(slot)
    }

    alert(`Uspješno kreirano ${slotsToCreate.length} termina!`)
    await loadSlots()
  } catch (error) {
    console.error('Failed to add bulk slots:', error)
    alert('Greška pri dodavanju termina: ' + (error.response?.data?.detail || error.message))
  } finally {
    addingBulk.value = false
  }
}

async function deleteSlot(slotId) {
  if (!confirm('Jeste li sigurni da želite obrisati ovaj termin?')) return

  try {
    await adminAPI.deleteSlot(slotId)
    alert('Termin uspješno obrisan!')
    await loadSlots()
  } catch (error) {
    console.error('Failed to delete slot:', error)
    alert('Greška pri brisanju termina: ' + (error.response?.data?.detail || error.message))
  }
}

function calculateSlotsCount() {
  if (!bulkSlot.value.startHour || !bulkSlot.value.endHour || !bulkSlot.value.duration) {
    return 0
  }
  const totalMinutes = (bulkSlot.value.endHour - bulkSlot.value.startHour) * 60
  return Math.floor(totalMinutes / bulkSlot.value.duration)
}

function formatDate(dateString) {
  const date = new Date(dateString)
  return date.toLocaleDateString('hr-HR', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
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

function calculateDuration(start, end) {
  const startDate = new Date(start)
  const endDate = new Date(end)
  return Math.round((endDate - startDate) / 1000 / 60)
}
</script>
