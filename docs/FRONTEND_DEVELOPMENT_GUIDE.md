# 🚀 Frontend Development Environment Guide

This guide explains how to use the complete frontend development setup with Docker.

## 📊 Overview

Your AnalyticBot now has **two frontend environments**:

| Environment | Port | Purpose | Features |
|------------|------|---------|----------|
| **Development** | `5173` | Active coding | 🔥 Hot reload, 🐛 Debug tools, 📝 Source maps |
| **Production** | `3000` | Testing & deployment | ⚡ Optimized, 🔒 Security headers, 🌐 Nginx |

## 🛠 Quick Start Commands

### Development Environment (Recommended for coding)
```bash
# Start development environment
./scripts/frontend-helper.sh docker-dev

# Access at: http://localhost:5173
# Features: Hot reload, instant changes, debug tools
```

### Production Environment (For testing & deployment)
```bash
# Start production environment
./scripts/frontend-helper.sh docker-prod

# Access at: http://localhost:3000
# Features: Optimized build, nginx server, production-ready
```

### Full Stack Development
```bash
# Start complete development environment
sudo docker-compose --profile dev up -d

# This starts:
# - Development frontend (5173) with hot reload
# - API backend (8000)
# - Database (5433)
# - Redis (6380)
# - Bot service
```

## 🔧 Development Workflow

### 1. **Daily Development Setup**
```bash
# Start development environment
./scripts/frontend-helper.sh docker-dev

# Your setup is now:
✅ Frontend: http://localhost:5173 (hot reload)
✅ API: http://localhost:8000
✅ Database & Redis: Running
```

### 2. **Code & Test Cycle**
```bash
# 1. Edit code in VS Code
nano apps/frontend/src/components/AnalyticsDashboard.jsx

# 2. Save file (Ctrl+S)
# 3. Browser automatically updates at localhost:5173 (instant!)
# 4. See changes immediately without rebuilding
```

### 3. **Production Testing**
```bash
# Test your changes in production environment
./scripts/frontend-helper.sh docker-prod

# Visit http://localhost:3000 to test optimized build
```

## 📋 Available Commands

### Frontend Helper Script
```bash
# Development
./scripts/frontend-helper.sh docker-dev       # Start dev with hot reload
./scripts/frontend-helper.sh docker-prod      # Start production build
./scripts/frontend-helper.sh docker-build     # Build both images
./scripts/frontend-helper.sh docker-stop      # Stop containers
./scripts/frontend-helper.sh docker-logs      # View logs
./scripts/frontend-helper.sh docker-status    # Check status
./scripts/frontend-helper.sh test             # Run tests

# Local development (without Docker)
./scripts/frontend-helper.sh setup            # Install dependencies
./scripts/frontend-helper.sh dev              # Start local dev server
./scripts/frontend-helper.sh build            # Build locally
```

### Docker Manager Script
```bash
# Environment management
./scripts/docker-manager.sh dev               # Full dev environment
./scripts/docker-manager.sh prod              # Full prod environment
./scripts/docker-manager.sh status            # Check all services
./scripts/docker-manager.sh logs frontend-dev # Dev logs
./scripts/docker-manager.sh logs frontend     # Prod logs
```

## 🎯 Development Features

### Hot Module Replacement (HMR)
- **Edit any React component** → Changes appear instantly
- **Edit CSS/styles** → Styles update without page refresh
- **Edit configuration** → Automatic restart when needed

### Development Tools
- **React DevTools**: Inspect component state and props
- **Source Maps**: Debug with original TypeScript/JSX code
- **Error Overlay**: Detailed error messages with exact line numbers
- **Console Logs**: Development logging enabled
- **Accessibility Testing**: Real-time a11y validation

### File Watching
```bash
# These files are watched for changes:
apps/frontend/src/**/*.js
apps/frontend/src/**/*.jsx
apps/frontend/src/**/*.ts
apps/frontend/src/**/*.tsx
apps/frontend/src/**/*.css
apps/frontend/src/**/*.scss
apps/frontend/public/**/*
```

## 🔍 Debugging & Monitoring

### View Logs
```bash
# Development logs (detailed)
sudo docker logs -f analyticbot-frontend-dev

# Production logs (nginx access logs)
sudo docker logs -f analyticbot-frontend

# Combined view
./scripts/frontend-helper.sh docker-logs
```

### Health Checks
```bash
# Check if services are healthy
./scripts/frontend-helper.sh docker-status

# Full system status
./scripts/docker-manager.sh status

# Test connectivity
curl http://localhost:5173  # Development
curl http://localhost:3000  # Production
```

### Performance Testing
```bash
# Test development performance
curl -w "@-" -o /dev/null -s http://localhost:5173 <<< "
time_namelookup:  %{time_namelookup}
time_connect:     %{time_connect}
time_appconnect:  %{time_appconnect}
time_pretransfer: %{time_pretransfer}
time_redirect:    %{time_redirect}
time_starttransfer: %{time_starttransfer}
time_total:       %{time_total}
"
```

## 🚨 Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the port
lsof -i :5173
lsof -i :3000

# Stop conflicting services
./scripts/frontend-helper.sh docker-stop
```

#### Container Won't Start
```bash
# Check logs for errors
sudo docker logs analyticbot-frontend-dev

# Rebuild with fresh image
./scripts/frontend-helper.sh docker-build
```

#### Hot Reload Not Working
```bash
# Restart development container
sudo docker-compose restart frontend-dev

# Check file watching is enabled
./scripts/frontend-helper.sh docker-logs
```

#### Permission Issues
```bash
# Docker permission fix
sudo usermod -aG docker $USER
newgrp docker

# Or use sudo with commands
sudo docker-compose up -d
```

### Getting Help
```bash
# Show all available commands
./scripts/frontend-helper.sh help
./scripts/docker-manager.sh help

# Test everything is working
./scripts/test-frontend.sh
```

## 🎨 Customization

### Environment Variables
Edit `.env` file to customize:
```bash
# Frontend configuration
VITE_API_URL=http://localhost:8000
VITE_ENABLE_DEBUG=true
VITE_DEFAULT_THEME=dark

# Development settings
VITE_PORT=5173
NODE_ENV=development
```

### Vite Configuration
Edit `apps/frontend/vite.config.js` for:
- Custom build settings
- Proxy configuration
- Plugin settings
- Performance optimization

## 🎉 Success Checklist

Your development environment is ready when:

- ✅ Development frontend runs on http://localhost:5173
- ✅ Production frontend runs on http://localhost:3000
- ✅ Hot reload works (edit files, see instant changes)
- ✅ Both environments show your accessibility-enhanced UI
- ✅ API proxy works through both frontends
- ✅ Docker containers show as healthy
- ✅ Frontend helper scripts work without errors

**You now have a complete professional development environment! 🚀**
