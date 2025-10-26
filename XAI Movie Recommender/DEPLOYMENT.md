# Deployment Guide - Lumiere Movie Recommender

This guide covers multiple deployment options for the Lumiere Movie Recommender application.

## Table of Contents
1. [Quick Deploy (Recommended)](#option-1-quick-deploy-vercel--render)
2. [Docker Deployment](#option-2-docker-deployment)
3. [Manual Deployment](#option-3-manual-deployment)
4. [Environment Variables](#environment-variables)

---

## Option 1: Quick Deploy (Vercel + Render)

### Best for: Quick deployment, minimal configuration

### Frontend (Vercel)

1. **Prepare the frontend:**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Deploy to Vercel:**
   ```bash
   # Install Vercel CLI
   npm i -g vercel

   # Deploy
   vercel
   ```

3. **Configure environment variables in Vercel dashboard:**
   - `VITE_API_URL` = Your backend URL (from Render)

### Backend (Render)

1. **Push your code to GitHub**

2. **Create a new Web Service on Render.com:**
   - Connect your GitHub repository
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

3. **Add environment variables:**
   - `NEO4J_URI` = `neo4j+s://77261dd5.databases.neo4j.io`
   - `NEO4J_USER` = `neo4j`
   - `NEO4J_PASSWORD` = `p2BTU3z2RfCFEHQwN8HY9tIqeYzgDqvnqL4fd7PfodU`

4. **Deploy and copy the backend URL**

5. **Update frontend API URL:**
   - Go back to Vercel
   - Update `VITE_API_URL` with your Render backend URL
   - Redeploy

---

## Option 2: Docker Deployment

### Best for: Full control, any cloud provider (AWS, GCP, Azure, DigitalOcean)

### Local Testing

1. **Create a `.env` file:**
   ```bash
   NEO4J_URI=neo4j+s://77261dd5.databases.neo4j.io
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=p2BTU3z2RfCFEHQwN8HY9tIqeYzgDqvnqL4fd7PfodU
   ```

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

3. **Access the application:**
   - Frontend: http://localhost
   - Backend: http://localhost:8000

### Deploy to Cloud (Example: AWS EC2)

1. **Launch an EC2 instance:**
   - Ubuntu 22.04 LTS
   - t3.medium or larger (for ML model)
   - Open ports: 80, 443, 8000

2. **SSH into the instance and install Docker:**
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose -y
   sudo systemctl start docker
   sudo systemctl enable docker
   ```

3. **Clone your repository:**
   ```bash
   git clone <your-repo-url>
   cd "XAI Movie Recommender"
   ```

4. **Create `.env` file with your credentials**

5. **Run the application:**
   ```bash
   sudo docker-compose up -d
   ```

6. **Set up a domain (optional but recommended):**
   - Point your domain to the EC2 public IP
   - Use Nginx or Caddy for SSL/HTTPS

---

## Option 3: Manual Deployment

### Backend Deployment

1. **On your server:**
   ```bash
   # Install Python 3.11+
   sudo apt install python3.11 python3.11-venv

   # Clone and setup
   git clone <your-repo-url>
   cd "XAI Movie Recommender"
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Create a systemd service:**
   ```bash
   sudo nano /etc/systemd/system/lumiere-backend.service
   ```

   Add:
   ```ini
   [Unit]
   Description=Lumiere Backend
   After=network.target

   [Service]
   User=ubuntu
   WorkingDirectory=/home/ubuntu/XAI Movie Recommender
   Environment="NEO4J_URI=neo4j+s://77261dd5.databases.neo4j.io"
   Environment="NEO4J_USER=neo4j"
   Environment="NEO4J_PASSWORD=p2BTU3z2RfCFEHQwN8HY9tIqeYzgDqvnqL4fd7PfodU"
   ExecStart=/home/ubuntu/XAI Movie Recommender/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Start the service:**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl start lumiere-backend
   sudo systemctl enable lumiere-backend
   ```

### Frontend Deployment

1. **Build the frontend:**
   ```bash
   cd frontend
   npm install
   npm run build
   ```

2. **Install and configure Nginx:**
   ```bash
   sudo apt install nginx
   sudo nano /etc/nginx/sites-available/lumiere
   ```

   Add:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       root /home/ubuntu/XAI Movie Recommender/frontend/dist;
       index index.html;

       location / {
           try_files $uri $uri/ /index.html;
       }

       location /api {
           proxy_pass http://localhost:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

3. **Enable and restart Nginx:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/lumiere /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

---

## Environment Variables

### Required for Backend:
- `NEO4J_URI` - Your Neo4j Aura DB URI
- `NEO4J_USER` - Neo4j username (default: neo4j)
- `NEO4J_PASSWORD` - Neo4j password

### Required for Frontend:
- `VITE_API_URL` - Backend API URL (e.g., https://api.yourdomain.com)

---

## Production Checklist

- [ ] Environment variables are set securely
- [ ] Models directory is included and has trained models
- [ ] CORS is configured correctly in `main.py`
- [ ] SSL/HTTPS is enabled (use Let's Encrypt)
- [ ] Database connection is working
- [ ] Health check endpoint `/health` returns 200
- [ ] Frontend can reach backend API
- [ ] Error monitoring is set up (optional: Sentry)
- [ ] Backups are configured for models

---

## Monitoring

### Check Backend Health:
```bash
curl http://your-backend-url/health
```

Should return:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "neo4j_connected": true
}
```

### View Backend Logs (systemd):
```bash
sudo journalctl -u lumiere-backend -f
```

### View Backend Logs (Docker):
```bash
docker-compose logs -f backend
```

---

## Troubleshooting

### Backend won't start:
- Check if models directory exists and has trained models
- Verify Neo4j credentials in environment variables
- Check port 8000 is not in use

### Frontend can't reach backend:
- Verify CORS settings in `main.py`
- Check `VITE_API_URL` in frontend build
- Ensure backend is accessible from frontend's network

### Database connection fails:
- Verify Neo4j Aura DB is active
- Check firewall rules allow outbound connections
- Test connection with Neo4j Browser

---

## Recommended Providers

### Frontend Hosting:
- **Vercel** (Easiest, free tier)
- **Netlify** (Easy, free tier)
- **Cloudflare Pages** (Fast, free tier)

### Backend Hosting:
- **Render** (Easiest, free tier available)
- **Railway** (Easy, generous free tier)
- **DigitalOcean App Platform** ($5/month)
- **AWS EC2** (Most flexible, ~$10-20/month)
- **Google Cloud Run** (Serverless, pay-per-use)

### Database:
- **Neo4j Aura DB** (Already using, $0-65/month)

---

## Cost Estimates

### Budget Option (~$0-10/month):
- Frontend: Vercel (Free)
- Backend: Render (Free tier or $7/month)
- Database: Neo4j Aura (Free tier)

### Production Option (~$50-100/month):
- Frontend: Vercel Pro ($20/month)
- Backend: AWS EC2 t3.medium ($30-40/month)
- Database: Neo4j Aura Professional ($65/month)

---

## Support

For issues or questions:
1. Check the [README.md](README.md)
2. Review logs for error messages
3. Verify all environment variables are set
4. Test database connection separately
