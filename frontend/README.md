# EVE Frontend

Next.js + React + Tailwind UI for EVE

## Run

```bash
npm install
npm run dev
```

Open http://localhost:3000

## Environment

Create `.env.local`:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000
```

## Components

- `RecordingPanel` - Audio recording/upload + transcription
- `TasksPanel` - Extracted tasks display
- `SummaryPanel` - Meeting summary + voice playback
- `Dashboard` - Analytics

## API Integration

All API calls in components use:
```typescript
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
```

Uses `axios` for HTTP requests.

