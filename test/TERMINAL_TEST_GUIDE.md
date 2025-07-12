# Testing Guide

## Overview

This guide covers testing and debugging procedures for the ChzzkStreamDeck system components.

## System Testing

### Server Testing

#### Start Server
```bash
node server.js
```

#### Test Server Status
```bash
# Check if server is running
curl http://localhost:7112/api/status

# Expected response:
{
  "success": true,
  "status": {
    "chat": { "active": false, "pid": null, "port": 8002, "messageCount": 0 },
    "spotify": { "active": false, "pid": null, "port": 8001, "hasToken": false, "tokenExpired": true },
    "server": { "port": 7112, "sseConnections": 0 }
  }
}
```

### Chat Module Testing

#### Direct Chat Client Test
```bash
# Test chat client directly
node src/chat-client.js <CHANNEL_ID>

# Test with verbose output
node src/chat-client.js <CHANNEL_ID> --verbose
```

#### Example with Channel ID
```bash
node src/chat-client.js 255a2ea465c44920aa3e93b8d60a72e0
```

#### Expected Output
```
CHZZK Chat Client started
Channel ID: 255a2ea465c44920aa3e93b8d60a72e0
✓ Channel info acquired
✓ Access token acquired
✓ WebSocket connected
Listening for chat messages...
[Username1] Hello everyone!
[Username2] Great stream!
```

### Spotify Module Testing

#### Test Authentication
1. Open dashboard at http://localhost:7112
2. Navigate to Spotify settings
3. Enter Client ID and Client Secret
4. Click "Authenticate"
5. Complete OAuth flow in popup

#### Test Token Management
```bash
# Check token status
curl http://localhost:7112/api/spotify/token

# Expected response:
{
  "success": true,
  "hasToken": true,
  "isExpired": false,
  "expiryTime": 1703875571000,
  "token": "BQB..."
}
```

#### Test Current Track
```bash
# Get current playing track
curl http://localhost:7112/api/spotify/current-track

# Expected response:
{
  "success": true,
  "isPlaying": true,
  "track": {
    "name": "Song Name",
    "artist": "Artist Name",
    "album": "Album Name",
    "duration": 210000,
    "progress": 45000,
    "image": "https://..."
  }
}
```

### Music Bot Testing

#### Prerequisites
1. Ensure Chat Module is active
2. Verify Spotify Module is authenticated
3. Enable Music Bot in dashboard

#### Test Commands
Send these messages in the connected chat:
```
!노래추가 아이유 밤편지
!건너뛰기
!현재곡
!대기열
```

#### Expected Responses
```
@Username 🎵 "밤편지" by 아이유 곡이 대기열에 추가되었습니다!
@Username ⏭️ 현재 곡을 건너뛰었습니다.
@Username 🎵 현재 재생 중: "밤편지" by 아이유 [1:23/3:45]
@Username 📋 대기열 (다음 2곡): 1. Song1 by Artist1 | 2. Song2 by Artist2
```

## OBS Integration Testing

### Chat Overlay Testing

#### Setup
1. Add Browser Source in OBS
2. URL: `http://localhost:7112/chat-overlay.html`
3. Width: 400, Height: 600
4. CSS: `body { background: transparent !important; }`

#### Test Steps
1. Start chat module from dashboard
2. Send test messages in chat
3. Verify messages appear in OBS overlay
4. Test theme changes from dashboard
5. Verify theme changes apply to overlay

### Spotify Widget Testing

#### Setup
1. Add Browser Source in OBS
2. URL: `http://localhost:7112/spotify-widget.html`
3. Width: 300, Height: 100

#### Test Steps
1. Authenticate Spotify in dashboard
2. Start playing music in Spotify app
3. Verify widget shows current track
4. Test control buttons (play/pause, next, previous)
5. Verify widget updates when track changes

## Debugging

### Enable Debug Mode

#### Server Debug
```bash
# Windows
set DEBUG=* && node server.js

# Linux/Mac
DEBUG=* node server.js
```

#### Chat Client Debug
```bash
# Windows
set DEBUG=* && node src/chat-client.js <CHANNEL_ID>

# Linux/Mac
DEBUG=* node src/chat-client.js <CHANNEL_ID>
```

