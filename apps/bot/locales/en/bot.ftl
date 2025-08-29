# Welcome Messages
start_message = 
    🚀 <b>Welcome to AnalyticBot, { $user_name }!</b>
    
    📊 Your ultimate channel analytics companion
    ✨ Track performance, schedule posts, and grow your audience
    
    🎯 <b>What you can do:</b>
    • 📈 Get detailed channel analytics
    • ⏰ Schedule posts with perfect timing
    • 🛡️ Protect your content from theft
    • 📱 Use our powerful web dashboard
    
    � <b>Quick Start Guide:</b>
    1️⃣ Add your first channel with <code>/add_channel @channel_name</code>
    2️⃣ View analytics with <code>/stats</code>
    3️⃣ Get help anytime with <code>/help</code>
    
    👆 <b>Choose an action below to get started!</b>

welcome_back = 👋 Welcome back, { $user_name }! Ready to analyze?

# Menu Buttons
menu-button-dashboard = 📊 Dashboard
menu-button-analytics = 📈 Analytics  
menu-button-schedule = ⏰ Schedule

# Quick Action Buttons
button-add-channel = 📢 Add Channel
button-view-stats = 📊 View Stats
button-help = ❓ Help
button-commands = 📋 All Commands
menu-button-settings = ⚙️ Settings
menu-button-help = ❓ Help

# Channel Management
add-channel-usage = 
    📢 <b>Add Channel Command</b>
    
    💡 <b>Usage:</b> <code>/add_channel @your_channel</code>
    
    ⚠️ <b>Requirements:</b>
    • You must be admin/owner of the channel
    • Channel must be public or add bot as admin
    • Channel username required (not invite link)
    
    📝 <b>Example:</b> <code>/add_channel @techchannel</code>

add-channel-not-found = 
    ❌ <b>Channel Not Found</b>
    
    🔍 Make sure:
    • Channel username is correct
    • Channel is public or bot is added as admin
    • You're using @ before channel name
    
    💡 Try: <code>/add_channel @channelname</code>

add-channel-success = 
    ✅ <b>Channel Added Successfully!</b>
    
    📢 <b>Channel:</b> { $channel_title }
    🆔 <b>ID:</b> <code>{ $channel_id }</code>
    
    🎉 You can now:
    • 📊 View analytics with /stats
    • ⏰ Schedule posts with /schedule  
    • 🛡️ Protect content with /protect
    
    🚀 <b>Start analyzing your growth!</b>

channel-list-header = 📢 <b>Your Channels</b>
channel-list-empty = 
    📭 <b>No Channels Added Yet</b>
    
    💡 Add your first channel with:
    <code>/add_channel @your_channel</code>

channel-list-item = 📢 <b>{ $channel_name }</b> | 👥 { $member_count } members

# Content Protection
guard-add-usage = 
    🛡️ <b>Add Protected Word</b>
    
    💡 <b>Usage:</b> <code>/add_word secret_word</code>
    
    🔒 <b>What it does:</b>
    • Detects if your content is copied
    • Monitors across Telegram channels
    • Alerts you of potential theft
    
    📝 <b>Example:</b> <code>/add_word MyUniqueTag2024</code>

guard-remove-usage = 
    🗑️ <b>Remove Protected Word</b>
    
    💡 <b>Usage:</b> <code>/remove_word word_to_remove</code>
    
    📝 <b>Example:</b> <code>/remove_word MyUniqueTag2024</code>

guard-list-usage = 
    📋 <b>List Protected Words</b>
    
    💡 <b>Usage:</b> <code>/list_words</code>
    
    📊 See all words being monitored for theft protection

guard-channel-not-found = 
    ❌ <b>Channel Not Found</b>
    
    💡 Add your channel first with:
    <code>/add_channel @your_channel</code>

guard-channel-not-owner = 
    🚫 <b>Access Denied</b>
    
    ⚠️ You must be admin or owner of this channel
    🔑 Check your permissions and try again

