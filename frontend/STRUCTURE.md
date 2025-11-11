# Frontend Application Structure

This frontend has been reorganized to clearly separate the two main applications: **Avatar** and **Call Center**.

## Directory Structure

```
frontend/
├── apps/
│   ├── avatar/                    # Avatar Video Application
│   │   ├── components/            # Avatar-specific React components
│   │   │   ├── ChatPanel.tsx      # Chat interface for video calls
│   │   │   ├── ControlBar.tsx     # Call controls (mute, video, etc)
│   │   │   ├── ParticipantThumbnail.tsx  # Local video thumbnail
│   │   │   ├── VideoCallInterface.tsx    # Main video interface
│   │   │   └── CallInfo.tsx       # Call information display
│   │   └── pages/                 # Avatar app pages
│   │       ├── index.tsx          # Home page
│   │       └── call.tsx           # Video call page
│   │
│   ├── callcenter/                # Call Center Application
│   │   ├── components/            # Call Center-specific components
│   │   │   └── (to be added)
│   │   └── pages/                 # Call Center app pages
│   │       ├── callcenter.tsx     # Call Center home
│   │       ├── call-with-audio.tsx        # Audio call interface
│   │       ├── agent-dashboard.tsx        # Agent dashboard
│   │       ├── crm-dashboard.tsx          # CRM dashboard
│   │       └── call.tsx           # Call routing
│   │
│   └── shared/                    # Shared Resources (used by both apps)
│       ├── pages/                 # Shared Next.js pages
│       │   ├── _app.tsx           # App wrapper
│       │   └── _document.tsx      # HTML document
│       ├── api/                   # Shared API routes
│       │   ├── token.ts           # LiveKit token generation
│       │   └── dispatch-agent.ts  # Agent dispatch
│       ├── styles/                # Global styles
│       │   └── globals.css
│       ├── lib/                   # Shared utilities
│       │   ├── livekit.ts         # LiveKit configuration
│       │   └── api.ts             # API utilities
│       └── hooks/                 # Shared React hooks
│           └── useCallCenterAPI.ts
│
├── public/                        # Static assets
├── node_modules/                  # Dependencies
├── package.json
├── next.config.js
├── tsconfig.json
└── tailwind.config.js
```

## Application Overview

### 🎬 Avatar App (`apps/avatar/`)
- **Purpose**: AI Video Avatar interaction
- **Key Pages**:
  - `/` - Home page
  - `/call` - Video call interface with AI avatar
- **Features**:
  - Real-time video streaming with AI avatar
  - Chat panel for conversation
  - Call controls (mute, video toggle)
  - Participant view
  - Call duration tracking

### 📞 Call Center App (`apps/callcenter/`)
- **Purpose**: Customer service call management
- **Key Pages**:
  - `/callcenter` - Call Center home/main menu
  - `/callcenter/call-with-audio` - Audio-based customer calls
  - `/callcenter/agent-dashboard` - Agent monitoring and management
  - `/callcenter/crm-dashboard` - Customer relationship management
- **Features**:
  - IVR (Interactive Voice Response) system
  - Agent dashboard for call monitoring
  - CRM integration
  - Customer call history

### 🔗 Shared Resources (`apps/shared/`)
- **Purpose**: Common functionality used by both apps
- **Contents**:
  - Global app configuration (`_app.tsx`, `_document.tsx`)
  - Shared API routes (token generation, agent dispatch)
  - Common styling and utilities
  - Shared React hooks
  - LiveKit configuration

## Backend Applications

This frontend works with two separate backend applications:

### 1. **Avatary** (`/avatary/`)
- Handles AI avatar generation and video streaming
- REST API for avatar interactions

### 2. **Call Center** (`/callCenter/`)
- Handles call management, IVR, and agent logistics
- REST API for call operations

## How to Use

### Development
```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Adding New Components

**For Avatar App:**
```
apps/avatar/components/NewComponent.tsx
```
Import from shared utilities:
```tsx
import { useCallCenterAPI } from '@/apps/shared/hooks/useCallCenterAPI'
import { API_BASE_URL } from '@/apps/shared/lib/api'
```

**For Call Center App:**
```
apps/callcenter/components/NewComponent.tsx
```

**For Shared Components:**
```
apps/shared/components/NewComponent.tsx (if needed)
```

## Environment Variables

Configure in `.env.local`:
```
NEXT_PUBLIC_LIVEKIT_URL=ws://localhost:7880
NEXT_PUBLIC_API_URL=http://localhost:3000
```

## Notes

- **API Routes**: Next.js API routes in `apps/shared/api/` are automatically served at `/api/*`
- **Imports**: Use path aliases configured in `tsconfig.json` (e.g., `@/apps/...`)
- **Styles**: Global styles are in `apps/shared/styles/globals.css`
- **Static Files**: Place public assets in `public/` directory

## Migration Status

- ✅ Avatar components separated
- ✅ Call Center pages organized
- ✅ Shared resources consolidated
- ⏳ Import paths to be updated in components
- ⏳ Test and verify both applications work correctly
