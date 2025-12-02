USER_STATES = {}

def handle_state_transition(user: str, message: str) -> str:
    state = USER_STATES.get(user, "START")

    if state == "START":
        USER_STATES[user] = "ASK_DATE"
        return "Bok! 👋 Kada želiš termin za šišanje? (npr. 'sutra u 5')"

    elif state == "ASK_DATE":
        USER_STATES[user] = "CONFIRM"
        return f"Super! Želiš li potvrditi termin: {message}? (da / ne)"

    elif state == "CONFIRM":
        if message.lower().strip() == "da":
            USER_STATES[user] = "END"
            return "Termin je potvrđen! Vidimo se 💈✂️"
        else:
            USER_STATES[user] = "START"
            return "Nema problema. Želiš li probati rezervirati drugi termin?"

    return "Nešto nije u redu 🤔"