guard-channel-not-registered = 
    ❌ <b>Channel Not Registered</b>
    
    💡 Register your channel first:
    <code>/add_channel @your_channel</code>

guard-word-added = 
    ✅ <b>Word Added to Protection!</b>
    
    🛡️ <b>"{ $word }"</b> is now being monitored
    🔍 We'll alert you if content theft is detected
    
    📊 View all protected words: <code>/list_words</code>

guard-word-removed = 
    ✅ <b>Word Removed</b>
    
    🗑️ <b>"{ $word }"</b> is no longer monitored
    
    📊 View remaining words: <code>/list_words</code>

guard-list-header = 
    🛡️ <b>Protected Words</b>
    
    🔍 <b>Currently monitoring { $count } words:</b>

guard-list-empty = 
    📭 <b>No Protected Words</b>
    
    💡 Add words to monitor for content theft:
    <code>/add_word your_unique_tag</code>

guard-list-item = 🔍 <code>{ $word }</code>

# User Plans & Subscriptions  
myplan-header = 
    💎 <b>Your Subscription Plan</b>
    
    📊 Current plan details:

myplan-plan-name = 
    📋 <b>Plan:</b> { $name }
    ⭐ <b>Status:</b> Active
    
myplan-features = 
    ✨ <b>Your Features:</b>
    • 📊 Advanced analytics
    • ⏰ Smart scheduling  
    • 🛡️ Content protection
    • 📱 Web dashboard access
    
myplan-upgrade-prompt = 
    🚀 <b>Ready to Upgrade?</b>
    
    💎 Get access to:
    • 📈 Real-time analytics
    • 🤖 AI-powered insights
    • 📊 Advanced reporting
    • 🎯 Growth recommendations
    
    💳 <b>Upgrade now and boost your growth!</b>

myplan-error = 
    ❌ <b>Plan Information Unavailable</b>
    
    🔄 Please try again in a moment
    💬 Contact support if issue persists

# Scheduling
schedule-usage = 
    ⏰ <b>Schedule Post Command</b>
    
    💡 <b>Usage:</b> <code>/schedule 15:30 Your post content</code>
    
    📅 <b>Time Formats:</b>
    • <code>HH:MM</code> - Today at specific time
    • <code>DD/MM HH:MM</code> - Specific date & time
    • <code>tomorrow 15:30</code> - Tomorrow
    
    📝 <b>Examples:</b>
    • <code>/schedule 18:00 🎉 New product launch!</code>
    • <code>/schedule 25/12 09:00 🎄 Merry Christmas!</code>

schedule-past-time-error = 
    ⏰ <b>Invalid Time</b>
    
    ❌ You can't schedule posts in the past!
    📅 Please choose a future time
    
    💡 <b>Try:</b> <code>/schedule 18:00 Your content</code>

schedule-success = 
    ✅ <b>Post Scheduled Successfully!</b>
    
    📢 <b>Channel:</b> { $channel_name }
    ⏰ <b>Time:</b> { $schedule_time }
    
    🎯 Your post will be published automatically
    📊 <b>View all scheduled posts:</b> <code>/myposts</code>

schedule-list-header = 
    📅 <b>Your Scheduled Posts</b>
    
    📊 <b>{ $count } posts scheduled:</b>

schedule-list-empty = 
    📭 <b>No Scheduled Posts</b>
    
    💡 Schedule your first post:
    <code>/schedule 18:00 Your amazing content</code>

schedule-list-item = 
    ⏰ <b>{ $time }</b> → 📢 { $channel }
    💬 { $content }

# Analytics & Statistics
stats-usage = 
    📊 <b>Analytics Command</b>
    
    💡 <b>Usage:</b> 
    • <code>/stats @channel</code> - Channel analytics
    • <code>/stats post_id</code> - Specific post stats
    • <code>/stats</code> - All channels overview
    
    📈 <b>Get insights on:</b>
    • 👥 Subscriber growth
    • 👀 Views & engagement
    • 📅 Performance trends
    • 🎯 Best posting times

