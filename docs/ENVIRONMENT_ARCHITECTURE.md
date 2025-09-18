# Environment Configuration - Clean Architecture Guide

## 🏗️ **Clean Architecture Overview**

This project now uses a clean, structured approach to environment configuration that separates concerns and eliminates conflicts.

## 📁 **Environment File Structure**

### **Root Level (Backend Configuration)**

```
.env.example          # ✅ Template with all possible variables
.env.development      # ✅ Development environment (11xxx ports)
.env.production       # ✅ Production environment (10xxx ports)  
.env.local            # 🔒 Local secrets (gitignored)
.env.mtproto.example  # ✅ MTProto-specific template
```

### **Frontend Level (apps/frontend/)**

```
.env.example          # ✅ Frontend template
.env.development      # ✅ Frontend development config
.env.production       # ✅ Frontend production config
.env.local            # 🔒 Frontend local overrides (gitignored)
.env.mock.example     # ✅ Mock data configuration
```

## 🎯 **Port Architecture**

### **Development Environment (11xxx series)**
- **API Server**: `11300` - Local development API
- **Frontend**: `11400` - Local development frontend  
- **Database**: `10100` - External Docker service port
- **Redis**: `10200` - External Docker service port

### **Production Environment (10xxx series)**
- **API Server**: `10300` - Docker internal + external
- **Frontend**: `10400` - Docker internal + external
- **Database**: `5432` - Docker internal (10100 external)
- **Redis**: `6379` - Docker internal (10200 external)

## 🔄 **Environment Loading Order**

### **Development Mode**
1. Load `.env.development` (base development config)
2. Override with `.env.local` (local secrets)
3. Environment variables take precedence

### **Production Mode**
1. Load `.env.production` (base production config)
2. Override with `.env.local` (local secrets)
3. Environment variables take precedence

## 🔒 **Security Model**

### **Public Files (Version Controlled)**
- `.env.example` - Template with CHANGE_ME placeholders
- `.env.development` - Development config with environment variable references
- `.env.production` - Production config with environment variable references

### **Private Files (Gitignored)**
- `.env.local` - Contains real secrets and API keys
- `.env.development.local` - Development-specific local overrides
- `.env.production.local` - Production-specific local overrides

## 🚀 **Usage Examples**

### **Development Workflow**

```bash
# Start development environment
make dev-start api

# The system will:
# 1. Load .env.development
# 2. Load .env.local (secrets)
# 3. Start API on port 11300
```

### **Production Deployment**

```bash
# Docker deployment
docker-compose up

# The system will:
# 1. Load .env.production  
# 2. Load .env.local (secrets)
# 3. Start services on 10xxx ports
```

### **Environment Variable References**

In configuration files, use environment variable syntax:
```bash
# .env.production
BOT_TOKEN=${BOT_TOKEN}
API_PORT=10300
DATABASE_URL=postgresql+asyncpg://analytic:${POSTGRES_PASSWORD}@db:5432/analytic_bot

# .env.local (provides the actual values)
BOT_TOKEN=7900046521:AAGgnLxHfXuKMfR0u1Fn6V6YliPnywkUu9E
POSTGRES_PASSWORD=your_secure_password
```

## 🛠️ **Migration from Old Structure**

### **Old Structure (Removed)**
```
❌ .env                    # Mixed dev/prod with real secrets
❌ .env.dev                # Development config
❌ apps/frontend/.env      # Conflicting frontend config
❌ apps/frontend/.env.docker # Docker frontend config
```

### **Migration Steps Completed**
1. ✅ **Backup**: All old files backed up to `.env-backup/`
2. ✅ **Restructure**: Created clean `.env.development` and `.env.production`
3. ✅ **Security**: Moved real secrets to `.env.local`
4. ✅ **Frontend**: Created matching frontend environment structure
5. ✅ **Scripts**: Updated all scripts to use new structure
6. ✅ **Cleanup**: Removed conflicting old files

## 📋 **Environment Variables Reference**

### **Core Application**
- `ENVIRONMENT` - development|production
- `DEBUG` - true|false
- `APP_VERSION` - Application version
- `LOG_LEVEL` - DEBUG|INFO|WARNING|ERROR

### **API Configuration**
- `API_HOST` - Host binding (0.0.0.0)
- `API_PORT` - Port number (11300 dev, 10300 prod)
- `API_HOST_URL` - Internal API URL
- `API_HOST_URL_EXTERNAL` - External API URL

### **Database**
- `POSTGRES_HOST` - Database host
- `POSTGRES_PORT` - Database port
- `POSTGRES_USER` - Database username
- `POSTGRES_PASSWORD` - Database password (from .env.local)
- `POSTGRES_DB` - Database name
- `DATABASE_URL` - Full connection string

### **Frontend (VITE_* prefix)**
- `VITE_API_BASE_URL` - Frontend API endpoint
- `VITE_API_TIMEOUT` - API request timeout
- `VITE_APP_NAME` - Application name
- `VITE_DEBUG` - Debug mode for frontend

### **Security**
- `JWT_SECRET_KEY` - JWT signing key (from .env.local)
- `SECRET_KEY` - Application secret key (from .env.local)
- `CORS_ORIGINS` - Allowed CORS origins

### **Payment System**
- `STRIPE_SECRET_KEY` - Stripe secret key (from .env.local)
- `STRIPE_PUBLISHABLE_KEY` - Stripe public key (from .env.local)
- `PAYMENT_PROCESSING_ENABLED` - Enable payment features

## 🔧 **Development Tools**

### **Create New Environment**
```bash
# Copy template and customize
cp .env.example .env.development
cp .env.example .env.production

# Add your secrets to .env.local
cp .env-backup/*/env.old .env.local
# Edit .env.local with your real values
```

### **Validate Configuration**
```bash
# Check environment loading
make dev-start api

# Verify all variables are loaded correctly
grep -v '^#' .env.development | grep -E '^[A-Z_]+'
```

### **Switch Environments**
```bash
# Development
export ENV=development
make dev-start

# Production  
export ENV=production
docker-compose up
```

## 🚨 **Security Best Practices**

1. ✅ **Never commit real secrets** - Use .env.local for actual values
2. ✅ **Use environment variable references** - `${VAR_NAME}` in config files
3. ✅ **Separate environments** - Different ports and configurations
4. ✅ **Backup before changes** - Automatic backup system in place
5. ✅ **Validate configurations** - Test loading before deployment

## 📞 **Support**

If you encounter issues with the new environment structure:

1. **Check file existence**: Ensure required files exist
2. **Validate syntax**: Check for syntax errors in .env files
3. **Review backups**: Original files are in `.env-backup/`
4. **Test loading**: Use `make dev-start` to test configuration
5. **Check logs**: Review application logs for environment loading errors

The new clean architecture provides better security, eliminates conflicts, and makes development/production separation crystal clear.