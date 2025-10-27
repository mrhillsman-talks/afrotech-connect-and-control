# MCP Chat App

A modern Next.js chat interface for interacting with MCP (Model Context Protocol) via a FastAPI backend.

## Features

- 💬 **Chat Interface**: Natural language conversations with AI
- 🛠️ **Tool Visualization**: See which MCP tools are being called
- 👥 **User Management**: View and create users
- 🎨 **Modern UI**: Built with Tailwind CSS
- ⚡ **Fast**: Next.js 14 with App Router
- 🔒 **Type-Safe**: Full TypeScript support

## Prerequisites

- Node.js 18+ and npm
- FastAPI backend running on `http://localhost:8000`

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

The `.env.local` file is already configured with:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

If you need to change the backend URL, edit `.env.local`.

### 3. Start Development Server

```bash
npm run dev
```

The app will be available at `http://localhost:3000`

### 4. Start the FastAPI Backend

In the parent directory:
```bash
cd ..
python main.py
```

## Project Structure

```
mcp-chat-app/
├── app/                    # Next.js App Router
│   ├── layout.tsx         # Root layout with metadata
│   ├── page.tsx           # Main page with tabs
│   └── globals.css        # Global styles
├── components/             # React components
│   ├── Chat.tsx           # Chat interface
│   └── UserList.tsx       # User list view
├── lib/                    # Utilities
│   └── api.ts             # API client
├── types/                  # TypeScript types
│   └── index.ts           # Type definitions
├── public/                 # Static assets
├── .env.local             # Environment variables
└── package.json           # Dependencies
```

## Available Scripts

- `npm run dev` - Start development server (port 3000)
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint

## Usage

### Chat Tab

1. Type a message in the input field
2. AI will process your request and call appropriate tools
3. See tool calls and results in the response
4. Click example prompts to get started quickly

Example prompts:
- "Create a random user"
- "How many users are in the database?"
- "Create a user named John Doe with email john@example.com"

### Users Tab

1. View all users in the database
2. Click "Add Random User" to create a new user
3. Click "Refresh List" to reload users
4. See user details including name, email, address, and phone

## API Integration

The app connects to the FastAPI backend at `http://localhost:8000` with the following endpoints:

- `POST /chat` - Send chat messages
- `GET /users` - Get all users
- `POST /tools/call` - Call MCP tools directly
- `GET /capabilities` - Get available tools/resources
- `GET /` - Health check

## Customization

### Changing the API URL

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=https://your-api-url.com
```

### Styling

The app uses Tailwind CSS. Modify:
- `tailwind.config.js` - Tailwind configuration
- `app/globals.css` - Global styles
- Component files - Component-specific styles

### Adding Features

1. **New API endpoints**: Add to `lib/api.ts`
2. **New types**: Add to `types/index.ts`
3. **New components**: Create in `components/`
4. **New pages**: Create in `app/`

## Troubleshooting

### Port Already in Use

```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9

# Or use a different port
npm run dev -- -p 3001
```

### API Connection Issues

1. Verify FastAPI backend is running: `http://localhost:8000`
2. Check `.env.local` has correct API URL
3. Check browser console for CORS errors
4. Ensure FastAPI CORS middleware allows `localhost:3000`

### Build Errors

```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

## Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel
```

Set environment variable in Vercel dashboard:
- `NEXT_PUBLIC_API_URL` = your production API URL

### Docker

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

Build and run:
```bash
docker build -t mcp-chat-app .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://your-api mcp-chat-app
```

## Technologies

- **Next.js 14** - React framework with App Router
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first styling
- **React 18** - UI library

## Contributing

1. Make changes in a new branch
2. Test locally with `npm run dev`
3. Run linting with `npm run lint`
4. Build with `npm run build` to check for errors
5. Submit a pull request

## License

MIT

## Support

For issues:
1. Check the console for error messages
2. Verify FastAPI backend is running
3. Check browser network tab
4. Review API documentation at `http://localhost:8000/docs`
