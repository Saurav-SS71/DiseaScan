# DiseaScan - Complete Frontend Solution

## Welcome to DiseaScan!

A production-ready disease detection frontend with ChatGPT-like UI, built with React + Vite.

## Start Here

Choose your path:

### ⚡ **Quick Start** (2 minutes)
→ See `QUICK_START.md`
```bash
pnpm install && pnpm dev
```

### 📖 **Full Documentation**
→ See `README.md` (259 lines)
- Features overview
- Installation & setup
- Usage guide
- Customization

### 🔧 **Setup & Deployment**
→ See `SETUP.md` (283 lines)
- Project structure
- Environment setup
- Deployment guides
- Troubleshooting

### 🌐 **API Documentation**
→ See `API_DOCS.md` (562 lines)
- Endpoint reference
- Request/response examples
- Backend implementation
- Integration guides

### 📦 **Project Delivery Summary**
→ See `DELIVERY.md` (396 lines)
- What's included
- Architecture overview
- Technology stack
- Next steps

## What You Get

### Frontend Components (412 lines)
- **Sidebar** - Chat history with delete
- **ChatWindow** - Message display with auto-scroll
- **Message** - Text/image/prediction rendering
- **InputBox** - Text input + image upload
- **ImageUpload** - Drag-and-drop file upload

### Services & Types (97 lines)
- **api.ts** - Axios-based API layer
- **types/index.ts** - TypeScript definitions

### Configuration (80 lines)
- **App.tsx** - State management & logic (222 lines)
- **main.tsx** - Entry point
- **index.css** - Global styles
- **config.ts** - App configuration

### Build Configuration
- `vite.config.ts` - Vite bundler
- `tailwind.config.ts` - Tailwind CSS
- `tsconfig.json` - TypeScript
- `package.json` - Dependencies

### Example Backend
- `backend_example.py` - FastAPI reference implementation

## Directory Structure

```
.
├── src/
│   ├── components/          # 5 reusable React components
│   ├── services/            # API integration layer
│   ├── types/               # TypeScript types
│   ├── App.tsx              # Main application
│   ├── main.tsx             # Entry point
│   ├── config.ts            # Configuration
│   └── index.css            # Global styles
├── public/                  # Static assets
├── Configuration
│   ├── vite.config.ts
│   ├── tailwind.config.ts
│   ├── tsconfig.json
│   ├── postcss.config.js
│   ├── package.json
│   └── index.html
├── Documentation
│   ├── README.md            # Full documentation
│   ├── SETUP.md             # Setup guide
│   ├── API_DOCS.md          # API reference
│   ├── DELIVERY.md          # Project summary
│   ├── QUICK_START.md       # Quick reference
│   └── INDEX.md             # This file
├── Example Backend
│   └── backend_example.py
├── .env.local               # Environment variables
└── .gitignore              # Git ignore rules
```

## Key Features

✓ ChatGPT-like layout
✓ Image upload with drag-drop
✓ Disease predictions
✓ AI-powered explanations
✓ Chat history with persistence
✓ Typing animations
✓ Loading indicators
✓ Dark theme
✓ Fully typed (TypeScript)
✓ Responsive design
✓ Production-ready code

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19 |
| Build | Vite 5 |
| Styling | Tailwind CSS 4.2 |
| Language | TypeScript 5.7 |
| HTTP | Axios 1.6 |
| State | React Hooks |
| Backend | FastAPI (example) |

## Quick Commands

```bash
# Development
pnpm dev              # Start dev server
pnpm build            # Build for production
pnpm preview          # Preview build
pnpm lint             # Run linter

# Backend (example)
python backend_example.py    # Start FastAPI server
```

## Environment Setup

Create `.env.local`:
```bash
VITE_API_URL=http://localhost:8000
VITE_MOCK_MODE=false
```

## API Endpoints

```
POST /predict     # Image → Disease predictions
POST /explain     # Disease → AI explanation
GET  /health      # Health check
```

## File Statistics

