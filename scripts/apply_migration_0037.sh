#!/bin/bash

# Apply Migration 0037: Drop 164 unused indexes
# CONCURRENTLY requires running outside transactions, so we execute each DROP separately

set -e

CONTAINER="analyticbot-db"
DB_USER="analytic"
DB_NAME="analytic_bot"

echo "========================================"
echo "Migration 0037: Dropping Unused Indexes"
echo "========================================"
echo "Started: $(date)"
echo ""

TOTAL_DROPPED=0
TOTAL_ERRORS=0

# Function to drop an index
drop_index() {
    local index_name=$1
    local table_name=$2

    echo -n "Dropping $index_name... "

    if docker exec $CONTAINER psql -U $DB_USER -d $DB_NAME -c "DROP INDEX CONCURRENTLY IF EXISTS $index_name;" > /dev/null 2>&1; then
        echo "✅"
        ((TOTAL_DROPPED++))
    else
        echo "❌ (may not exist)"
        ((TOTAL_ERRORS++))
    fi
}

echo "📦 Admin tables..."
drop_index "ix_admin_api_keys_expires_at" "admin_api_keys"
drop_index "ix_admin_api_keys_is_active" "admin_api_keys"
drop_index "ix_admin_audit_log_action" "admin_audit_log"
drop_index "ix_admin_audit_log_admin_user_id" "admin_audit_log"
drop_index "ix_admin_audit_log_resource" "admin_audit_log"
drop_index "ix_admin_audit_log_timestamp" "admin_audit_log"
drop_index "idx_admin_actions_action" "admin_bot_actions"
drop_index "idx_admin_actions_admin_id" "admin_bot_actions"
drop_index "idx_admin_actions_target_user" "admin_bot_actions"
drop_index "idx_admin_actions_timestamp" "admin_bot_actions"
drop_index "ix_admin_sessions_admin_user_id" "admin_sessions"
drop_index "ix_admin_sessions_expires_at" "admin_sessions"
drop_index "ix_admin_sessions_is_active" "admin_sessions"
drop_index "ix_superadmin_users_is_active" "admin_users"
drop_index "ix_superadmin_users_role_id" "admin_users"
drop_index "ix_superadmin_users_user_id" "admin_users"
echo ""

echo "📦 Alert tables..."
drop_index "ix_alert_sent_status" "alert_sent"
drop_index "ix_alert_sent_user_channel_type_time" "alert_sent"
drop_index "ix_alert_sent_user_time" "alert_sent"
drop_index "ix_alert_subscriptions_chat_channel" "alert_subscriptions"
drop_index "ix_alert_subscriptions_enabled" "alert_subscriptions"
drop_index "ix_alert_subscriptions_kind" "alert_subscriptions"
drop_index "ix_alerts_sent_sent_at" "alerts_sent"
echo ""

echo "📦 Bot health metrics..."
drop_index "idx_bot_health_status_timestamp" "bot_health_metrics"
drop_index "idx_bot_health_timestamp" "bot_health_metrics"
drop_index "idx_bot_health_user_id" "bot_health_metrics"
drop_index "idx_bot_health_user_timestamp" "bot_health_metrics"
echo ""

echo "📦 Channel daily..."
drop_index "idx_channel_daily_channel_metric" "channel_daily"
drop_index "idx_channel_daily_day" "channel_daily"
drop_index "idx_channel_daily_metric_day" "channel_daily"
echo ""

echo "📦 Channel MTProto settings..."
drop_index "ix_channel_mtproto_settings_channel_id" "channel_mtproto_settings"
drop_index "ix_channel_mtproto_settings_user_id" "channel_mtproto_settings"
drop_index "ix_channel_mtproto_user_enabled" "channel_mtproto_settings"
echo ""

echo "📦 Channels table (12 of 16)..."
drop_index "idx_channels_is_active" "channels"
drop_index "idx_channels_performance_lookup" "channels"
drop_index "idx_channels_subscriber_count" "channels"
drop_index "idx_channels_user_active" "channels"
drop_index "idx_channels_user_analytics_cover" "channels"
drop_index "idx_channels_user_count" "channels"
drop_index "idx_channels_user_dashboard" "channels"
drop_index "idx_channels_user_id" "channels"
drop_index "ix_channels_auto_moderation" "channels"
drop_index "ix_channels_created_at" "channels"
drop_index "ix_channels_last_content_scan" "channels"
drop_index "ix_channels_protection_level" "channels"
echo ""

