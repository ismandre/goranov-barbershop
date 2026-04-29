# Goranov Barbershop - Admin Dashboard

Vue.js admin dashboard for managing barbershop appointments and availability.

## Features

✅ **Authentication** - Secure JWT-based login
✅ **Dashboard** - Overview statistics and quick actions
✅ **Appointments** - View and manage all appointments
✅ **Calendar** - Week view of appointments and available slots
✅ **Availability** - Add single or bulk time slots
✅ **Responsive Design** - Works on desktop and tablet
✅ **Modern UI** - Built with Tailwind CSS

## Tech Stack

- **Vue 3** - Progressive JavaScript framework
- **Vite** - Fast build tool
- **Vue Router** - Client-side routing
- **Pinia** - State management
- **Axios** - HTTP client
- **Tailwind CSS** - Utility-first CSS

## Quick Start

### 1. Install Dependencies

```bash
cd admin-dashboard
npm install
```

### 2. Start Backend API

In the project root:
```bash
# Make sure backend is running
uvicorn app.main:app --reload
```

The backend should be running on `http://localhost:8000`

### 3. Start Development Server

```bash
npm run dev
```

Dashboard will be available at `http://localhost:3000`

### 4. Login

Default credentials:
- **Username**: barber
- **Password**: (the password you set when creating admin)

If you haven't created an admin yet:
```bash
# In project root
python scripts/create_admin.py --username barber --password barber123
```

## Build for Production

```bash
npm run build
```

Built files will be in `dist/` directory.

Preview production build:
```bash
npm run preview
```

## Project Structure

```
admin-dashboard/
├── src/
│   ├── api/              # API client and endpoints
│   │   ├── client.js     # Axios instance with interceptors
│   │   ├── auth.js       # Authentication endpoints
│   │   └── admin.js      # Admin API endpoints
│   ├── stores/           # Pinia stores
│   │   └── auth.js       # Authentication state
│   ├── router/           # Vue Router configuration
│   │   └── index.js      # Routes and navigation guards
│   ├── views/            # Page components
│   │   ├── LoginView.vue
│   │   ├── DashboardView.vue
│   │   ├── AppointmentsView.vue
│   │   ├── CalendarView.vue
│   │   └── AvailabilityView.vue
│   ├── layouts/          # Layout components
│   │   └── DashboardLayout.vue
│   ├── App.vue           # Root component
│   ├── main.js           # Entry point
│   └── style.css         # Global styles (Tailwind)
├── index.html
├── vite.config.js
├── tailwind.config.js
└── package.json
```

## Pages

### Dashboard (`/`)
- Statistics cards (appointments, pending, slots, customers)
- Quick action links
- System information

### Appointments (`/appointments`)
- List all appointments with filters (date, status)
- Update appointment status inline
- View customer details

### Calendar (`/calendar`)
- Week view of all appointments
- Navigate between weeks
- See available slots
- Click appointments for details

### Manage Availability (`/availability`)
- **Add Single Slot**: Create one time slot
- **Bulk Add Slots**: Create multiple slots for a day
- **View/Delete Slots**: Manage existing time slots
- Filter by date and availability

## API Integration

The dashboard connects to the FastAPI backend at `http://localhost:8000`.

All API calls go through the axios client in `src/api/client.js` which:
- Automatically adds JWT token to requests
- Handles 401 errors and redirects to login
- Uses proxy for development (configured in `vite.config.js`)

## Authentication

JWT token is:
- Stored in `localStorage` as `admin_token`
- Automatically added to all API requests
- Checked on route navigation
- Cleared on logout

Protected routes redirect to `/login` if not authenticated.

## Customization

### Change Colors

Edit `tailwind.config.js`:
```js
theme: {
  extend: {
    colors: {
      primary: {
        // Change these values
        500: '#0ea5e9',
        600: '#0284c7',
        700: '#0369a1',
      }
    }
  }
}
```

### Change API URL

Edit `src/api/client.js`:
```js
const apiClient = axios.create({
  baseURL: 'https://your-api-domain.com'
})
```

## Deployment

### Option 1: Static Hosting (Vercel, Netlify)

1. Build the app:
   ```bash
   npm run build
   ```

2. Deploy the `dist/` folder to your hosting provider

3. Configure environment:
   - Set API base URL in `src/api/client.js`
   - Enable CORS on backend for your domain

### Option 2: Serve with Backend

1. Build the app:
   ```bash
   npm run build
   ```

2. Serve static files from FastAPI:
   ```python
   from fastapi.staticfiles import StaticFiles

   app.mount("/", StaticFiles(directory="admin-dashboard/dist", html=True), name="static")
   ```

## Troubleshooting

### Cannot connect to API

- Check backend is running on `http://localhost:8000`
- Check CORS is enabled in backend
- Check network tab in browser dev tools

### Login fails

- Verify admin user exists: `python scripts/create_admin.py`
- Check credentials
- Check browser console for errors

### Slots not showing

- Seed some slots: `python scripts/seed_slots.py`
- Check filters (date, availability toggle)

## Development Tips

### Hot Reload

Vite provides instant hot module replacement (HMR). Changes appear immediately without full page reload.

### Vue DevTools

Install Vue DevTools browser extension for debugging:
- https://devtools.vuejs.org/

### API Proxy

Development server proxies API requests to avoid CORS issues:
- `/admin/*` → `http://localhost:8000/admin/*`
- `/whatsapp/*` → `http://localhost:8000/whatsapp/*`

Configured in `vite.config.js`

## Next Steps

- [ ] Add user management page
- [ ] Implement appointment notes/details editing
- [ ] Add email/SMS notifications UI
- [ ] Create reports and analytics page
- [ ] Add mobile responsive improvements
- [ ] Implement dark mode

## License

MIT
