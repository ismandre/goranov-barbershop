# Testing Checklist - Croatian Mobile-Friendly Dashboard

## 🧪 Quick Start Testing

### 1. Start the Application

```bash
# Terminal 1: Backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd admin-dashboard
npm run dev
```

### 2. Open in Browser
- Desktop: http://localhost:3000
- Mobile: Use Chrome DevTools (F12 → Toggle Device Toolbar)

## ✅ Desktop Testing

### Login Page
- [ ] Page loads with Croatian text
- [ ] "Korisničko ime" and "Lozinka" fields visible
- [ ] Button says "Prijavi se"
- [ ] Login with: username=`barber`, password=`barber123`
- [ ] Redirects to dashboard after successful login

### Dashboard (Početna)
- [ ] Title says "Pregled"
- [ ] 4 stat cards visible: Danas, Na čekanju, Dostupno, Ukupno
- [ ] "Brze akcije" section shows 3 actions
- [ ] "Informacije" section shows version and status
- [ ] Status shows "Aktivno" with green dot

### Sidebar Navigation
- [ ] All menu items in Croatian: Početna, Termini, Kalendar, Dostupnost
- [ ] Active page is highlighted
- [ ] User initial appears in bottom circle
- [ ] Logout button works (redirects to login)

### Appointments (Termini)
- [ ] Page title is "Termini"
- [ ] Filter section says "Filteri"
- [ ] Status dropdown shows Croatian options
- [ ] "Primijeni" button applies filters
- [ ] "Osvježi" button reloads data
- [ ] Table shows appointments (if any exist)
- [ ] Status badges in Croatian
- [ ] Can change appointment status via dropdown

### Calendar (Kalendar)
- [ ] Page title is "Kalendar"
- [ ] Week navigation arrows work
- [ ] "Danas" button goes to current week
- [ ] Week days in Croatian: Ned, Pon, Uto, etc.
- [ ] Current day is highlighted
- [ ] Click appointment opens modal
- [ ] Modal shows "Detalji termina"
- [ ] Modal "Zatvori" button closes it

### Availability (Dostupnost)
- [ ] Page title is "Dostupnost"
- [ ] Two forms: "Dodaj jedan termin" and "Dodaj više termina"
- [ ] Single slot form has Datum, Početak, Kraj
- [ ] Bulk form calculates number of slots
- [ ] "Dodaj termin" button adds single slot
- [ ] Success message in Croatian: "Termin uspješno dodan!"
- [ ] Existing slots table shows with Croatian headers
- [ ] "Samo slobodni" checkbox filters
- [ ] "Obriši" button deletes available slots
- [ ] Confirmation dialog in Croatian

## 📱 Mobile Testing (< 640px width)

### Responsive Layout
- [ ] Hamburger menu icon visible in header
- [ ] Tap hamburger opens sidebar from left
- [ ] Tap outside sidebar closes it
- [ ] No horizontal scrolling anywhere

### Login Page (Mobile)
- [ ] Form fits screen width
- [ ] Inputs are large and easy to tap
- [ ] No zoom when focusing inputs
- [ ] "Prijavi se" button is full width

### Dashboard (Mobile)
- [ ] Stats cards stack vertically (1 column)
- [ ] All text is readable without zooming
- [ ] "Brze akcije" cards stack vertically
- [ ] Cards have good spacing

### Appointments (Mobile)
- [ ] Title and "Osvježi" button fit on one row or stack nicely
- [ ] Filters stack vertically
- [ ] Appointments show as cards (not table)
- [ ] Each card shows customer, date, time, status
- [ ] Status dropdown is full width
- [ ] Easy to read and tap

### Calendar (Mobile)
- [ ] Week navigation buttons are large
- [ ] Shows list view (not grid)
- [ ] Each day is a separate card
- [ ] Day name and date clearly visible
- [ ] Appointments within day are color-coded
- [ ] "Danas" badge shows on current day
- [ ] Free slots shown under appointments

### Availability (Mobile)
- [ ] Two forms stack vertically
- [ ] All inputs are full width
- [ ] Time inputs are easy to use
- [ ] Info box about slot count is visible
- [ ] Existing slots show as cards (not table)
- [ ] Each slot card shows time, duration, status
- [ ] "Obriši termin" button is full width

