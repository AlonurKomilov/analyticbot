# Stripe Webhook Setup Guide
## Complete Configuration for Production Payment System

### 🎯 Overview
This guide helps you configure Stripe webhooks for your production AnalyticBot payment system. Webhooks are essential for real-time payment status updates and subscription management.

---

## 📋 Prerequisites

- ✅ Stripe account with live mode access
- ✅ Production domain with SSL certificate
- ✅ AnalyticBot deployed and running
- ✅ API accessible at your production domain

---

## 🔧 Step-by-Step Webhook Configuration

### Step 1: Access Stripe Dashboard
1. Go to [Stripe Dashboard](https://dashboard.stripe.com/)
2. Switch to **Live mode** (toggle in top-left corner)
3. Navigate to **Developers** → **Webhooks**

### Step 2: Create Webhook Endpoint
1. Click **"Add endpoint"**
2. Enter your endpoint URL:
   ```
   https://api.your-domain.com/api/payments/webhook/stripe
   ```
   *Replace `your-domain.com` with your actual domain*

### Step 3: Select Events to Listen For
Select these essential events for the payment system:

#### Payment Events
- ✅ `payment_intent.succeeded` - Successful one-time payments
- ✅ `payment_intent.payment_failed` - Failed payments
- ✅ `payment_method.attached` - Payment method added to customer

#### Subscription Events
- ✅ `customer.subscription.created` - New subscription created
- ✅ `customer.subscription.updated` - Subscription changes (plan, status)
- ✅ `customer.subscription.deleted` - Subscription cancelled
- ✅ `invoice.payment_succeeded` - Subscription renewal successful
- ✅ `invoice.payment_failed` - Subscription renewal failed

#### Customer Events
- ✅ `customer.created` - New customer record
- ✅ `customer.updated` - Customer information changed
- ✅ `customer.deleted` - Customer account deleted

### Step 4: Configure Webhook Settings
- **Description**: "AnalyticBot Payment System"
- **URL**: `https://api.your-domain.com/api/payments/webhook/stripe`
- **Version**: Latest API version (recommended)

### Step 5: Get Webhook Signing Secret
1. After creating the webhook, click on it to view details
2. In the **Signing secret** section, click **"Reveal"**
3. Copy the webhook signing secret (starts with `whsec_`)
4. Update your production environment:
   ```bash
   # In .env.production
   STRIPE_WEBHOOK_SECRET=whsec_your_actual_webhook_secret_here
   ```

---

## 🧪 Testing Webhook Configuration

### Test 1: Webhook Endpoint Accessibility
```bash
# Test if your endpoint is accessible
curl -X POST https://api.your-domain.com/api/payments/webhook/stripe \
  -H "Content-Type: application/json" \
  -d '{"test": "webhook"}'

# Expected: 400 Bad Request (Missing Stripe signature)
# This confirms the endpoint is reachable
```

### Test 2: Stripe Webhook Test
1. In Stripe Dashboard, go to your webhook
2. Click **"Send test webhook"**
3. Select `payment_intent.succeeded` event
4. Click **"Send test webhook"**
5. Check the **Response** tab for status 200

### Test 3: Real Payment Test
1. Create a test subscription in your application
2. Use Stripe test card: `4242 4242 4242 4242`
3. Check webhook delivery in Stripe Dashboard
4. Verify payment status updates in your application

---

## 🔍 Monitoring & Troubleshooting

### Webhook Delivery Monitoring
1. **Stripe Dashboard**: Monitor webhook delivery status
2. **Application Logs**: Check payment service logs
3. **Database**: Verify webhook events are recorded

### Common Issues & Solutions

#### Issue: Webhook Returns 400/401 Error
**Solution**: 
- Verify webhook signing secret is correct
- Check endpoint URL is accessible
- Ensure SSL certificate is valid

#### Issue: Events Not Processing
**Solution**:
- Check selected events match your needs
- Verify webhook handler logic
- Review application logs for errors

#### Issue: Duplicate Events
**Solution**:
- Implement idempotency checks
- Use webhook event IDs to prevent duplicates
- Check for multiple webhook endpoints

### Webhook Logs Access
```bash
# Check webhook processing logs
sudo docker-compose logs api | grep webhook

# Monitor real-time webhook events
sudo docker-compose logs -f api | grep payment
```

---

## 🛡️ Security Best Practices

### 1. Webhook Signature Verification
- ✅ Always verify webhook signatures
- ✅ Use environment variables for secrets
- ✅ Implement replay attack protection

### 2. Endpoint Security
- ✅ Use HTTPS only
- ✅ Implement rate limiting
- ✅ Monitor for suspicious activity

### 3. Error Handling
- ✅ Log all webhook events
- ✅ Implement retry logic for failures
- ✅ Alert on critical webhook failures

---

## 📊 Webhook Events Reference

### Event Types and Actions

| Stripe Event | Application Action | Database Update |
|--------------|-------------------|-----------------|
| `payment_intent.succeeded` | Mark payment as successful | Update payment status |
| `payment_intent.payment_failed` | Mark payment as failed | Update with failure reason |
| `invoice.payment_succeeded` | Renew subscription | Extend subscription period |
| `customer.subscription.updated` | Update subscription details | Sync subscription data |
| `customer.subscription.deleted` | Cancel subscription | Mark as cancelled |

### Webhook Payload Example
```json
{
  "id": "evt_1234567890",
  "object": "event",
  "api_version": "2023-10-16",
  "created": 1641234567,
  "data": {
    "object": {
      "id": "pi_1234567890",
      "object": "payment_intent",
      "amount": 2999,
      "currency": "usd",
      "status": "succeeded"
    }
  },
  "type": "payment_intent.succeeded"
}
```

---

## ✅ Production Checklist

Before going live, ensure:

- [ ] Webhook endpoint is accessible via HTTPS
- [ ] Signing secret is correctly configured
- [ ] All required events are selected
- [ ] Webhook has been tested successfully
- [ ] Error monitoring is in place
- [ ] Backup webhook endpoint configured (optional)
- [ ] Documentation is updated with webhook details

---

## 🆘 Support & Resources

### Stripe Resources
- [Webhook Documentation](https://stripe.com/docs/webhooks)
- [Webhook Testing Guide](https://stripe.com/docs/webhooks/test)
- [Event Types Reference](https://stripe.com/docs/api/events/types)

### AnalyticBot Payment System
- API Documentation: `/docs` endpoint
- Payment Status: `/api/payments/status`
- Webhook Endpoint: `/api/payments/webhook/stripe`

### Emergency Contacts
- **Webhook Issues**: Check application logs first
- **Payment Failures**: Monitor Stripe Dashboard
- **System Downtime**: Check server and Docker status

---

*Last Updated: Week 15-16 Payment System Implementation*
*Version: Production Ready*
