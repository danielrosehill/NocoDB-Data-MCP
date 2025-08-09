# Configuration Guide

This guide will help you configure the NoCoDB Data MCP server for your own NoCoDB instance.

## Required Configuration Files

The MCP server requires three configuration files in the repository root:

### 1. `nocodb.json` - NoCoDB API Token

This file contains your NoCoDB API token. Replace `YOUR_NOCODB_API_TOKEN_HERE` with your actual API token.

**How to get your NoCoDB API token:**
1. Log into your NoCoDB instance
2. Go to Account Settings
3. Navigate to "Tokens" section
4. Create a new API token
5. Copy the token and replace the placeholder in `nocodb.json`

### 2. `cf.json` - Cloudflare Access Credentials (Optional)

This file is only needed if your NoCoDB instance is behind Cloudflare Access. If you're not using Cloudflare Access, you can ignore this file.

**Required fields to replace:**
- `your-email@example.com` - Your Cloudflare Access email
- `YOUR_CF_ACCESS_PASSWORD` - Your Cloudflare Access password
- `YOUR_CLIENT_ID_HERE` - Your Cloudflare Access Client ID
- `YOUR_CLIENT_SECRET_HERE` - Your Cloudflare Access Client Secret

**How to get Cloudflare Access credentials:**
1. Log into your Cloudflare dashboard
2. Go to Zero Trust > Access > Service Tokens
3. Create a new service token
4. Copy the Client ID and Client Secret
5. Replace the placeholders in `cf.json`

### 3. `thetask.m d` - NoCoDB Instance URL

Replace `your-nocodb-instance.com` with your actual NoCoDB instance URL (without `https://`).

Examples:
- `app.nocodb.com` (for NoCoDB Cloud)
- `nocodb.yourdomain.com` (for self-hosted)
- `localhost:8080` (for local development)

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit sensitive credentials to version control**
2. **Keep your API tokens secure and rotate them regularly**
3. **Use environment variables in production deployments**
4. **Ensure your NoCoDB instance uses HTTPS in production**

## Alternative Configuration Methods

### Environment Variables

Instead of using JSON files, you can set environment variables:

```bash
export NOCODB_API_TOKEN="your_api_token_here"
export NOCODB_HOST="your-nocodb-instance.com"
export CF_ACCESS_CLIENT_ID="your_client_id"
export CF_ACCESS_CLIENT_SECRET="your_client_secret"
```

### Docker Configuration

If deploying with Docker, use secrets or environment files:

```yaml
version: '3.8'
services:
  nocodb-mcp:
    build: .
    environment:
      - NOCODB_API_TOKEN_FILE=/run/secrets/nocodb_token
      - NOCODB_HOST=your-nocodb-instance.com
    secrets:
      - nocodb_token

secrets:
  nocodb_token:
    file: ./secrets/nocodb_token.txt
```

## Troubleshooting

### Connection Issues

1. **Verify your NoCoDB instance is accessible**
   ```bash
   curl https://your-nocodb-instance.com/api/v1/db/meta/projects
   ```

2. **Test your API token**
   ```bash
   curl -H "xc-token: YOUR_API_TOKEN" https://your-nocodb-instance.com/api/v1/db/meta/projects
   ```

3. **Check Cloudflare Access (if applicable)**
   - Ensure your service token has the correct permissions
   - Verify the Client ID and Secret are correct

### Common Error Messages

- **"Invalid API token"** - Check your `nocodb.json` configuration
- **"Host not found"** - Verify the URL in `thetask.m d`
- **"Access denied"** - Check your Cloudflare Access configuration
- **"SSL certificate error"** - Ensure your NoCoDB instance has a valid SSL certificate

## Testing Your Configuration

After setting up the configuration files, test the connection:

```bash
# Activate virtual environment
source venv/bin/activate

# Run the connection test
python test_connection.py
```

If successful, you should see output confirming the connection to your NoCoDB instance.
