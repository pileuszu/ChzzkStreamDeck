# Troubleshooting Guide

## Common Issues and Solutions

### Chat Module Issues

#### "App update required for normal viewing" Error
**Cause**: Stream is not live or incorrect channel ID
**Solution**:
1. Verify the channel is currently live streaming
2. Check the channel ID is exactly 32 characters (alphanumeric)
3. Test with a different active channel ID

#### Chat messages not appearing
**Cause**: Server connection issues or API limitations
**Solution**:
1. Check server status at `http://localhost:7112/api/status`
2. Verify browser console for errors
3. Confirm firewall settings allow port 7112
4. Restart server and try again

#### WebSocket connection fails
**Cause**: Network issues or server overload
**Solution**:
1. Test with different channel ID
2. Disable VPN if active
3. Check network connectivity to CHZZK servers
4. Restart server after 5-10 minutes

#### Chat overlay not updating in OBS
**Cause**: OBS browser source configuration
**Solution**:
1. Verify URL is correct: `http://localhost:7112/chat-overlay.html`
2. Check "Refresh browser when scene becomes active" is disabled
3. Ensure "Shutdown source when not visible" is disabled
4. Add CSS: `body { background: transparent !important; }`

### Spotify Module Issues

#### Authentication fails
**Cause**: Incorrect client credentials or callback URL
**Solution**:
1. Verify Client ID and Client Secret from Spotify Developer Dashboard
2. Ensure redirect URI is set to `http://localhost:7112/spotify/callback`
3. Check popup blocker is disabled
4. Clear browser cache and cookies

#### "Invalid redirect URI" error
**Cause**: Mismatch between configured and actual redirect URI
**Solution**:
1. In Spotify Developer Dashboard, go to your app settings
2. Add `http://localhost:7112/spotify/callback` to redirect URIs
3. Save settings and retry authentication

#### Token expires frequently
**Cause**: Server-side token refresh issues
**Solution**:
1. Check Client Secret is correctly configured
2. Verify refresh token is being saved
3. Check server logs for refresh token errors
4. Re-authenticate if refresh token is invalid

#### Spotify widget not showing in OBS
**Cause**: Authentication not shared between dashboard and widget
**Solution**:
1. Authenticate in main dashboard first
2. Wait for "Token saved to server" confirmation
3. Add OBS browser source: `http://localhost:7112/spotify-widget.html`
4. Check server logs for token sharing issues

### Music Bot Issues

#### Commands not responding
**Cause**: Prerequisites not met or module not active
**Solution**:
1. Ensure Chat Module is active and connected
2. Verify Spotify Module is authenticated
3. Check Music Bot is enabled in dashboard
4. Confirm both modules show "Active" status

#### Queue management fails (403 error)
**Cause**: Spotify Premium required or no active device
**Solution**:
1. Upgrade to Spotify Premium account
2. Open Spotify app and start playing music
3. Verify device appears as active in Spotify
4. Check Spotify app has queue management permissions

#### "No active device" error
**Cause**: Spotify app not running or no music playing
**Solution**:
1. Open Spotify desktop app or mobile app
2. Start playing any song
3. Verify device appears in Spotify Connect
4. Ensure device is not set to private session

#### Search returns no results
**Cause**: Network issues or search query problems
**Solution**:
1. Check internet connection
2. Try simpler search terms
3. Verify Spotify API access token is valid
4. Check server logs for API response errors

### Server Issues

#### "EADDRINUSE" error on startup
**Cause**: Port 7112 already in use
**Solution**:
1. Check if another instance is running:
   ```bash
   netstat -ano | findstr :7112
   ```
2. Kill existing process:
   ```bash
   taskkill /F /PID <process_id>
   ```
3. Restart server

#### "Cannot GET /api/endpoint" errors
**Cause**: Route ordering or server initialization issues
**Solution**:
1. Ensure server is fully started before accessing APIs
2. Check server logs for initialization errors
3. Verify all required dependencies are installed
4. Restart server completely

#### SSE connection drops frequently
**Cause**: Network instability or server resource issues
**Solution**:
1. Check server resource usage (CPU, memory)
2. Verify network stability
3. Increase server timeout settings if needed
4. Check for firewall interference

### General Troubleshooting

#### Server won't start
**Cause**: Missing dependencies or port conflicts
**Solution**:
1. Install dependencies: `npm install`
2. Check Node.js version (14.0.0 or higher)
3. Verify port 7112 is available
4. Check for permission issues

#### Settings not persisting
**Cause**: localStorage issues or browser restrictions
**Solution**:
1. Enable localStorage in browser settings
2. Disable private/incognito mode
3. Clear browser cache and reload
4. Check browser console for storage errors

#### OBS browser source shows blank page
**Cause**: URL incorrect or server not running
**Solution**:
1. Verify server is running at `http://localhost:7112`
2. Test URL in regular browser first
3. Check OBS browser source settings
4. Ensure no typos in URL

## Testing and Debugging

### Manual Testing

#### Test Chat Module
```bash
# Test chat client directly
node src/chat-client.js <CHANNEL_ID>

# Test with verbose logging
node src/chat-client.js <CHANNEL_ID> --verbose
```

#### Test Server APIs
```bash
# Check server status
curl http://localhost:7112/api/status

# Test Spotify token
curl http://localhost:7112/api/spotify/token

# Test chat stream
curl http://localhost:7112/api/chat/stream
```

### Debug Mode

#### Enable Debug Logging
Set environment variable for detailed logs:
```bash
# Windows
set DEBUG=*
node server.js

# Linux/Mac
DEBUG=* node server.js
```

#### Browser Console Debugging
1. Open browser developer tools (F12)
2. Check Console tab for errors
3. Monitor Network tab for failed requests
4. Check Application tab for localStorage issues

### Log Files

#### Server Logs
- Monitor server console output
- Check for connection errors
- Verify API response codes
- Watch for authentication failures

#### Browser Logs
- Check browser console for JavaScript errors
- Monitor network requests and responses
- Verify localStorage data persistence
- Check for CORS or permission issues

## Network Requirements

### Firewall Settings
- Allow inbound connections on port 7112
- Allow outbound connections to:
  - `api.chzzk.naver.com` (CHZZK API)
  - `accounts.spotify.com` (Spotify Auth)
  - `api.spotify.com` (Spotify API)

### Proxy Configuration
If using a proxy server:
1. Configure proxy settings in your system
2. Ensure proxy allows WebSocket connections
3. Check proxy doesn't block required domains

## Getting Help

### Information to Include
When reporting issues, include:
- Server logs and error messages
- Browser console logs
- System information (OS, Node.js version)
- Steps to reproduce the issue
- Expected vs actual behavior

### Common Solutions Summary
1. **Server issues**: Restart server, check port conflicts
2. **Auth issues**: Verify credentials, clear cache
3. **Chat issues**: Check channel ID, verify stream is live
4. **Spotify issues**: Ensure Premium account, active device
5. **Music bot issues**: Verify both modules are active
6. **OBS issues**: Check URL, browser source settings

For persistent issues, check the project repository for updates and known issues. 