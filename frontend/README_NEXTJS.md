# Ornina AI Avatar - Next.js Frontend

Professional interactive AI avatar call center system built with Next.js, TypeScript, and LiveKit.

## Features

- 🎥 **Real-time Video Calls** - HD video with LiveKit
- 🤖 **AI Avatar Integration** - Tavus video avatars
- 💬 **Live Chat** - Text messaging during calls
- 🎙️ **Voice Communication** - Arabic and English support
- 📊 **Call Analytics** - Duration tracking and recording
- 🎨 **Modern UI** - Glassmorphism design matching screen.png
- 📱 **Responsive** - Works on desktop and mobile

## Tech Stack

- **Framework**: Next.js 14 (React 18)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Real-time**: LiveKit Client SDK
- **Video**: Tavus AI Avatars
- **Backend**: Python LiveKit Agents (../avatary/)

## Project Structure

```
frontend/
├── components/          # React components
│   ├── VideoCallInterface.tsx
│   ├── ChatPanel.tsx
│   ├── ControlBar.tsx
│   ├── ParticipantThumbnail.tsx
│   └── CallInfo.tsx
├── pages/              # Next.js pages
│   ├── _app.tsx
│   ├── _document.tsx
│   ├── index.tsx       # Landing page
│   └── call.tsx        # Video call page
├── lib/                # Utilities
│   ├── livekit.ts      # LiveKit connection
│   └── api.ts          # Backend API calls
├── styles/             # Global styles
│   └── globals.css
└── public/             # Static assets
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd /var/www/avatar\ /frontend
npm install
```

### 2. Configure Environment

Create `.env.local` file:

```env
# LiveKit Configuration (get from your backend)
NEXT_PUBLIC_LIVEKIT_URL=wss://your-livekit-server.com
NEXT_PUBLIC_LIVEKIT_API_KEY=your-api-key
NEXT_PUBLIC_LIVEKIT_API_SECRET=your-api-secret

# Ornina Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Enable Tavus video avatars
NEXT_PUBLIC_TAVUS_ENABLED=true
```

### 3. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### 4. Build for Production

```bash
npm run build
npm start
```

## Usage

### Basic Flow

1. **Landing Page** (`/`)
   - Enter your name
   - Optionally enter room code
   - Click "Start Call"

2. **Video Call** (`/call`)
   - See AI avatar video
   - Your video in top-right thumbnail
   - Chat panel in bottom-left
   - Controls at bottom-center

### Controls

- **🎙️ Microphone**: Toggle mute/unmute
- **📹 Camera**: Toggle video on/off
- **💬 Chat**: Show/hide chat panel
- **⚙️ Settings**: Call settings (future)
- **📞 End Call**: Disconnect and return home

### Chat Features

- Send text messages
- Receive AI responses
- Bilingual support (Arabic/English)
- Timestamps on all messages

## Integration with Backend

The frontend connects to the Ornina AI Avatar backend at `/var/www/avatar /avatary/`:

### LiveKit Connection

```typescript
import { connectToRoom } from '@/lib/livekit'

const room = await connectToRoom({
  roomName: 'ornina-room',
  userName: 'User Name',
  apiUrl: 'http://localhost:8000'
})
```

### API Endpoints Expected

The frontend expects these endpoints from the backend:

- `POST /api/token` - Get LiveKit access token
- `GET /api/conversations` - List conversations
- `GET /api/conversations/:id` - Get conversation details
- `POST /api/knowledge-base/search` - Search knowledge base
- `GET /api/services` - Get company services
- `GET /api/training` - Get training programs

## Customization

### Branding

Update colors in `tailwind.config.js`:

```javascript
colors: {
  primary: '#0b73da',        // Your brand color
  'background-light': '#f5f7f8',
  'background-dark': '#101922',
}
```

### Language

The app supports RTL (Arabic) by default. Change in `pages/_document.tsx`:

```typescript
<Html lang="ar" dir="rtl">  // Arabic RTL
<Html lang="en" dir="ltr">  // English LTR
```

### UI Components

All components are in `components/` and can be customized:

- `VideoCallInterface.tsx` - Main call layout
- `ChatPanel.tsx` - Chat messages and input
- `ControlBar.tsx` - Bottom controls
- `ParticipantThumbnail.tsx` - Video thumbnail
- `CallInfo.tsx` - Timer and recording indicator

## Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Docker

```dockerfile
FROM node:18-alpine

WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY . .
RUN npm run build

EXPOSE 3000
CMD ["npm", "start"]
```

### Manual Deploy

```bash
npm run build
# Copy .next/ folder to production server
# Run: npm start
```

## Troubleshooting

### LiveKit Connection Failed

- Check `NEXT_PUBLIC_LIVEKIT_URL` is correct
- Verify backend is running
- Check firewall allows WebSocket connections

### Video Not Showing

- Allow camera permissions in browser
- Check browser console for errors
- Verify LiveKit room is active

### Chat Not Working

- Check browser console for errors
- Verify WebSocket connection
- Check backend API is accessible

## Performance

- **First Load**: ~150KB gzipped
- **Video Quality**: Adaptive (up to 720p)
- **Latency**: < 100ms (local network)
- **Browser Support**: Chrome, Firefox, Safari, Edge

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ❌ Internet Explorer (not supported)

## Development

### Add New Component

```bash
# Create component
touch components/MyComponent.tsx

# Use in page
import MyComponent from '@/components/MyComponent'
```

### Debugging

```bash
# Enable verbose logging
export DEBUG=livekit*

# Run with inspector
NODE_OPTIONS='--inspect' npm run dev
```

## Support

For issues or questions:

- **GitHub**: [Report an issue]
- **Email**: support@ornina.com
- **Phone**: 3349028 (Damascus, Syria)
- **Location**: المزرعة - مقابل وزارة التربية

## License

Proprietary - Ornina © 2025

---

**Made with ❤️ by Ornina AI Team**
**شركة أورنينا للذكاء الاصطناعي والحلول الرقمية**