## 🎯 Touch Interaction Tests

### Button Sizes
- [ ] All buttons are easy to tap (minimum 44px)
- [ ] Buttons show visual feedback when tapped
- [ ] No accidental taps on nearby elements

### Input Fields
- [ ] Date pickers open native date selector
- [ ] Time pickers open native time selector
- [ ] Text inputs don't cause page zoom on focus
- [ ] Dropdowns are easy to use on mobile

### Navigation
- [ ] Sidebar slides smoothly
- [ ] Menu items are easy to tap
- [ ] Overlay closes menu when tapped

## 🌐 Language Verification

### Check All Croatian Translations
- [ ] No English text visible (except technical terms like "ID")
- [ ] Date formats use Croatian locale (hr-HR)
- [ ] Time formats use 24-hour format
- [ ] Error messages in Croatian
- [ ] Success messages in Croatian
- [ ] Confirmation dialogs in Croatian

## ⚡ Performance Tests

### Loading States
- [ ] Spinner shows when loading data
- [ ] Text says "Učitavanje..." while loading
- [ ] No blank screens during load

### Form Submissions
- [ ] Buttons disable while submitting
- [ ] Spinner shows during submission
- [ ] Success message appears after completion
- [ ] Data refreshes after actions

### Error Handling
- [ ] Invalid login shows Croatian error
- [ ] Network errors show friendly message
- [ ] Form validation prevents invalid submissions

## 🔄 User Flow Tests

### Complete Appointment Management Flow
1. [ ] Login as barber
2. [ ] Go to Dostupnost
3. [ ] Add a single slot for tomorrow at 10:00-10:30
4. [ ] Verify slot appears in list
5. [ ] Go to Kalendar
6. [ ] Verify slot shows as "Dostupno"
7. [ ] Delete the slot
8. [ ] Verify confirmation dialog
9. [ ] Verify slot is removed

### Complete Multi-Device Test
1. [ ] Open on desktop browser
2. [ ] Add 5 slots using bulk add
3. [ ] Open same URL on mobile (or DevTools)
4. [ ] Verify all 5 slots visible
5. [ ] Delete one slot from mobile
6. [ ] Refresh desktop
7. [ ] Verify slot is deleted

## 🐛 Common Issues to Check

### Mobile-Specific
- [ ] No horizontal scroll bars
- [ ] All modals fit on screen
- [ ] Forms don't overflow screen
- [ ] Text doesn't get cut off
- [ ] Buttons don't overlap

### Desktop-Specific
- [ ] Sidebar always visible
- [ ] Tables display properly
- [ ] Multi-column layouts work
- [ ] No wasted white space

### Both
- [ ] Logout works from all pages
- [ ] Navigation preserves filters
- [ ] Date/time formatted correctly
- [ ] Colors are consistent

## 📸 Visual Inspection

### Color Coding
- [ ] Green = confirmed/available
- [ ] Yellow = pending
- [ ] Blue = completed
- [ ] Red = cancelled/booked
- [ ] Consistent across all pages

### Typography
- [ ] Headings are clear hierarchy
- [ ] Body text is readable (min 14px)
- [ ] Labels are bold and clear
- [ ] Icons align with text

### Spacing
- [ ] Cards have consistent padding
- [ ] Lists have good spacing
- [ ] Buttons have breathing room
- [ ] Nothing feels cramped

## ✨ Final Acceptance Criteria

### For Tech-Savvy Owner
- [ ] Can login without help
- [ ] Understands what each page does
- [ ] Can add a time slot successfully
- [ ] Can view appointments easily
- [ ] Can change appointment status
- [ ] Can use on phone comfortably

### Overall Quality
- [ ] All text in Croatian
- [ ] Works on mobile phone
- [ ] Works on tablet
- [ ] Works on desktop
- [ ] Fast and responsive
- [ ] No errors in browser console

## 🎉 Success Criteria Met When:
- ✅ All checkboxes above are checked
- ✅ No English text visible
- ✅ Barbershop owner can use it without asking questions
- ✅ Works smoothly on phone and computer
- ✅ Everything looks professional and polished

---

**Last Updated**: After Croatian & Mobile-Friendly implementation
**Testing Environment**: Chrome/Safari on iOS/Android + Desktop browsers