echo "📦 Content moderation..."
drop_index "ix_content_analysis_analysis_type" "content_analysis"
drop_index "ix_content_analysis_analyzed_at" "content_analysis"
drop_index "ix_content_analysis_channel_id" "content_analysis"
drop_index "ix_content_analysis_tags" "content_analysis"
drop_index "ix_content_filters_filter_type" "content_filters"
drop_index "ix_content_filters_is_active" "content_filters"
drop_index "ix_content_filters_severity" "content_filters"
drop_index "ix_content_violations_channel_id" "content_violations"
drop_index "ix_content_violations_detected_at" "content_violations"
drop_index "ix_content_violations_severity" "content_violations"
drop_index "ix_content_violations_status" "content_violations"
drop_index "ix_content_violations_violation_type" "content_violations"
echo ""

echo "📦 Deliveries..."
drop_index "ix_deliveries_attempted_at" "deliveries"
drop_index "ix_deliveries_channel_id" "deliveries"
drop_index "ix_deliveries_created_at" "deliveries"
drop_index "ix_deliveries_delivered_at" "deliveries"
drop_index "ix_deliveries_pending" "deliveries"
drop_index "ix_deliveries_post_id" "deliveries"
drop_index "ix_deliveries_retryable" "deliveries"
drop_index "ix_deliveries_status" "deliveries"
echo ""

echo "📦 MTProto audit log..."
drop_index "ix_mtproto_audit_log_channel_id" "mtproto_audit_log"
drop_index "ix_mtproto_audit_log_timestamp" "mtproto_audit_log"
drop_index "ix_mtproto_audit_log_user_id" "mtproto_audit_log"
drop_index "ix_mtproto_audit_user_timestamp" "mtproto_audit_log"
echo ""

echo "📦 Muted channels..."
drop_index "ix_muted_channels_muted_until" "muted_channels"
echo ""

echo "📦 Materialized views..."
drop_index "idx_mv_post_metrics_recent_views" "mv_post_metrics_recent"
echo ""

echo "📦 Payment tables..."
drop_index "ix_payment_methods_provider" "payment_methods"
drop_index "ix_payment_methods_user_id" "payment_methods"
drop_index "idx_payments_user_status_date" "payments"
drop_index "ix_payments_created_at" "payments"
drop_index "ix_payments_provider" "payments"
drop_index "ix_payments_status" "payments"
drop_index "ix_payments_user_id" "payments"
echo ""

echo "📦 Post metrics (5 of 7)..."
drop_index "idx_post_metrics_channel_msg" "post_metrics"
drop_index "idx_post_metrics_comments" "post_metrics"
drop_index "idx_post_metrics_covering" "post_metrics"
drop_index "idx_post_metrics_replies" "post_metrics"
drop_index "idx_post_metrics_snapshot_time" "post_metrics"
echo ""

echo "📦 Posts table (9 of 12)..."
drop_index "idx_posts_channel_date" "posts"
drop_index "idx_posts_channel_date_active" "posts"
drop_index "idx_posts_channel_id_active" "posts"
drop_index "idx_posts_channel_not_deleted" "posts"
drop_index "idx_posts_content_type" "posts"
drop_index "idx_posts_date_content" "posts"
drop_index "idx_posts_images_only" "posts"
drop_index "idx_posts_is_deleted" "posts"
drop_index "idx_posts_videos_only" "posts"
echo ""

echo "📦 Reporting snapshots..."
drop_index "ix_reporting_snapshots_channel_id" "reporting_snapshots"
drop_index "ix_reporting_snapshots_snapshot_date" "reporting_snapshots"
echo ""

echo "📦 Scheduled posts (18 of 19)..."
drop_index "idx_scheduled_posts_analytics_agg" "scheduled_posts"
drop_index "idx_scheduled_posts_channel_status_time" "scheduled_posts"
drop_index "idx_scheduled_posts_recent_activity" "scheduled_posts"
drop_index "idx_scheduled_posts_schedule_time_status" "scheduled_posts"
drop_index "idx_scheduled_posts_timeseries" "scheduled_posts"
drop_index "idx_scheduled_posts_tracking_cover" "scheduled_posts"
drop_index "idx_scheduled_posts_trending" "scheduled_posts"
drop_index "idx_scheduled_posts_user_activity" "scheduled_posts"
drop_index "idx_scheduled_posts_user_created_views" "scheduled_posts"
drop_index "idx_scheduled_posts_user_id_status" "scheduled_posts"
drop_index "idx_scheduled_posts_view_tracking_cover" "scheduled_posts"
drop_index "idx_scheduled_posts_views_desc" "scheduled_posts"
drop_index "ix_scheduled_posts_channel_id" "scheduled_posts"
drop_index "ix_scheduled_posts_created_at" "scheduled_posts"
drop_index "ix_scheduled_posts_status_enhanced" "scheduled_posts"
drop_index "ix_scheduled_posts_status_schedule_time" "scheduled_posts"
drop_index "ix_scheduled_posts_user_created_at" "scheduled_posts"
drop_index "ix_scheduled_posts_user_id" "scheduled_posts"
echo ""