| Category | Files | Lines |
|----------|-------|-------|
| Components | 5 | 412 |
| Services | 1 | 72 |
| Types | 1 | 25 |
| App Logic | 3 | 252 |
| Styles | 1 | 80 |
| Config | 5 | Config |
| Docs | 6 | 1500+ |
| **Total** | **22** | **~2300** |

## Getting Started

### Option 1: Frontend Only (for testing)
```bash
pnpm install
pnpm dev
# Opens http://localhost:5173
# Uses mock predictions (no backend needed)
```

### Option 2: With Backend
```bash
# Terminal 1: Frontend
pnpm install && pnpm dev

# Terminal 2: Backend
pip install fastapi uvicorn python-multipart
python backend_example.py
```

### Option 3: With OpenAI Integration
```bash
# In backend_example.py:
pip install openai
export OPENAI_API_KEY=sk-xxxxxxx
# Uncomment OpenAI code
python backend_example.py
```

## Next Steps

1. **Read** `QUICK_START.md` for immediate setup
2. **Read** `README.md` for full documentation
3. **Read** `API_DOCS.md` if connecting custom backend
4. **Review** `backend_example.py` for API structure
5. **Deploy** using `SETUP.md` guide

## Documentation Guide

### For Quick Reference
→ `QUICK_START.md` (2-minute overview)

### For Complete Setup
→ `README.md` (full feature docs)

### For Deployment
→ `SETUP.md` (deployment guides)

### For Backend Integration
→ `API_DOCS.md` (API reference)

### For Project Overview
→ `DELIVERY.md` (architecture & stats)

## Code Quality

- **TypeScript**: Full type safety
- **React**: Modern hooks patterns
- **Tailwind**: Utility-first styling
- **Architecture**: Component-based modular design
- **Performance**: Optimized rendering
- **Accessibility**: Semantic HTML
- **Error Handling**: Comprehensive error management

## Browser Support

- Chrome/Chromium 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Common Tasks

### Change Backend URL
```bash
# Option 1: Environment
VITE_API_URL=https://api.example.com pnpm dev

# Option 2: .env.local
echo "VITE_API_URL=https://api.example.com" > .env.local
```

### Deploy to Vercel
```bash
vercel login
vercel
# Set VITE_API_URL in dashboard
```

### Add OpenAI API
1. Install: `pip install openai`
2. Set env: `export OPENAI_API_KEY=sk-xxx`
3. Edit: `backend_example.py` (uncomment OpenAI code)

### Use Mock Mode (no backend)
```bash
VITE_MOCK_MODE=true pnpm dev
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Cannot connect to API" | Ensure backend running, check VITE_API_URL |
| "Port 5173 in use" | Change port in vite.config.ts |
| "Images won't upload" | Check file is PNG/JPG/GIF, < 10MB |
| "Chat history gone" | Check localStorage enabled, not incognito |
| "Build fails" | Run `pnpm install --force` |

## Support

- **Issues?** Check the relevant documentation file
- **Setup help?** See `SETUP.md`
- **API help?** See `API_DOCS.md`
- **Quick ref?** See `QUICK_START.md`
- **Full docs?** See `README.md`

## License

MIT - Free for commercial and personal projects

---

## Ready to Start?

```bash
pnpm install
pnpm dev
```

Then visit `http://localhost:5173`

**Happy coding!** 🚀

---

### File Manifest

| File | Purpose | Size |
|------|---------|------|
| `README.md` | Full documentation | 259 lines |
| `SETUP.md` | Setup & deployment | 283 lines |
| `API_DOCS.md` | API reference | 562 lines |
| `DELIVERY.md` | Project summary | 396 lines |
| `QUICK_START.md` | Quick reference | 214 lines |
| `INDEX.md` | This file | Navigation |
| `backend_example.py` | FastAPI reference | 159 lines |
| `src/App.tsx` | Main app | 222 lines |
| `src/components/*.tsx` | React components | 412 lines |
| `src/services/api.ts` | API layer | 72 lines |
| `tailwind.config.ts` | Tailwind config | 40 lines |
| `vite.config.ts` | Vite config | 14 lines |

**Total:** 2,600+ lines of production-ready code and documentation
