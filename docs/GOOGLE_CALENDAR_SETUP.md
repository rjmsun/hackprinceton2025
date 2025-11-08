# Google Calendar OAuth Setup

## ✅ What's Already Done

1. ✅ Client ID added to `env.example`: `329625451973-fmvvbtmr1mu2n98m3l6vah6q3td8eki1.apps.googleusercontent.com`
2. ✅ OAuth endpoints added to backend:
   - `GET /calendar/auth` - Get authorization URL
   - `GET /calendar/callback` - Handle OAuth callback
3. ✅ Calendar service updated with OAuth flow

## 🔧 What You Need to Do

### Step 1: Get Your Client Secret

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Credentials**
3. Find your OAuth 2.0 Client ID: `329625451973-fmvvbtmr1mu2n98m3l6vah6q3td8eki1`
4. Click on it to view details
5. **Copy the Client Secret** (it's partially masked like `****4dH1`)

### Step 2: Add Client Secret to `.env`

```bash
# Edit your .env file
nano .env
```

Add/update:
```bash
GOOGLE_CLIENT_ID=329625451973-fmvvbtmr1mu2n98m3l6vah6q3td8eki1.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=YOUR_ACTUAL_CLIENT_SECRET_HERE
```

### Step 3: Add Authorized Redirect URI

In Google Cloud Console (same page as Step 1):

1. Scroll to **"Authorized redirect URIs"** section
2. Click **"+ Add URI"**
3. Add these URIs:

**For local development:**
```
http://localhost:3000/auth/google/callback
```

**For production (if deploying):**
```
https://your-deployed-url.vercel.app/auth/google/callback
```

4. Click **"Save"**

⚠️ **Important:** It may take 5 minutes to a few hours for settings to take effect.

### Step 4: Enable Google Calendar API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Navigate to **APIs & Services** → **Library**
3. Search for "Google Calendar API"
4. Click **Enable**

## 🧪 Testing the OAuth Flow

### 1. Start Backend

```bash
cd backend
python main.py
```

### 2. Test Authorization URL

Visit: http://localhost:8000/calendar/auth

Should return:
```json
{
  "auth_url": "https://accounts.google.com/o/oauth2/auth?...",
  "redirect_uri": "http://localhost:3000/auth/google/callback"
}
```

### 3. Test Full Flow

1. Open the `auth_url` from step 2 in your browser
2. Sign in with Google
3. Grant calendar permissions
4. You'll be redirected to: `http://localhost:3000/auth/google/callback?code=...`
5. Backend will exchange code for token and redirect to: `http://localhost:3000/auth/success?access_token=...`

## 📝 Frontend Integration (Next Steps)

You'll need to:

1. **Create auth page** that calls `/calendar/auth` to get the auth URL
2. **Redirect user** to Google's OAuth page
3. **Handle callback** at `/auth/google/callback` (backend handles this)
4. **Store access token** from success page
5. **Use token** when calling `/calendar/schedule`

Example frontend code:
```typescript
// Get auth URL
const response = await axios.get(`${API_URL}/calendar/auth`);
window.location.href = response.data.auth_url;

// After redirect, token will be in URL params
// Extract from: /auth/success?access_token=...
```

## 🔒 Security Notes

- ⚠️ Currently tokens are passed in URL (OK for demo)
- ✅ For production, use secure HTTP-only cookies or session storage
- ✅ Never commit `.env` with real secrets
- ✅ Rotate secrets if exposed

## 🐛 Troubleshooting

**"redirect_uri_mismatch"**
- Check redirect URI matches exactly in Google Console
- Must include `http://localhost:3000/auth/google/callback` (no trailing slash)

**"invalid_client"**
- Verify Client ID and Secret are correct in `.env`
- Check for extra spaces or quotes

**"access_denied"**
- User didn't grant permissions
- Try again and make sure to click "Allow"

**Settings not working**
- Wait 5-10 minutes after saving in Google Console
- Clear browser cache and try again

## ✅ Checklist

- [ ] Client Secret added to `.env`
- [ ] Redirect URI added in Google Cloud Console
- [ ] Google Calendar API enabled
- [ ] Tested `/calendar/auth` endpoint
- [ ] Tested full OAuth flow
- [ ] Frontend integration (if needed)

---

**Your Client ID:** `329625451973-fmvvbtmr1mu2n98m3l6vah6q3td8eki1.apps.googleusercontent.com`

**Redirect URI to add:** `http://localhost:3000/auth/google/callback`