echo "📦 Sent posts..."
drop_index "idx_sent_posts_analytics_composite" "sent_posts"
drop_index "idx_sent_posts_channel_stats" "sent_posts"
drop_index "idx_sent_posts_join_optimization" "sent_posts"
drop_index "ix_sent_posts_channel_id" "sent_posts"
drop_index "ix_sent_posts_scheduled_post_id" "sent_posts"
drop_index "ix_sent_posts_sent_at" "sent_posts"
drop_index "ix_sent_posts_status" "sent_posts"
drop_index "ix_sent_posts_views" "sent_posts"
echo ""

echo "📦 Shared reports..."
drop_index "ix_shared_reports_channel_id" "shared_reports"
drop_index "ix_shared_reports_token" "shared_reports"
echo ""

echo "📦 Subscriptions..."
drop_index "ix_subscriptions_expires_at" "subscriptions"
drop_index "ix_subscriptions_payment_method_id" "subscriptions"
drop_index "ix_subscriptions_plan_id" "subscriptions"
drop_index "ix_subscriptions_status" "subscriptions"
drop_index "ix_subscriptions_user_id" "subscriptions"
echo ""

echo "📦 Telegram media..."
drop_index "ix_telegram_media_channel_id" "telegram_media"
drop_index "ix_telegram_media_file_type" "telegram_media"
drop_index "ix_telegram_media_msg_id" "telegram_media"
drop_index "ix_telegram_media_post_id" "telegram_media"
drop_index "ix_telegram_media_uploaded" "telegram_media"
drop_index "ix_telegram_media_uploaded_at" "telegram_media"
drop_index "ix_telegram_media_user_id" "telegram_media"
echo ""

echo "📦 User bot credentials..."
drop_index "idx_bot_credentials_active" "user_bot_credentials"
drop_index "idx_bot_credentials_health_status" "user_bot_credentials"
drop_index "idx_bot_credentials_last_used" "user_bot_credentials"
drop_index "idx_bot_credentials_user_id" "user_bot_credentials"
drop_index "ix_user_bot_credentials_created_at" "user_bot_credentials"
drop_index "ix_user_bot_credentials_is_active" "user_bot_credentials"
drop_index "ix_user_bot_credentials_user_id" "user_bot_credentials"
echo ""

echo "📦 User storage channels..."
drop_index "ix_user_storage_channels_channel_id" "user_storage_channels"
drop_index "ix_user_storage_channels_channel_title" "user_storage_channels"
drop_index "ix_user_storage_channels_created_at" "user_storage_channels"
drop_index "ix_user_storage_channels_is_active" "user_storage_channels"
drop_index "ix_user_storage_channels_user_id" "user_storage_channels"
echo ""

echo "📦 Users table..."
drop_index "idx_users_active_count" "users"
drop_index "idx_users_email" "users"
drop_index "idx_users_id_active" "users"
drop_index "idx_users_phone_number" "users"
drop_index "idx_users_username" "users"
drop_index "ix_users_created_at" "users"
drop_index "ix_users_is_active" "users"
drop_index "ix_users_plan_id" "users"
echo ""

echo "📦 Webhook events..."
drop_index "ix_webhook_events_created_at" "webhook_events"
drop_index "ix_webhook_events_event_type" "webhook_events"
drop_index "ix_webhook_events_processed" "webhook_events"
drop_index "ix_webhook_events_user_id" "webhook_events"
echo ""

# Update migration version
echo "📝 Updating alembic_version..."
docker exec $CONTAINER psql -U $DB_USER -d $DB_NAME -c "UPDATE alembic_version SET version_num = '0037';" > /dev/null 2>&1
echo "✅"
echo ""

echo "========================================"
echo "✅ Migration 0037 Complete"
echo "========================================"
echo "Finished: $(date)"
echo ""
echo "Summary:"
echo "  • Indexes dropped: $TOTAL_DROPPED"
echo "  • Errors/Skipped: $TOTAL_ERRORS"
echo ""

# Show final stats
echo "Final Index Statistics:"
docker exec $CONTAINER psql -U $DB_USER -d $DB_NAME -c "
SELECT
    COUNT(*) as remaining_indexes,
    pg_size_pretty(SUM(pg_relation_size(indexrelid))) as total_index_size
FROM pg_stat_user_indexes
WHERE schemaname = 'public';
"
