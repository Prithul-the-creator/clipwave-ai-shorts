# 🚀 **ClipWave AI Shorts - Deployment Guide**

## 🔒 **Secure Cookie Management for Production**

Your application is now ready for secure deployment! Here's how to ensure your YouTube cookies work on any server while maintaining security.

## 📋 **Step 1: Environment Variables Setup**

### **For Local Development:**
Your current setup with `cookies.txt` file works perfectly for local development.

### **For Production Deployment:**

1. **Copy the base64-encoded cookies** from the script output above:
   ```
   YOUTUBE_COOKIES_B64=<the_long_base64_string_from_script_output>
   ```

2. **Add this to your server's environment variables:**
   - **Vercel:** Add in Project Settings → Environment Variables
   - **Railway:** Add in Project Settings → Variables
   - **Heroku:** Use `heroku config:set YOUTUBE_COOKIES_B64="..."` 
   - **Docker:** Add to your `.env` file or docker-compose.yml
   - **VPS/Server:** Add to your system environment or `.env` file

## 🔧 **Step 2: Update Your Code**

Your `video_processor.py` has already been updated to support both methods:
- ✅ **Base64 cookies** (for production) - `YOUTUBE_COOKIES_B64`
- ✅ **File cookies** (for local development) - `YOUTUBE_COOKIES_FILE`

## 🛡️ **Security Features Implemented**

### **✅ What's Protected:**
- **Cookies are base64-encoded** - Not human-readable in environment variables
- **Cookies are never committed** to git (`.gitignore` configured)
- **Temporary file creation** - Cookies are decoded to temp files and cleaned up
- **Fallback system** - Works with both file and base64 methods

### **✅ What's NOT Exposed:**
- ❌ No cookies in your code repository
- ❌ No cookies in your deployment files
- ❌ No cookies in your logs
- ❌ No cookies in your environment variable names

## 🚀 **Deployment Options**

### **Option A: Vercel (Recommended for Frontend)**
```bash
# 1. Install Vercel CLI
npm i -g vercel

# 2. Deploy frontend
vercel

# 3. Add environment variable in Vercel dashboard
YOUTUBE_COOKIES_B64=<your_base64_string>
```

### **Option B: Railway (Recommended for Full Stack)**
```bash
# 1. Connect your GitHub repo to Railway
# 2. Add environment variable in Railway dashboard
YOUTUBE_COOKIES_B64=<your_base64_string>
```

### **Option C: Docker**
```dockerfile
# Dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Environment variable will be set at runtime
ENV YOUTUBE_COOKIES_B64=""

CMD ["python", "backend/main.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  app:
    build: .
    environment:
      - YOUTUBE_COOKIES_B64=${YOUTUBE_COOKIES_B64}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    ports:
      - "8000:8000"
```

### **Option D: VPS/Server**
```bash
# 1. Set environment variable
export YOUTUBE_COOKIES_B64="<your_base64_string>"

# 2. Or add to .env file
echo "YOUTUBE_COOKIES_B64=<your_base64_string>" >> .env

# 3. Run your application
python backend/main.py
```

## 🧪 **Testing Your Deployment**

### **1. Test Cookie Decoding:**
The script already tested decoding - check `cookies_decoded.txt` to verify.

### **2. Test Video Download:**
```bash
# Test with a simple YouTube video
curl -X POST "https://your-domain.com/api/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "instructions": "Find the most engaging moments"
  }'
```

### **3. Monitor Logs:**
Look for these success messages:
- ✅ `"Using base64-encoded cookies from environment variable"`
- ✅ `"Download successful"`
- ✅ `"Video processing completed"`

## 🔄 **Cookie Refresh Process**

### **When to Refresh Cookies:**
- Every 30-60 days (YouTube cookies expire)
- When you get authentication errors
- When you change YouTube accounts

### **How to Refresh:**
1. **Extract new cookies:**
   ```bash
   yt-dlp --cookies-from-browser chrome --cookies cookies_new.txt
   ```

2. **Run the preparation script:**
   ```bash
   python prepare_deployment.py
   ```

3. **Update your environment variable** with the new base64 string

## 🚨 **Troubleshooting**

### **Common Issues:**

**❌ "No cookies found"**
- Check if `YOUTUBE_COOKIES_B64` is set correctly
- Verify the base64 string is complete

**❌ "Download failed"**
- Cookies may have expired - refresh them
- Check if the YouTube video requires age verification

**❌ "Authentication required"**
- Your cookies don't have sufficient permissions
- Try logging into YouTube in your browser first

### **Debug Commands:**
```bash
# Check if environment variable is set
echo $YOUTUBE_COOKIES_B64 | head -c 50

# Test cookie decoding
python -c "
import base64, os
cookies_b64 = os.getenv('YOUTUBE_COOKIES_B64')
if cookies_b64:
    print('✅ Cookies found')
    print(f'Length: {len(cookies_b64)} characters')
else:
    print('❌ No cookies found')
"
```

## 📝 **Environment Variables Summary**

| Variable | Purpose | Required | Example |
|----------|---------|----------|---------|
| `YOUTUBE_COOKIES_B64` | Base64-encoded YouTube cookies | ✅ | `ZXhhbXBsZQ==` |
| `OPENAI_API_KEY` | OpenAI API key | ✅ | `sk-...` |
| `YOUTUBE_COOKIES_FILE` | File path to cookies (local dev) | ❌ | `./cookies.txt` |

## 🎉 **You're Ready to Deploy!**

Your application is now configured for secure, production-ready deployment with working YouTube cookies. The system will automatically:

1. **Detect your deployment environment**
2. **Use base64 cookies in production**
3. **Fall back to file cookies in development**
4. **Clean up temporary files automatically**
5. **Maintain security best practices**

**Happy deploying! 🚀** 