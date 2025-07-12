# ChzzkStreamDeck v2.0

**CHZZK Streaming Widget System**

A comprehensive streaming widget system for OBS Studio with real-time chat overlay, Spotify integration, and music bot functionality.

## Features

### Core Modules
- **Chat Module**: Real-time CHZZK chat integration with WebSocket connection
- **Spotify Module**: Music information display and playback control
- **Music Bot**: Chat command-based Spotify control system
- **Server-based Token Management**: Centralized token sharing between dashboard and OBS browser sources

### Chat System
- Real-time chat overlay with SSE (Server-Sent Events)
- CHZZK emoticon support
- Customizable message display duration
- Multiple alignment options (left, center, right)
- Automatic message cleanup and fade effects
- Theme support (Simple Purple, Neon Green)

### Spotify Integration
- OAuth 2.0 Authorization Code Flow authentication
- Current track information display
- Playback control (play/pause, next, previous)
- Queue management through chat commands
- Server-based token storage for OBS compatibility

### Music Bot Commands
- `!노래추가 [keyword]` - Add song to Spotify queue
- `!건너뛰기` - Skip current track
- `!현재곡` - Show current playing track
- `!대기열` - Display upcoming tracks

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Server
```bash
node server.js
```

### 3. Access Dashboard
- **Main Dashboard**: http://localhost:7112
- **Chat Overlay**: http://localhost:7112/chat-overlay.html
- **Spotify Widget**: http://localhost:7112/spotify-widget.html

## Project Structure

```
ChzzkStreamDeck/
├── src/
│   ├── chat-client.js           # CHZZK chat client
│   ├── chat-overlay.html        # Chat overlay for OBS
│   └── spotify-widget.html      # Spotify widget for OBS
├── js/
│   ├── modules/
│   │   ├── chat.js              # Chat module
│   │   ├── spotify.js           # Spotify module
│   │   └── musicbot.js          # Music bot module
│   ├── utils/
│   │   ├── settings.js          # Settings management
│   │   └── ui.js                # UI utilities
│   └── main.js                  # Main application
├── css/
│   ├── components.css           # Component styles
│   ├── main.css                 # Main styles
│   └── themes.css               # Theme definitions
├── server.js                    # Main backend server
├── index.html                   # Main dashboard
└── package.json                 # Project configuration
```

## Configuration

### Chat Module Setup
1. Open dashboard at http://localhost:7112
2. Enter CHZZK Channel ID (32-character alphanumeric)
3. Configure display settings (theme, duration, alignment)
4. Click "Start Chat" to begin monitoring

### Spotify Module Setup
1. Create Spotify application at https://developer.spotify.com/dashboard
2. Set redirect URI to `http://localhost:7112/spotify/callback`
3. Enter Client ID and Client Secret in dashboard
4. Click "Authenticate" to complete OAuth flow
5. Ensure Spotify Premium account for full functionality

### Music Bot Setup
1. Ensure both Chat and Spotify modules are active
2. Enable Music Bot in dashboard
3. Customize command keywords if needed
4. Music bot will automatically respond to chat commands

## OBS Integration

### Chat Overlay
1. Add Browser Source in OBS
2. Set URL: `http://localhost:7112/chat-overlay.html`
3. Dimensions: 400x600px recommended
4. CSS: `body { background: transparent !important; }`

### Spotify Widget
1. Add Browser Source in OBS
2. Set URL: `http://localhost:7112/spotify-widget.html`
3. Dimensions: 300x100px recommended
4. Widget automatically syncs with dashboard authentication

## API Endpoints

### Chat Management
- `POST /api/chat/start` - Start chat monitoring
- `POST /api/chat/stop` - Stop chat monitoring
- `GET /api/chat/stream` - Real-time chat stream (SSE)
- `GET /api/chat/messages` - Retrieve chat messages

### Spotify Management
- `GET /api/spotify/token` - Check token status
- `POST /api/spotify/token` - Save authentication token
- `DELETE /api/spotify/token` - Clear authentication token
- `POST /api/spotify/refresh` - Refresh access token
- `GET /api/spotify/current-track` - Get current playing track
- `POST /api/spotify/next` - Skip to next track
- `POST /api/spotify/previous` - Skip to previous track
- `POST /api/spotify/play` - Toggle play/pause

### Server Status
- `GET /api/status` - Get server and module status

## Requirements

### System Requirements
- Node.js 14.0.0 or higher
- npm 6.0.0 or higher
- Modern browser with ES6+ support

### Spotify Requirements
- Spotify Premium account (required for queue management)
- Active Spotify device (app must be playing music)
- Valid Spotify Developer application

### CHZZK Requirements
- Valid CHZZK channel ID
- Active live stream for real-time chat

## Theme System

### Simple Purple
- Purple gradient background (#667eea, #764ba2)
- Advanced animation effects
- Hover effects and transitions
- Multi-layer shadows and glow effects

### Neon Green
- Cyberpunk-style neon green theme
- Glowing effects and animations
- High contrast design

## Troubleshooting

### Common Issues

#### "App update required for normal viewing"
- **Cause**: Stream is not live or incorrect channel ID
- **Solution**: Verify channel ID of active live stream

#### Chat messages not appearing
- **Cause**: Server connection issues or API limitations
- **Solution**: 
  1. Check server status at `/api/status`
  2. Verify browser console for errors
  3. Confirm firewall settings

#### Spotify authentication fails
- **Cause**: Incorrect client credentials or callback URL
- **Solution**:
  1. Verify Client ID and Client Secret
  2. Ensure redirect URI matches dashboard settings
  3. Check popup blocker settings

#### Music bot commands not working
- **Cause**: Missing Premium account or inactive device
- **Solution**:
  1. Upgrade to Spotify Premium
  2. Start music playback in Spotify app
  3. Verify authentication in dashboard

#### Queue management fails (403 error)
- **Cause**: Spotify Premium required or no active device
- **Solution**:
  1. Ensure Premium account subscription
  2. Open Spotify app and start playing music
  3. Verify device is active and visible

## Development

### Running in Development Mode
```bash
# Start server with debugging
node server.js

# Run chat client directly
node src/chat-client.js <CHANNEL_ID>

# Enable verbose logging
node src/chat-client.js <CHANNEL_ID> --verbose
```

### Module Development
Each module is independently developed and can be extended:
- Chat Module: `js/modules/chat.js`
- Spotify Module: `js/modules/spotify.js`
- Music Bot Module: `js/modules/musicbot.js`

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/NewFeature`)
3. Commit changes (`git commit -m 'Add NewFeature'`)
4. Push to branch (`git push origin feature/NewFeature`)
5. Create Pull Request

## Acknowledgments

- CHZZK API for real-time chat data
- Spotify Web API for music integration
- OBS Studio for streaming capabilities
- Node.js community for excellent ecosystem

---

For technical support and bug reports, please create an issue in the repository. 