# Setup Guide

## Quick Setup (3 Minutes)

### Step 1: Start FastAPI Backend

Open a terminal in the parent directory:

```bash
cd ..
python main.py
```

You should see:
```
🚀 Starting MCP FastAPI Server on http://localhost:8000
📚 API docs available at http://localhost:8000/docs
✓ MCP Client initialized
```

### Step 2: Install Dependencies (Already Done!)

Dependencies are already installed! If you need to reinstall:

```bash
npm install
```

### Step 3: Start Next.js Development Server

```bash
npm run dev
```

The app will be available at: **http://localhost:3000**

### Step 4: Open in Browser

Visit: http://localhost:3000

You should see:
- Two tabs: **Chat** and **Users**
- Clean, modern interface

## What to Try

### In the Chat Tab:

Click example prompts or type:
- "Create a random user"
- "How many users are in the database?"
- "Create a user named Alice with email alice@example.com"

You'll see:
- AI responses
- Tool calls being made
- Results from the database

### In the Users Tab:

- View all users
- Click "Add Random User" to create users instantly
- See real-time updates

## Verification Checklist

✅ **Backend Running**: FastAPI server at http://localhost:8000
- Test: `curl http://localhost:8000/` should return `{"status":"ok",...}`

✅ **Frontend Running**: Next.js at http://localhost:3000
- Test: Open in browser, see the app

✅ **Connection Working**: Chat sends messages successfully
- Test: Type a message in chat, get AI response

✅ **Tools Working**: User creation works
- Test: Click "Add Random User" in Users tab

## Troubleshooting

### Port 3000 Already in Use

```bash
# Kill existing process
lsof -ti:3000 | xargs kill -9

# Or use a different port
npm run dev -- -p 3001
```

### Backend Not Responding

```bash
# Check if backend is running
curl http://localhost:8000/

# If not, start it
cd ..
python main.py
```

### CORS Errors

The FastAPI server should have CORS configured for `localhost:3000`. If you see CORS errors:

1. Check FastAPI console for errors
2. Verify `main.py` has CORS middleware configured
3. Check browser console for specific error

### Build Errors

```bash
# Clear cache and rebuild
rm -rf .next
npm run build
```

## Development Tips

### Auto-Reload

Both servers support auto-reload:
- **Next.js**: Changes to `.tsx`, `.ts`, `.css` files auto-reload
- **FastAPI**: Changes to `.py` files may require restart

### Hot Module Replacement

Next.js preserves component state during development, so you can:
- Edit components without losing chat history
- Tweak styles and see instant updates

### TypeScript Errors

If you see TypeScript errors in your editor:
```bash
# Verify types
npx tsc --noEmit
```

## Production Build

### Build

```bash
npm run build
```

This creates an optimized production build in `.next/`.

### Start Production Server

```bash
npm start
```

Runs the production build on port 3000.

### Production Checklist

- [ ] Build completes without errors
- [ ] Environment variables set correctly
- [ ] Backend API URL updated for production
- [ ] CORS configured for production domain

## Environment Variables

Current configuration (`.env.local`):
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

For production, update to your deployed API URL:
```
NEXT_PUBLIC_API_URL=https://your-api.example.com
```

## Architecture

```
Browser (localhost:3000)
    ↓ HTTP
Next.js Frontend
    ↓ REST API
FastAPI Backend (localhost:8000)
    ↓ stdio
MCP Server
    ↓
Database (users.json) + RandomUser.me API
```

## Next Steps

1. **Customize UI**: Edit components in `components/`
2. **Add Features**: Extend API client in `lib/api.ts`
3. **Style Changes**: Modify Tailwind config or global CSS
4. **Deploy**: Use Vercel for Next.js, Railway/Render for FastAPI

## Success!

If you can:
- ✅ Chat with the AI
- ✅ See tool calls in responses
- ✅ Create users via chat or Users tab
- ✅ View all users

**You're all set!** 🎉

Enjoy exploring MCP with this chat interface!
