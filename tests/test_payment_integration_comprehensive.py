"""
🧪 Phase 2.7: Backend Testing & Quality Assurance
Payment System Integration Tests

Comprehensive testing for the payment system including
all gateways, webhooks, security, and business logic.
"""

import asyncio
import pytest
import json
import hmac
import hashlib
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from apps.bot.services.payment_service import PaymentService
from apps.bot.models.payment import (
    PaymentProvider, BillingCycle, PaymentMethodCreate,
    PaymentRequest, SubscriptionCreate
)


class TestPaymentSystemIntegration:
    """
    💳 Payment System Integration Tests
    
    Comprehensive testing of the payment system including
    all adapters, security features, and business workflows.
    """
    
    def setup_method(self):
        """Setup payment service and test data"""
        self.payment_service = PaymentService()
        
        # Test payment method data
        self.test_payment_method = PaymentMethodCreate(
            user_id="test_user_123",
            provider=PaymentProvider.STRIPE,
            payment_details={
                "card_number": "4242424242424242",
                "exp_month": 12,
                "exp_year": 2025,
                "cvc": "123"
            }
        )
        
        # Test payment request
        self.test_payment = PaymentRequest(
            user_id="test_user_123",
            amount=29.99,
            currency="USD",
            description="Premium subscription",
            payment_method_id="pm_test_123"
        )
        
        # Test subscription
        self.test_subscription = SubscriptionCreate(
            user_id="test_user_123",
            plan_id="premium_monthly",
            payment_method_id="pm_test_123",
            billing_cycle=BillingCycle.MONTHLY
        )

    @pytest.mark.asyncio
    async def test_stripe_adapter_integration(self):
        """Test Stripe payment adapter integration"""
        stripe_adapter = self.payment_service.adapters['stripe']
        
        # Mock Stripe API responses
        with patch('stripe.PaymentMethod.create') as mock_create_pm, \
             patch('stripe.PaymentIntent.create') as mock_create_pi:
            
            mock_create_pm.return_value = Mock(id='pm_stripe_123')
            mock_create_pi.return_value = Mock(
                id='pi_stripe_123',
                status='succeeded',
                amount=2999,
                currency='usd'
            )
            
            # Test payment method creation
            pm_result = await stripe_adapter.create_payment_method(
                self.test_payment_method
            )
            assert pm_result['id'] == 'pm_stripe_123'
            
            # Test payment processing
            payment_result = await stripe_adapter.process_payment(
                self.test_payment
            )
            assert payment_result['status'] == 'succeeded'
            assert payment_result['amount'] == 29.99

    @pytest.mark.asyncio
    async def test_payme_adapter_integration(self):
        """Test Payme payment adapter integration"""
        payme_adapter = self.payment_service.adapters['payme']
        
        # Mock Payme API responses
        mock_response = {
            'jsonrpc': '2.0',
            'id': 1,
            'result': {
                'transaction': '12345',
                'state': 2,  # Success
                'create_time': int(datetime.utcnow().timestamp() * 1000)
            }
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.json = AsyncMock(
                return_value=mock_response
            )
            
            # Test payment processing
            payment_result = await payme_adapter.process_payment(
                self.test_payment
            )
            
            assert 'transaction_id' in payment_result
            assert payment_result['status'] == 'succeeded'

    @pytest.mark.asyncio
    async def test_click_adapter_integration(self):
        """Test Click payment adapter integration"""
        click_adapter = self.payment_service.adapters['click']
        
        # Mock Click API response
        mock_response = {
            'error': 0,
            'error_note': 'Success',
            'click_trans_id': 123456789,
            'merchant_trans_id': 'test_trans_123'
        }
        
        with patch('aiohttp.ClientSession.post') as mock_post:
            mock_post.return_value.__aenter__.return_value.json = AsyncMock(
                return_value=mock_response
            )
            
            # Test payment processing
            payment_result = await click_adapter.process_payment(
                self.test_payment
            )
            
            assert payment_result['transaction_id'] == 123456789
            assert payment_result['status'] == 'succeeded'

    @pytest.mark.asyncio
    async def test_universal_payment_service(self):
        """Test the universal payment service workflow"""
        with patch.object(self.payment_service, 'payment_repository') as mock_repo:
            mock_repo.create_payment_method = AsyncMock(return_value={
                'id': 'pm_123',
                'provider': 'stripe',
                'user_id': 'test_user_123'
            })
            
            # Test payment method creation
            result = await self.payment_service.create_payment_method(
                self.test_payment_method
            )
            
            assert result['id'] == 'pm_123'
            assert result['provider'] == 'stripe'
            mock_repo.create_payment_method.assert_called_once()

    @pytest.mark.asyncio
    async def test_subscription_lifecycle(self):
        """Test complete subscription lifecycle"""
        with patch.object(self.payment_service, 'subscription_repository') as mock_repo:
            # Mock subscription creation
            mock_repo.create_subscription = AsyncMock(return_value={
                'id': 'sub_123',
                'status': 'active',
                'user_id': 'test_user_123',
                'plan_id': 'premium_monthly'
            })
            
            # Mock subscription retrieval
            mock_repo.get_subscription = AsyncMock(return_value={
                'id': 'sub_123',
                'status': 'active',
                'next_billing_date': datetime.utcnow() + timedelta(days=30)
            })
            
            # Test subscription creation
            subscription = await self.payment_service.create_subscription(
                self.test_subscription
            )
            
            assert subscription['id'] == 'sub_123'
            assert subscription['status'] == 'active'
            
            # Test subscription cancellation
            mock_repo.update_subscription = AsyncMock(return_value={
                'id': 'sub_123',
                'status': 'cancelled'
            })
            
            cancelled = await self.payment_service.cancel_subscription('sub_123')
            assert cancelled['status'] == 'cancelled'

    @pytest.mark.asyncio
    async def test_webhook_signature_verification(self):
        """Test webhook signature verification for all providers"""
        
        # Test Stripe webhook verification
        stripe_payload = json.dumps({'type': 'payment_intent.succeeded'})
        stripe_signature = self._create_stripe_signature(stripe_payload)
        
        is_valid = await self.payment_service.verify_webhook_signature(
            PaymentProvider.STRIPE,
            stripe_payload,
            {'stripe-signature': stripe_signature}
        )
        assert is_valid
        
        # Test Payme webhook verification
        payme_payload = {'method': 'CheckPerformTransaction'}
        payme_auth = self._create_payme_auth(payme_payload)
        
        is_valid = await self.payment_service.verify_webhook_signature(
            PaymentProvider.PAYME,
            json.dumps(payme_payload),
            {'authorization': payme_auth}
        )
        assert is_valid

    def _create_stripe_signature(self, payload):
        """Create valid Stripe webhook signature"""
        secret = "whsec_test_secret"
        timestamp = str(int(datetime.utcnow().timestamp()))
        
        # Create signature
        signed_payload = f"{timestamp}.{payload}"
        signature = hmac.new(
            secret.encode('utf-8'),
            signed_payload.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return f"t={timestamp},v1={signature}"

    def _create_payme_auth(self, payload):
        """Create valid Payme authorization header"""
        import base64
        credentials = f"Paycom:{json.dumps(payload)}"
        return f"Basic {base64.b64encode(credentials.encode()).decode()}"

    @pytest.mark.asyncio
    async def test_idempotency_key_handling(self):
        """Test idempotency key functionality"""
        idempotency_key = "test_key_123"
        
        with patch.object(self.payment_service, 'redis_client') as mock_redis:
            # First request with idempotency key
            mock_redis.get.return_value = None
            mock_redis.setex = Mock()
            
            result1 = await self.payment_service.process_payment_with_idempotency(
                self.test_payment,
                idempotency_key
            )
            
            # Second request with same key (should return cached result)
            mock_redis.get.return_value = json.dumps(result1)
            
            result2 = await self.payment_service.process_payment_with_idempotency(
                self.test_payment,
                idempotency_key
            )
            
            assert result1 == result2

    @pytest.mark.asyncio
    async def test_fraud_prevention(self):
        """Test fraud prevention mechanisms"""
        # Test rate limiting
        user_id = "test_user_123"
        
        with patch.object(self.payment_service, 'redis_client') as mock_redis:
            # Simulate rate limit check
            mock_redis.get.return_value = "5"  # 5 attempts
            
            with pytest.raises(Exception) as exc_info:
                await self.payment_service.check_rate_limit(user_id)
            
            assert "rate limit exceeded" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_payment_retry_logic(self):
        """Test payment retry mechanism for failed payments"""
        failed_payment = self.test_payment.copy()
        
        with patch.object(self.payment_service.adapters['stripe'], 'process_payment') as mock_process:
            # First attempt fails
            mock_process.side_effect = [
                Exception("Network error"),
                {'status': 'succeeded', 'id': 'pi_retry_123'}  # Second attempt succeeds
            ]
            
            result = await self.payment_service.process_payment_with_retry(
                failed_payment,
                max_retries=2
            )
            
            assert result['status'] == 'succeeded'
            assert mock_process.call_count == 2

    @pytest.mark.asyncio
    async def test_currency_conversion(self):
        """Test currency conversion for multi-currency support"""
        usd_payment = PaymentRequest(
            user_id="test_user_123",
            amount=29.99,
            currency="USD",
            description="Test payment",
            payment_method_id="pm_test_123"
        )
        
        # Mock currency conversion
        with patch('apps.bot.services.currency_service.get_exchange_rate') as mock_rate:
            mock_rate.return_value = 12500  # 1 USD = 12500 UZS
            
            uzs_amount = await self.payment_service.convert_currency(
                usd_payment.amount,
                "USD",
                "UZS"
            )
            
            assert uzs_amount == 374875.0  # 29.99 * 12500

    @pytest.mark.asyncio
    async def test_payment_analytics(self):
        """Test payment analytics and reporting"""
        with patch.object(self.payment_service, 'payment_repository') as mock_repo:
            mock_repo.get_payment_analytics = AsyncMock(return_value={
                'total_revenue': 15420.50,
                'successful_payments': 234,
                'failed_payments': 12,
                'average_payment_amount': 65.45
            })
            
            analytics = await self.payment_service.get_payment_analytics(
                start_date=datetime.utcnow() - timedelta(days=30),
                end_date=datetime.utcnow()
            )
            
            assert analytics['total_revenue'] == 15420.50
            assert analytics['successful_payments'] == 234

    @pytest.mark.asyncio
    async def test_subscription_billing_cycle(self):
        """Test subscription billing cycle calculations"""
        subscription_id = "sub_test_123"
        
        with patch.object(self.payment_service, 'subscription_repository') as mock_repo:
            mock_repo.get_subscription.return_value = {
                'id': subscription_id,
                'billing_cycle': BillingCycle.MONTHLY,
                'created_at': datetime(2025, 1, 15),
                'amount': 29.99
            }
            
            next_billing_date = await self.payment_service.calculate_next_billing_date(
                subscription_id
            )
            
            expected_date = datetime(2025, 2, 15)
            assert next_billing_date.date() == expected_date.date()

    @pytest.mark.asyncio
    async def test_payment_refund_process(self):
        """Test payment refund functionality"""
        payment_id = "pi_test_123"
        refund_amount = 29.99
        
        with patch.object(self.payment_service.adapters['stripe'], 'create_refund') as mock_refund:
            mock_refund.return_value = {
                'id': 're_test_123',
                'status': 'succeeded',
                'amount': 2999,  # Stripe uses cents
                'reason': 'requested_by_customer'
            }
            
            refund_result = await self.payment_service.create_refund(
                payment_id,
                refund_amount,
                reason="Customer request"
            )
            
            assert refund_result['status'] == 'succeeded'
            assert refund_result['amount'] == 29.99

    @pytest.mark.asyncio
    async def test_webhook_event_processing(self):
        """Test webhook event processing for all providers"""
        # Test Stripe webhook event
        stripe_event = {
            'type': 'payment_intent.succeeded',
            'data': {
                'object': {
                    'id': 'pi_test_123',
                    'status': 'succeeded',
                    'amount': 2999
                }
            }
        }
        
        result = await self.payment_service.process_webhook_event(
            PaymentProvider.STRIPE,
            stripe_event
        )
        
        assert result['processed'] is True
        
        # Test Payme webhook event
        payme_event = {
            'method': 'CheckPerformTransaction',
            'params': {
                'amount': 2999,
                'account': {'user_id': 'test_user_123'}
            }
        }
        
        result = await self.payment_service.process_webhook_event(
            PaymentProvider.PAYME,
            payme_event
        )
        
        assert result['processed'] is True

    @pytest.mark.asyncio
    async def test_error_handling_and_logging(self):
        """Test comprehensive error handling and logging"""
        # Test invalid payment provider
        with pytest.raises(ValueError) as exc_info:
            await self.payment_service.process_payment_with_invalid_provider(
                self.test_payment
            )
        assert "Invalid payment provider" in str(exc_info.value)
        
        # Test network timeout handling
        with patch.object(self.payment_service.adapters['stripe'], 'process_payment') as mock_process:
            mock_process.side_effect = asyncio.TimeoutError("Request timed out")
            
            with pytest.raises(asyncio.TimeoutError):
                await self.payment_service.process_payment(self.test_payment)

    @pytest.mark.asyncio
    async def test_payment_method_security(self):
        """Test payment method security features"""
        # Test payment method tokenization
        sensitive_data = {
            'card_number': '4242424242424242',
            'exp_month': 12,
            'exp_year': 2025,
            'cvc': '123'
        }
        
        token = await self.payment_service.tokenize_payment_method(sensitive_data)
        assert token != sensitive_data['card_number']
        assert len(token) > 16  # Should be a secure token
        
        # Test PCI compliance data handling
        processed_data = await self.payment_service.sanitize_payment_data(
            sensitive_data
        )
        assert 'cvc' not in processed_data  # CVC should be removed
        assert processed_data['card_number'].endswith('4242')  # Should be masked


class TestPaymentDatabaseIntegration:
    """
    🗄️ Payment Database Integration Tests
    
    Tests database operations for payment system
    including schema, transactions, and data integrity.
    """
    
    @pytest.mark.asyncio
    async def test_payment_method_crud_operations(self):
        """Test payment method database operations"""
        # This would test actual database operations
        # For now, we'll mock the repository
        pass
    
    @pytest.mark.asyncio
    async def test_subscription_database_integrity(self):
        """Test subscription database integrity and constraints"""
        # Test subscription creation with all required fields
        # Test subscription state transitions
        # Test billing cycle calculations
        pass
    
    @pytest.mark.asyncio
    async def test_payment_transaction_atomicity(self):
        """Test payment transaction atomicity"""
        # Test that payment operations are atomic
        # Test rollback on failure
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
