# DiseaScan Setup Guide

## Quick Start (5 minutes)

### 1. Install Dependencies
```bash
pnpm install
```

### 2. Start Development Server
```bash
pnpm dev
```

The frontend will open at `http://localhost:5173`

### 3. Setup Backend (Optional)

#### Option A: Use the Example Backend
```bash
# Install FastAPI
pip install fastapi uvicorn python-multipart

# Run the example backend
python backend_example.py
```

Backend runs at `http://localhost:8000`

#### Option B: Use Your Own Backend
Update `.env.local`:
```
VITE_API_URL=https://your-backend-url.com
```

## Full Project Structure

```
diseascan/
├── src/
│   ├── components/
│   │   ├── Sidebar.tsx           # Chat history sidebar
│   │   ├── ChatWindow.tsx        # Main chat display
│   │   ├── Message.tsx           # Individual message
│   │   ├── ImageUpload.tsx       # Drag-drop upload
│   │   └── InputBox.tsx          # Input & controls
│   ├── services/
│   │   └── api.ts                # Backend API calls
│   ├── types/
│   │   └── index.ts              # Type definitions
│   ├── App.tsx                   # Main component
│   ├── main.tsx                  # Entry point
│   ├── config.ts                 # App config
│   └── index.css                 # Global styles
├── public/                        # Static assets
├── vite.config.ts                # Vite configuration
├── tailwind.config.ts            # Tailwind config
├── tsconfig.json                 # TypeScript config
├── package.json                  # Dependencies
├── index.html                    # HTML template
├── backend_example.py            # Example FastAPI backend
├── README.md                     # Full documentation
└── .env.local                    # Environment variables

```

## Features Implemented

✅ **ChatGPT-like Layout**
- Left sidebar with chat history
- Main chat area with messages
- Input box at bottom

✅ **Image Upload**
- Drag-and-drop support
- Click to select file
- Image preview before sending
- Remove image option

✅ **Backend Integration**
- API service layer with Axios
- Image upload via multipart/form-data
- Error handling with fallback messages

✅ **Chat System**
- Persistent chat history (localStorage)
- Multiple chats management
- Delete chat functionality
- Chat title from first message

✅ **UI/UX Features**
- Smooth animations and transitions
- Typing animation for AI responses
- Loading indicators
- Responsive design
- Dark theme with modern styling

✅ **Message Types**
- Text messages (user & assistant)
- Image messages with preview
- Prediction messages with confidence scores
- AI explanations

## API Integration Details

### Backend API Endpoints

#### POST /predict
```bash
curl -X POST http://localhost:8000/predict \
  -F "file=@image.jpg"
```

Response:
```json
{
  "predictions": [
    {"label": "Disease A", "confidence": 0.85},
    {"label": "Disease B", "confidence": 0.10},
    {"label": "Disease C", "confidence": 0.05}
  ]
}
```

#### POST /explain
```bash
curl -X POST http://localhost:8000/explain \
  -H "Content-Type: application/json" \
  -d '{"disease": "Eczema", "confidence": 0.85}'
```

Response:
```json
{
  "explanation": "Eczema is a chronic inflammatory skin condition..."
}
```

## Development Commands

```bash
# Start dev server
pnpm dev

# Build for production
pnpm build

# Preview production build
pnpm preview

# Run linter
pnpm lint
```

## Environment Variables

Create `.env.local`:
```bash
# Backend API URL (default: http://localhost:8000)
VITE_API_URL=http://localhost:8000

# Enable mock mode (no API calls)
VITE_MOCK_MODE=false
```

## Customization

### Change API URL
Edit `.env.local`:
```
VITE_API_URL=https://your-disease-detection-api.com
```

### Add OpenAI Explanations
In your backend `backend_example.py`:

1. Install: `pip install openai`
2. Set env: `export OPENAI_API_KEY=your-key`
3. Uncomment the OpenAI code in `/explain` endpoint

### Modify UI Colors
Edit `src/index.css` and `tailwind.config.ts`:
```ts
// tailwind.config.ts
theme: {
  extend: {
    colors: {
      // Your custom colors
    }
  }
}
```

### Change Default Backend
Edit `src/services/api.ts`:
```ts
const API_BASE_URL = 'https://your-api.com'
```

## Deployment

### Deploy Frontend (Vercel)
```bash
# Login to Vercel
vercel login

# Deploy
vercel

# Set environment variables in Vercel dashboard
```

### Deploy Backend (Heroku/Railway)
1. Ensure `backend_example.py` is in repo root
2. Create `requirements.txt`:
```
fastapi
uvicorn
python-multipart
```

3. Create `Procfile`:
```
web: uvicorn backend_example:app --host 0.0.0.0 --port $PORT
```

4. Deploy to Heroku:
```bash
git push heroku main
```

5. Update frontend `.env` with new backend URL

## Troubleshooting

### "Cannot connect to API"
- Ensure backend is running: `python backend_example.py`
- Check CORS is enabled in backend
- Verify `VITE_API_URL` in `.env.local`

### Images not uploading
- Check file size (max 10MB)
- Verify file format (PNG, JPG, GIF)
- Check browser console for errors

### Chat history not persisting
- Check localStorage is enabled
- Check browser privacy settings
- Try clearing browser cache

### Styling issues
- Rebuild Tailwind: `pnpm dev`
- Clear browser cache
- Check dark theme is active

## Performance Tips

1. **Optimize Images**: Compress before upload
2. **API Caching**: Implement result caching in backend
3. **Lazy Loading**: Images are lazy-loaded automatically
4. **Chat Limits**: Consider archiving old chats after 30 days

## Next Steps

1. ✅ Frontend is ready - test with example backend
2. 📊 Connect your disease detection model
3. 🤖 Integrate OpenAI or other LLM for explanations
4. 🔐 Add user authentication
5. 📱 Test on mobile devices
6. 🚀 Deploy to production

## Support & Resources

- **Vite Docs**: https://vitejs.dev
- **React Docs**: https://react.dev
- **Tailwind Docs**: https://tailwindcss.com
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **OpenAI Docs**: https://platform.openai.com/docs

## License

MIT - Feel free to use for commercial or personal projects
