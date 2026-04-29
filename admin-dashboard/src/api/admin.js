import apiClient from './client'

export const adminAPI = {
  // Stats
  getStats() {
    return apiClient.get('/admin/stats')
  },

  // Appointments
  getAppointments(params = {}) {
    return apiClient.get('/admin/appointments', { params })
  },

  updateAppointmentStatus(appointmentId, status) {
    return apiClient.patch(`/admin/appointments/${appointmentId}`, { status })
  },

  // Slots
  getSlots(params = {}) {
    return apiClient.get('/admin/slots', { params })
  },

  createSlot(slotData) {
    return apiClient.post('/admin/slots', slotData)
  },

  deleteSlot(slotId) {
    return apiClient.delete(`/admin/slots/${slotId}`)
  }
}
