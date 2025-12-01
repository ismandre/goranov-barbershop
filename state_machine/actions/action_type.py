from enum import StrEnum


class ActionType(StrEnum):
    ACTION_USER_MESSAGE = 'ActionUserMessage'
    ACTION_SHOW_AVAILABLE_APPOINTMENTS = 'ActionShowAvailableAppointments'
    ACTION_SHOW_EXISTING_RESERVATIONS = 'ActionShowExistingReservations'
    ACTION_SHOW_NO_RESERVATIONS = 'ActionShowNoReservations'
    ACTION_SELECT_APPOINTMENT = 'ActionSelectAppointment'
    ACTION_CONTINUE = 'ActionContinue'
    ACTION_CANCEL = 'ActionCancel'
    ACTION_BOOK_APPOINTMENT = 'ActionBookAppointment'
