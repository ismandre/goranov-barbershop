"""Croatian message templates for bot responses."""

from datetime import datetime
from typing import List

from app.database.models import AvailableSlot, Appointment


class Messages:
    """Message templates in Croatian."""

    @staticmethod
    def welcome() -> str:
        """Welcome message for new users."""
        return (
            "Bok! 👋 Dobrodošli u Goranov Barbershop.\n\n"
            "Kako vam mogu pomoći?\n\n"
            "1️⃣ Rezerviraj termin\n"
            "2️⃣ Moje rezervacije"
        )

    @staticmethod
    def main_menu() -> str:
        """Main menu options."""
        return (
            "Što želite?\n\n"
            "1️⃣ Rezerviraj termin\n"
            "2️⃣ Moje rezervacije"
        )

    @staticmethod
    def show_available_slots(slots: List[AvailableSlot]) -> str:
        """Display available time slots."""
        if not slots:
            return "Nažalost, trenutno nema slobodnih termina. Molimo pokušajte kasnije."

        lines = ["Evo slobodnih termina:\n"]

        for i, slot in enumerate(slots, 1):
            date_str = Messages._format_datetime(slot.start_time)
            time_str = Messages._format_time(slot.start_time)
            lines.append(f"{i}️⃣ {date_str} u {time_str}")

        lines.append("\nOdaberite broj termina koji želite rezervirati.")
        return "\n".join(lines)

    @staticmethod
    def confirm_booking(slot: AvailableSlot) -> str:
        """Ask user to confirm booking."""
        date_str = Messages._format_datetime(slot.start_time)
        time_str = Messages._format_time(slot.start_time)

        return (
            f"Želite li potvrditi termin:\n"
            f"📅 {date_str}\n"
            f"🕐 {time_str}\n\n"
            f"1️⃣ Potvrdi (da)\n"
            f"2️⃣ Odustani (ne)"
        )

    @staticmethod
    def booking_confirmed(slot: AvailableSlot) -> str:
        """Booking confirmation message."""
        date_str = Messages._format_datetime(slot.start_time)
        time_str = Messages._format_time(slot.start_time)

        return (
            f"Termin je potvrđen! ✅\n"
            f"📅 {date_str}\n"
            f"🕐 {time_str}\n\n"
            f"Vidimo se! 💈✂️"
        )

    @staticmethod
    def show_my_reservations(appointments: List[Appointment]) -> str:
        """Display user's reservations."""
        if not appointments:
            return Messages.no_reservations()

        lines = ["Vaše rezervacije:\n"]

        for i, appt in enumerate(appointments, 1):
            date_str = Messages._format_datetime(appt.slot.start_time)
            time_str = Messages._format_time(appt.slot.start_time)
            status = "✅" if appt.status == "confirmed" else "⏱"
            lines.append(f"{i}️⃣ {date_str} u {time_str} {status}")

        lines.append("\n1️⃣ Otkaži rezervaciju")
        lines.append("2️⃣ Natrag na glavni izbornik")
        return "\n".join(lines)

    @staticmethod
    def no_reservations() -> str:
        """No reservations message."""
        return (
            "Nemate aktivnih rezervacija.\n\n"
            "1️⃣ Rezerviraj termin\n"
            "2️⃣ Natrag"
        )

    @staticmethod
    def cancel_confirmation(slot: AvailableSlot) -> str:
        """Ask to confirm cancellation."""
        date_str = Messages._format_datetime(slot.start_time)
        time_str = Messages._format_time(slot.start_time)

        return (
            f"Jeste li sigurni da želite otkazati termin?\n"
            f"📅 {date_str}\n"
            f"🕐 {time_str}\n\n"
            f"1️⃣ Da, otkaži\n"
            f"2️⃣ Ne, zadrži"
        )

    @staticmethod
    def cancel_success() -> str:
        """Cancellation success message."""
        return "Termin je uspješno otkazan. ✅"

    @staticmethod
    def error() -> str:
        """Generic error message."""
        return "Nešto nije u redu. Molimo pokušajte ponovno."

    @staticmethod
    def invalid_choice() -> str:
        """Invalid selection message."""
        return "Nevažeći izbor. Molimo pokušajte ponovno."

    @staticmethod
    def invalid_slot_number() -> str:
        """Invalid slot number selection."""
        return "Nevažeći broj termina. Molimo odaberite broj s popisa."

    @staticmethod
    def slot_no_longer_available() -> str:
        """Slot became unavailable."""
        return "Nažalost, taj termin više nije dostupan. Molimo odaberite drugi."

    @staticmethod
    def _format_datetime(dt: datetime) -> str:
        """Format datetime to Croatian format (e.g., 'Ponedjeljak, 5. prosinca 2024.')."""
        days = ['Ponedjeljak', 'Utorak', 'Srijeda', 'Četvrtak', 'Petak', 'Subota', 'Nedjelja']
        months = [
            'siječnja', 'veljače', 'ožujka', 'travnja', 'svibnja', 'lipnja',
            'srpnja', 'kolovoza', 'rujna', 'listopada', 'studenoga', 'prosinca'
        ]

        day_name = days[dt.weekday()]
        day = dt.day
        month = months[dt.month - 1]
        year = dt.year

        return f"{day_name}, {day}. {month} {year}."

    @staticmethod
    def _format_time(dt: datetime) -> str:
        """Format time (e.g., '14:30')."""
        return dt.strftime('%H:%M')
