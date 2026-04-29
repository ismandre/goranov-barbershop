# Setup Guide - Admin Dashboard

Complete setup instructions for the Goranov Barbershop admin dashboard.

## Prerequisites

- Node.js 18+ installed
- npm or yarn
- Backend API running on http://localhost:8000

## Step-by-Step Setup

### 1. Install Node.js (if not installed)

```bash
# Check if Node.js is installed
node --version

# If not installed, download from:
# https://nodejs.org/ (LTS version recommended)
```

### 2. Install Dependencies

```bash
cd admin-dashboard
npm install
```

This will install:
- Vue 3
- Vue Router
- Pinia (state management)
- Axios (HTTP client)
- Vite (build tool)
- Tailwind CSS
- PostCSS & Autoprefixer

### 3. Ensure Backend is Running

```bash
# In project root directory
cd /Users/andreism/me/goranov-barbershop

# Start FastAPI backend
uvicorn app.main:app --reload
```

Verify backend is running:
```bash
curl http://localhost:8000/
# Should return: {"status":"ok","message":"...","version":"1.0.0"}
```

### 4. Create Admin User (if not exists)

```bash
# In project root
python scripts/create_admin.py --username barber --password barber123
```

### 5. Seed Test Data (optional)

```bash
# Add some test appointments slots
python scripts/seed_slots.py
```

### 6. Start Development Server

```bash
cd admin-dashboard
npm run dev
```

You should see:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
➜  Network: use --host to expose
➜  press h + enter to show help
```

### 7. Open Browser

Navigate to: **http://localhost:3000**

You should see the login page.

### 8. Login

Use the credentials you created:
- Username: `barber`
- Password: `barber123` (or whatever you set)

## Verification Checklist

After setup, verify everything works:

- [ ] Login page loads at http://localhost:3000
- [ ] Can login with admin credentials
- [ ] Dashboard shows statistics
- [ ] Appointments page loads
- [ ] Calendar view works
- [ ] Can add new slots in Availability page
- [ ] No console errors in browser DevTools

## Common Issues

### Port 3000 already in use

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use different port
npm run dev -- --port 3001
```

### Cannot connect to backend

**Check:**
1. Backend is running: `curl http://localhost:8000/`
2. No firewall blocking ports
3. Check browser console for CORS errors

**Fix CORS if needed:** Backend already has CORS middleware enabled.

### npm install fails

```bash
# Clear cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Vite build fails

```bash
# Check Node.js version (must be 18+)
node --version

# Update if needed
nvm install 18
nvm use 18
```

## Development Workflow

### Making Changes

1. Edit files in `src/`
2. Save - Vite will hot reload automatically
3. Check browser - changes appear instantly

### Adding New Pages

1. Create component in `src/views/YourView.vue`
2. Add route in `src/router/index.js`
3. Add navigation link in `src/layouts/DashboardLayout.vue`

### Calling New API Endpoints

1. Add endpoint in `src/api/admin.js` or `src/api/auth.js`
2. Use in component:
   ```js
   import { adminAPI } from '@/api/admin'
   
   const response = await adminAPI.yourNewMethod()
   ```

## Building for Production

```bash
# Build optimized production bundle
npm run build

# Files will be in dist/ directory
# Deploy dist/ folder to your hosting service
```

Preview production build locally:
```bash
npm run preview
```

## Next Steps

Once everything is working:

1. **Customize branding** - Update colors in `tailwind.config.js`
2. **Test all features** - Go through each page and test functionality
3. **Add real data** - Create actual time slots for your business
4. **Deploy** - Follow deployment instructions in README.md

## Need Help?

- Check browser console for errors (F12 → Console tab)
- Check terminal where `npm run dev` is running for build errors
- Verify backend logs for API errors
- Check `README.md` for detailed documentation

## Success!

If you can login and see the dashboard, you're all set! 🎉

The admin dashboard is now ready for managing your barbershop appointments.
