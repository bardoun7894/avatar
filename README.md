# Avatar Project

This project contains an avatar-based video calling application.

## Structure

- `frontend/` - Next.js frontend application
- `avatary/` - Avatar-related components and assets
- `agent.py` - Python agent for avatar interactions
- `avatar_data_structure.json` - Data structure for avatar configuration
- `avatar_parsed.json` - Parsed avatar data

## Getting Started

### Frontend

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

Create a `.env.local` file based on `.env.example` and configure your environment variables.

Run the development server:

```bash
npm run dev
```

### Backend

Run the Python agent:

```bash
python agent.py
```

## Features

- Video calling interface
- Avatar integration
- Real-time communication
- Chat functionality
