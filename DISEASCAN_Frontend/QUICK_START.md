# DiseaScan Quick Reference

## Get Started in 2 Minutes

```bash
# 1. Install
pnpm install

# 2. Run
pnpm dev

# 3. Open
# http://localhost:5173
```

## Key Files

| File | Purpose | Lines |
|------|---------|-------|
| `src/App.tsx` | Main app + state | 222 |
| `src/components/ChatWindow.tsx` | Message display | 58 |
| `src/components/Message.tsx` | Message rendering | 93 |
| `src/components/InputBox.tsx` | Input area | 102 |
| `src/components/Sidebar.tsx` | Chat history | 85 |
| `src/components/ImageUpload.tsx` | File upload | 74 |
| `src/services/api.ts` | API calls | 72 |

## Commands

```bash
pnpm dev          # Start dev server
pnpm build        # Build for production
pnpm preview      # Preview build
pnpm lint         # Run linter
```

## API Endpoints

```bash
POST /predict     # Image analysis -> Disease predictions
POST /explain     # Disease details -> AI explanation
```

## Environment Setup

Create `.env.local`:
```
VITE_API_URL=http://localhost:8000
VITE_MOCK_MODE=false
```

## Backend Quick Start

```bash
# Install
pip install fastapi uvicorn python-multipart

# Run
python backend_example.py

# Test
curl -X POST http://localhost:8000/predict -F "file=@image.jpg"
```

## Folder Structure

```
src/
├── components/     # 5 React components
├── services/       # API layer
├── types/          # TypeScript types
├── App.tsx         # Main component
├── main.tsx        # Entry point
├── config.ts       # Configuration
└── index.css       # Global styles
```

## Key Features

- ChatGPT-like interface
- Image upload (drag & drop)
- Disease predictions
- AI explanations
- Chat history (localStorage)
- Dark theme
- Type-safe (TypeScript)
- Responsive design

## Common Tasks

### Change API URL
Edit `.env.local`:
```
VITE_API_URL=https://your-api.com
```

### Add OpenAI Explanations
1. `pip install openai`
2. Set `OPENAI_API_KEY` env var
3. Uncomment code in `backend_example.py`

### Deploy Frontend
```bash
pnpm build        # Create dist/
vercel            # Upload to Vercel
```

### Deploy Backend
```bash
heroku create my-app
git push heroku main
```

## Component Props

### Sidebar
```typescript
{
  chats: Chat[]
  onNewChat: () => void
  onSelectChat: (id: string) => void
  onDeleteChat: (id: string) => void
  currentChatId: string | null
}
```

### ChatWindow
```typescript
{
  messages: Message[]
  isLoading: boolean
}
```

### InputBox
```typescript
{
  onSendMessage: (text, imageFile?, imagePreview?) => void
  isLoading: boolean
}
```

## API Response Format

### Predictions
```json
{
  "predictions": [
    {"label": "Disease", "confidence": 0.85},
    {"label": "Other", "confidence": 0.15}
  ]
}
```

### Explanation
```json
{
  "explanation": "Disease details..."
}
```

## Tips & Tricks

1. **Clear chat history**: Open DevTools → Application → localStorage → Clear
2. **Debug API calls**: Open DevTools → Network tab
3. **Mock mode**: Set `VITE_MOCK_MODE=true` to test without backend
4. **Faster builds**: Use `pnpm dev` for hot reload development
5. **Type checking**: Run `tsc --noEmit` to check types

## File Sizes (Production)

- Main bundle: ~150KB (gzipped)
- Image handling: Optimized
- Dependencies: Well-optimized
- Total: Production-ready

## Browser Compatibility

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Port already in use | Change port in `vite.config.ts` |
| API not connecting | Check backend URL in `.env.local` |
| Images not uploading | Verify file type (PNG/JPG/GIF) |
| Chat not saving | Check localStorage enabled |
| Slow performance | Clear cache, rebuild |

## Documentation

- `README.md` - Full docs
- `SETUP.md` - Setup guide
- `API_DOCS.md` - API reference
- `DELIVERY.md` - Project summary

## Next Steps

1. Connect your ML model
2. Add authentication (optional)
3. Integrate OpenAI for explanations
4. Deploy to production
5. Monitor & optimize

---

**Ready to code?** `pnpm dev`

**Questions?** See `README.md` and `API_DOCS.md`
