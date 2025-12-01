from actions.action_book_appointment import ActionBookAppointment
from actions.action_select_appointment import ActionSelectAppointment
from actions.action_show_available_appointments import ActionShowAvailableAppointments
from actions.action_user_message import ActionUserMessage
from states.state_user_unknown import StateUserUnknown

if __name__ == '__main__':
    state = StateUserUnknown()
    state = state.on_action(ActionUserMessage())
    state = state.on_action(ActionShowAvailableAppointments())
    state = state.on_action(ActionSelectAppointment())
    state = state.on_action(ActionBookAppointment())
    state = state.on_action(ActionUserMessage())