stats-generating = 
    📊 <b>Generating Analytics...</b>
    
    🔄 Processing your data
    ⏳ This might take a moment

stats-no-data = 
    📊 <b>No Analytics Data</b>
    
    💡 <b>Possible reasons:</b>
    • Channel is too new
    • Not enough posts yet
    • Bot needs admin access
    
    ⏳ Try again in a few hours

stats-caption-all = 
    📊 <b>Complete Analytics Report</b>
    📅 Generated on { $date }

stats-caption-specific = 
    📈 <b>Detailed Analytics</b>
    🎯 Performance insights

# Views Tracking
views-usage = 
    👀 <b>Post Views Command</b>
    
    💡 <b>Usage:</b> <code>/views post_id</code>
    
    📊 Get detailed view counts for any post
    📈 Track engagement over time
    
    📝 <b>Example:</b> <code>/views 1234</code>

views-invalid-id = 
    ❌ <b>Invalid Post ID</b>
    
    💡 Please provide a valid post ID number
    📝 <b>Example:</b> <code>/views 1234</code>

views-not-found = 
    ❌ <b>Post Not Found</b>
    
    🔍 Make sure:
    • Post ID is correct
    • Post exists in your channels
    • You have access to the post

views-success = 
    👀 <b>Post Views Report</b>
    
    📄 <b>Post ID:</b> { $post_id }
    👀 <b>Total Views:</b> { $view_count }
    
    📊 <b>Want detailed analytics?</b>
    Use: <code>/stats { $post_id }</code>

# Web App Integration
twa-data-received-post = 
    ✅ <b>Data Received Successfully!</b>
    
    📱 Your web app action has been processed
    🔄 Changes will be reflected shortly

dashboard-opening = 
    📊 <b>Opening Dashboard...</b>
    
    📱 Your analytics dashboard is loading
    💡 Use the web interface for detailed insights

# Errors & Help
error-general = 
    ❌ <b>Something went wrong</b>
    
    🔄 Please try again
    💬 Contact support if issue persists

error-permission-denied = 
    🚫 <b>Permission Denied</b>
    
    ⚠️ You don't have permission for this action
    🔑 Make sure you're an admin of the channel

error-rate-limited = 
    ⏸️ <b>Too Many Requests</b>
    
    🕐 Please wait a moment and try again
    💡 Rate limiting helps keep the service stable

help-message = 
    ❓ <b>AnalyticBot Help Center</b>
    
    🚀 <b>Quick Commands:</b>
    • <code>/start</code> - Main menu
    • <code>/add_channel @channel</code> - Add channel
    • <code>/stats</code> - View analytics
    • <code>/schedule time content</code> - Schedule post
    • <code>/dashboard</code> - Open web dashboard
    
    💡 <b>Need more help?</b>

# Commands List
commands-list = 
    📋 <b>All Available Commands</b>
    
    📊 <b>Analytics Commands:</b>
    • <code>/stats</code> - View channel analytics
    • <code>/add_channel @channel_name</code> - Add a channel to track
    • <code>/remove_channel @channel_name</code> - Remove channel
    • <code>/channels</code> - List your channels
    
    ⏰ <b>Scheduling Commands:</b>
    • <code>/schedule HH:MM text</code> - Schedule a post
    • <code>/scheduled</code> - View scheduled posts
    
    🛠️ <b>Other Commands:</b>
    • <code>/dashboard</code> - Open web dashboard  
    • <code>/myplan</code> - Check your subscription
    • <code>/help</code> - Show help center
    • <code>/start</code> - Back to main menu
    
    💡 <b>Tip:</b> Use buttons for easier navigation!
    📞 Contact support: @support
    📖 Documentation: /docs

# Success Messages
success-general = ✅ <b>Operation completed successfully!</b>
processing = 🔄 <b>Processing...</b>
loading = ⏳ <b>Loading...</b>

# Navigation
back-button = ⬅️ Back
next-button = ➡️ Next
cancel-button = ❌ Cancel
confirm-button = ✅ Confirm
