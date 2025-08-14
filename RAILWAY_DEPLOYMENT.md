# Railway Deployment Guide for ClipWave AI Shorts

## Prerequisites
- GitHub account
- Railway account (free at railway.app)
- Domain name (optional but recommended)

## Step 1: Prepare Your Repository

### 1.1 Push to GitHub
```bash
# Initialize git if not already done
git init
git add .
git commit -m "Initial commit for Railway deployment"

# Create a new repository on GitHub and push
git remote add origin https://github.com/YOUR_USERNAME/clipwave-ai-shorts.git
git push -u origin main
```

### 1.2 Create Railway Configuration
Create a `railway.json` file in your project root:

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "DOCKERFILE",
    "dockerfilePath": "Dockerfile"
  },
  "deploy": {
    "startCommand": "python backend/main.py",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

## Step 2: Deploy to Railway

### 2.1 Connect Railway to GitHub
1. Go to [railway.app](https://railway.app)
2. Sign up with your GitHub account
3. Click "New Project"
4. Select "Deploy from GitHub repo"
5. Choose your `clipwave-ai-shorts` repository
6. Railway will automatically detect your Dockerfile

### 2.2 Configure Environment Variables
In your Railway project dashboard:

1. Go to the "Variables" tab
2. Add these environment variables:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   YOUTUBE_COOKIES_B64=your_base64_encoded_cookies_here
   PORT=8000
   ```

### 2.3 Deploy
Railway will automatically:
- Build your Docker image
- Deploy it to their infrastructure
- Provide you with a public URL

## Step 3: Add Custom Domain

### 3.1 Get Your Railway URL
After deployment, Railway will give you a URL like:
`https://clipwave-ai-shorts-production.up.railway.app`

### 3.2 Add Custom Domain
1. In your Railway project dashboard, go to "Settings"
2. Scroll to "Domains" section
3. Click "Add Domain"
4. Enter your domain (e.g., `clipwave.yourdomain.com`)
5. Railway will provide DNS records to configure

### 3.3 Configure DNS
Add these DNS records to your domain provider:

**For Cloudflare:**
- Type: CNAME
- Name: clipwave (or your subdomain)
- Target: `clipwave-ai-shorts-production.up.railway.app`
- Proxy status: Proxied (orange cloud)

**For other providers:**
- Type: CNAME
- Name: clipwave
- Value: `clipwave-ai-shorts-production.up.railway.app`

### 3.4 Wait for SSL
Railway will automatically provision SSL certificates for your custom domain (usually takes 5-10 minutes).

## Step 4: Update Application for Production

### 4.1 Update CORS Settings
Update your `backend/main.py` to allow your domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://clipwave.yourdomain.com",
        "https://clipwave-ai-shorts-production.up.railway.app",
        "http://localhost:3000"  # For local development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4.2 Update Frontend API Calls
Make sure your frontend uses relative URLs for API calls:

```typescript
// Instead of hardcoded localhost:8000
const API_BASE = window.location.origin;
const response = await fetch(`${API_BASE}/api/jobs`, {
  // ... rest of your fetch code
});
```

## Step 5: Monitor and Scale

### 5.1 Monitor Usage
- Railway dashboard shows CPU, memory, and network usage
- Set up alerts for high usage
- Monitor your OpenAI API usage

### 5.2 Scaling Options
- **Free Tier**: 500 hours/month, 512MB RAM, shared CPU
- **Pro Plan**: $5/month for 1000 hours, 1GB RAM, dedicated CPU
- **Team Plan**: $20/month for unlimited hours, 2GB RAM

## Troubleshooting

### Common Issues:

1. **Build Fails**
   - Check Railway logs for specific errors
   - Ensure all files are committed to GitHub
   - Verify Dockerfile syntax

2. **Environment Variables Not Working**
   - Double-check variable names in Railway dashboard
   - Ensure no extra spaces or quotes
   - Redeploy after adding variables

3. **Domain Not Working**
   - Wait 5-10 minutes for DNS propagation
   - Check DNS records are correct
   - Verify SSL certificate is provisioned

4. **Application Crashes**
   - Check Railway logs
   - Verify all dependencies are in requirements.txt
   - Ensure proper file permissions

### Useful Commands:
```bash
# View Railway logs
railway logs

# Redeploy manually
railway up

# Check deployment status
railway status
```

## Cost Estimation

**Free Tier (Recommended for testing):**
- 500 hours/month (enough for light usage)
- 512MB RAM
- Shared CPU
- Perfect for personal projects

**Pro Plan (Recommended for production):**
- $5/month
- 1000 hours/month
- 1GB RAM
- Dedicated CPU
- Better performance for multiple users

## Security Considerations

1. **API Keys**: Never commit API keys to GitHub
2. **Cookies**: Keep your YouTube cookies secure
3. **Rate Limiting**: Consider adding rate limiting for production
4. **Monitoring**: Set up alerts for unusual activity

## Next Steps

1. **Analytics**: Add Google Analytics or similar
2. **Error Tracking**: Set up Sentry for error monitoring
3. **Backup**: Consider database backup if you add persistent storage
4. **CDN**: Add Cloudflare for better global performance

Your ClipWave AI Shorts application will now be accessible worldwide at your custom domain! 🚀 