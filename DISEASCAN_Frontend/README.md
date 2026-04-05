# DiseaScan - Disease Detection Frontend

A modern, ChatGPT-like React + Vite application for disease detection with AI-powered explanations.

## Features

- 💬 ChatGPT-like interface with conversation history
- 🖼️ Image upload with drag-and-drop support
- 🔍 Disease prediction from images
- 🤖 AI-generated disease explanations
- 📱 Responsive design
- 🌙 Dark theme UI
- ✨ Smooth animations and typing effects
- 💾 Chat history persistence with localStorage

## Project Structure

```
src/
├── components/
│   ├── Sidebar.tsx         # Left sidebar with chat history
│   ├── ChatWindow.tsx      # Main chat display area
│   ├── Message.tsx         # Individual message component
│   ├── ImageUpload.tsx     # Image upload with drag-drop
│   └── InputBox.tsx        # Message input & controls
├── services/
│   └── api.ts              # Backend API integration
├── types/
│   └── index.ts            # TypeScript type definitions
├── App.tsx                 # Main application component
├── main.tsx                # Entry point
├── config.ts               # Configuration
└── index.css               # Global styles
```

## Prerequisites

- Node.js 18+ 
- npm or pnpm

## Installation

1. Install dependencies:
```bash
pnpm install
```

2. Create `.env.local` file:
```bash
VITE_API_URL=http://localhost:8000
```

## Development

Start the development server:
```bash
pnpm dev
```

The app will open at `http://localhost:5173`

## Building

Build for production:
```bash
pnpm build
```

Preview production build:
```bash
pnpm preview
```

## Backend API Integration

### API Configuration

The app expects a FastAPI backend running at `http://localhost:8000` by default.

Set a custom API URL using environment variable:
```bash
VITE_API_URL=https://your-api-url.com pnpm dev
```

### Required Backend Endpoints

#### 1. Image Prediction
```
POST /predict
Content-Type: multipart/form-data

Request:
- file: Image file

Response:
{
  "predictions": [
    {
      "label": "Disease A",
      "confidence": 0.85
    },
    {
      "label": "Disease B", 
      "confidence": 0.10
    },
    {
      "label": "Disease C",
      "confidence": 0.05
    }
  ]
}
```

#### 2. Disease Explanation (Optional)
```
POST /explain
Content-Type: application/json

Request:
{
  "disease": "Disease Name",
  "confidence": 0.85
}

Response:
{
  "explanation": "Detailed disease explanation..."
}
```

## Adding OpenAI API for Explanations

To use OpenAI for dynamic explanations:

1. Install OpenAI package in your backend:
```bash
pip install openai
```

2. Update `/explain` endpoint in your FastAPI backend:
```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/explain")
async def explain_disease(data: dict):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": "You are a medical assistant explaining skin diseases."
            },
            {
                "role": "user",
                "content": f"Explain {data['disease']} with {data['confidence']*100:.1f}% confidence"
            }
        ]
    )
    return {"explanation": response.choices[0].message.content}
```

3. Add to your backend `.env`:
```
OPENAI_API_KEY=your-key-here
```

## UI Components

### Sidebar
- New Chat button
- Previous chats history
- Delete chat functionality
- Currently active chat highlight

### Chat Window
- Scrollable message area
- User messages (right-aligned, blue)
- Assistant messages (left-aligned, dark)
- Typing animation for responses
- Image preview support

### Message Types
- **Text**: Regular AI/user messages with typing animation
- **Image**: User uploaded images with preview
- **Prediction**: Disease predictions with confidence scores

### InputBox
- Image upload with drag-and-drop
- Multiline text input
- Send button
- Image preview with remove option

## Styling

- **Framework**: Tailwind CSS v4
- **Theme**: Dark mode (slate/dark palette)
- **Colors**: 
  - Primary: Blue-600
  - Background: Dark-900
  - Borders: Dark-700
  - Text: Dark-100

## State Management

Uses React hooks for state management:
- `useState`: Chat state, current chat, loading state
- `useEffect`: LocalStorage persistence, auto-scroll
- `useCallback`: Memoized functions for performance
- `useRef`: DOM references for scroll behavior

## Error Handling

- Backend API errors gracefully show error messages
- Image upload validation (type & size)
- Network error handling with user feedback
- Mock explanations as fallback when API unavailable

## Performance Optimizations

- Image lazy loading
- Smooth scrolling with refs
- Optimized re-renders with useCallback
- LocalStorage caching for chat history
- Debounced typing animations

## Browser Support

- Chrome/Chromium (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000` | Backend API URL |
| `VITE_MOCK_MODE` | `false` | Use mock data when true |

## Keyboard Shortcuts

- `Enter` - Send message
- `Shift + Enter` - New line in text input

## Next Steps

1. Connect your FastAPI backend
2. Set up disease detection model
3. Configure OpenAI API for explanations
4. Deploy to production
5. Add authentication (optional)
6. Implement chat export/sharing

## License

MIT