### Browser Console Testing

#### Dashboard Testing
1. Open http://localhost:7112
2. Open browser developer tools (F12)
3. Check Console tab for errors
4. Monitor Network tab for API calls

#### Overlay Testing
1. Open http://localhost:7112/chat-overlay.html
2. Open browser developer tools (F12)
3. Check Console tab for errors
4. Monitor for SSE connection status

### Log Analysis

#### Server Logs
Monitor server console output for:
- API request/response codes
- WebSocket connection status
- Authentication success/failure
- Token refresh attempts

#### Browser Logs
Check browser console for:
- JavaScript errors
- Network request failures
- LocalStorage access issues
- SSE connection problems

## Common Test Scenarios

### Scenario 1: Full System Test
1. Start server
2. Authenticate Spotify
3. Start chat module
4. Enable music bot
5. Test all chat commands
6. Verify OBS overlays work

### Scenario 2: Authentication Test
1. Clear all tokens
2. Test Spotify authentication
3. Verify token sharing between dashboard and widget
4. Test token refresh functionality

### Scenario 3: Connection Recovery Test
1. Start all modules
2. Disconnect network
3. Reconnect network
4. Verify automatic reconnection
5. Test continued functionality

### Scenario 4: Error Handling Test
1. Test with invalid channel ID
2. Test with expired Spotify tokens
3. Test with no active Spotify device
4. Test with invalid music bot commands

## Finding Channel IDs

### Method 1: Browser URL
1. Visit CHZZK live stream
2. Copy channel ID from URL
3. Format: `https://chzzk.naver.com/live/[32-character-id]`

### Method 2: Developer Tools
1. Open browser developer tools (F12)
2. Go to Network tab
3. Look for API calls containing channel ID
4. Copy 32-character alphanumeric ID

## Performance Testing

### Load Testing
```bash
# Test multiple connections
node src/chat-client.js <CHANNEL_ID> &
node src/chat-client.js <CHANNEL_ID> &
node src/chat-client.js <CHANNEL_ID> &
```

### Memory Usage
Monitor server memory usage during extended operation:
```bash
# Check Node.js process memory
ps aux | grep node
```

### Connection Stability
Test long-running connections:
1. Start all modules
2. Leave running for several hours
3. Monitor for connection drops
4. Verify automatic reconnection

## API Testing

### Manual API Tests
```bash
# Test all endpoints
curl http://localhost:7112/api/status
curl http://localhost:7112/api/chat/messages
curl http://localhost:7112/api/spotify/token
curl http://localhost:7112/api/spotify/current-track
```

### Automated Testing
Create test scripts for regular API validation:
```javascript
// Example test script
const fetch = require('node-fetch');

async function testAPI() {
    const response = await fetch('http://localhost:7112/api/status');
    const data = await response.json();
    console.log('API Status:', data.success ? 'OK' : 'FAIL');
}
```

## Troubleshooting Common Issues

### "Channel not found" Error
- Verify channel ID is exactly 32 characters
- Ensure channel is currently live
- Try different active channel

### "Token expired" Error
- Re-authenticate Spotify in dashboard
- Check Client ID/Secret configuration
- Verify redirect URI settings

### "No active device" Error
- Open Spotify app
- Start playing music
- Verify device appears in Spotify Connect

### Connection Drops
- Check network stability
- Verify firewall settings
- Monitor server resource usage

## Test Data

### Sample Channel IDs
Use these for testing (verify they're currently live):
- Large channel: `255a2ea465c44920aa3e93b8d60a72e0`
- Medium channel: `[find active channel]`
- Small channel: `[find active channel]`

### Sample Spotify Credentials
Create your own at https://developer.spotify.com/dashboard:
- Client ID: (your app's client ID)
- Client Secret: (your app's client secret)
- Redirect URI: `http://localhost:7112/spotify/callback`

## Best Practices

### Testing Guidelines
1. Always test with live channels
2. Verify all modules are active before testing
3. Check logs for errors during testing
4. Test both success and failure scenarios
5. Verify OBS integration regularly

### Security Considerations
1. Never commit actual Spotify credentials
2. Use test accounts for development
3. Regularly rotate test credentials
4. Monitor API usage limits

This guide should be updated as new features are added to the system. 