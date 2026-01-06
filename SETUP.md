# FlowTask Setup Instructions

## Database Configuration (Required for Auth Persistence)

### 1. Create Neon Serverless PostgreSQL Database

1. Visit https://console.neon.tech
2. Click "Create Project"
3. Choose a region (e.g., US East)
4. Copy the connection string provided

### 2. Configure Environment Variables

Edit `frontend/.env.local` and add your database URL:

```env
DATABASE_URL=postgresql://username:password@ep-xxx.us-east-1.aws.neon.tech/neondb?sslmode=require
```

**CRITICAL**: Replace the placeholder with your actual Neon connection string.

### 3. Restart Development Server

```bash
cd frontend
npm run dev
```

### 4. Test Authentication

1. Navigate to http://localhost:3000
2. Click "Get Started"
3. Create an account with email/password
4. You should see a green toast: "Account created successfully!"
5. Login with your credentials
6. You should be redirected to the dashboard with your username displayed

## Features Implemented

### ✅ Phase 4 Complete

- **Navbar**: Sticky, glassmorphic, displays parsed username
- **Footer**: Premium SaaS multi-column layout on all pages
- **Dashboard**: Interactive project cards (Project Alpha 85%, Marketing Campaign 60%)
- **Animated Progress Bars**: Smooth fill animations on page load
- **Hover Effects**: Elevation and scale on card hover
- **Scroll-based Reveal**: Feature cards fade in as you scroll
- **Motion System**: Framer Motion animations across all pages
- **Better Auth**: Configured for Neon PostgreSQL persistence

### Database Files

- `frontend/lib/auth.ts` - Better Auth configuration with Neon adapter
- `frontend/lib/auth-client.ts` - Client-side auth hooks
- `frontend/.env.local` - Environment configuration

## Troubleshooting

### Issue: Navbar not visible
- Check that `z-index: 50` is present in Navbar component
- Verify layout does not have conflicting z-index values

### Issue: Authentication not persisting
- Ensure `DATABASE_URL` is set correctly in `.env.local`
- Restart the development server after adding the URL
- Check Neon console for connection errors

### Issue: Animations not smooth
- Ensure GPU acceleration is enabled in browser
- Verify Framer Motion is using `transform` and `opacity` only
- Check browser console for performance warnings

## Next Steps

1. Set up Neon database (see above)
2. Test signup/login flow
3. Verify dashboard displays interactive cards
4. Check that animations work smoothly (60 FPS)
5. Test responsive layout (300px - 2560px)
