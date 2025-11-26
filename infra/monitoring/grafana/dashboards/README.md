# AnalyticBot API Performance Dashboard

**Dashboard File:** `api-performance.json`
**Grafana Version:** 10.0+
**Data Source:** Prometheus
**Auto-Refresh:** 30 seconds

## 📊 Dashboard Overview

Comprehensive real-time monitoring dashboard for AnalyticBot API performance with 7 panels covering all critical metrics.

## 🎯 Panels

### 1. 📊 API Request Rate
- **Metric:** HTTP requests per second
- **Type:** Time series graph
- **Query:** `rate(http_requests_total{job="analyticbot-api"}[5m])`
- **Breakdown:** By HTTP method (GET, POST, PUT, DELETE) and endpoint
- **Shows:** Traffic patterns, load distribution, peak hours
- **Legend:** mean, max, current

### 2. ⚡ API Response Time
- **Metrics:** p95, p99, and average response times
- **Type:** Time series graph
- **Unit:** Milliseconds
- **Thresholds:**
  - Green: <200ms (excellent)
  - Yellow: 200-500ms (acceptable)
  - Orange: 500-1000ms (slow)
  - Red: >1000ms (critical)
- **SLA Target:** p95 <200ms, p99 <500ms
- **Shows:** Performance trends, slowdowns, optimization opportunities

### 3. 🚨 API Error Rate
- **Metrics:** 4xx errors, 5xx errors, total error rate
- **Type:** Time series graph
- **Unit:** Percentage
- **Thresholds:**
  - Green: <1% (healthy)
  - Yellow: 1-3% (warning)
  - Orange: 3-5% (degraded)
  - Red: >5% (critical)
- **Breakdown:**
  - 4xx: Client errors (bad requests, auth failures)
  - 5xx: Server errors (bugs, crashes)
- **SLA Target:** <1% total error rate

### 4. 📺 Active Channels
- **Type:** Gauge
- **Metric:** Number of channels with active data collection
- **Query:** `count(count by (channel_id) (channel_metrics{job="analyticbot-api"}))`
- **Shows:** Platform usage, customer count
- **Useful for:** Capacity planning, growth tracking

### 5. ✅ Success Rate
- **Type:** Gauge
- **Metric:** Percentage of 2xx HTTP responses
- **Thresholds:**
  - Red: <95%
  - Yellow: 95-99%
  - Green: >99%
- **SLA Target:** >99.5% success rate
- **Shows:** Overall system health at a glance

### 6. 📍 Top Endpoints by Request Volume
- **Type:** Donut chart
- **Shows:** Distribution of requests across endpoints
- **Useful for:**
  - Identifying most-used endpoints
  - Capacity planning per endpoint
  - Caching strategy optimization
  - Rate limiting configuration

### 7. 📋 Endpoint Performance Table
- **Type:** Sortable table
- **Columns:**
  - Endpoint path
  - Requests per second
  - p95 response time (ms)
  - Error rate (%)
- **Features:**
  - Sortable by any column
  - Color-coded thresholds
  - Shows slowest/busiest/most-error-prone endpoints
- **Useful for:**
  - Performance troubleshooting
  - Optimization prioritization
  - SLA compliance verification

## 🚀 Installation

### Option 1: Grafana UI (Manual Import)

1. **Open Grafana** (http://localhost:3000)
2. **Navigate:** Dashboards → Import
3. **Upload JSON:**
   ```bash
   # Copy the file path
   /home/abcdeveloper/projects/analyticbot/infra/monitoring/grafana/dashboards/api-performance.json
   ```
4. **Select Data Source:** Choose your Prometheus instance
5. **Click:** Import

### Option 2: Provisioning (Automatic)

1. **Copy to Grafana provisioning directory:**
   ```bash
   # Docker volume mount
   cp api-performance.json /var/lib/grafana/dashboards/

   # Or update docker-compose.yml
   volumes:
     - ./infra/monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
   ```

2. **Create provisioning config** (if not exists):
   ```yaml
   # /etc/grafana/provisioning/dashboards/dashboard.yml
   apiVersion: 1
   providers:
     - name: 'AnalyticBot'
       type: file
       disableDeletion: false
       updateIntervalSeconds: 30
       allowUiUpdates: true
       options:
         path: /etc/grafana/provisioning/dashboards
   ```

3. **Restart Grafana:**
   ```bash
   docker-compose restart grafana
   ```

### Option 3: Grafana API

```bash
# Set your Grafana credentials
GRAFANA_URL="http://localhost:3000"
GRAFANA_API_KEY="your-api-key-here"

# Import dashboard via API
curl -X POST "$GRAFANA_URL/api/dashboards/db" \
  -H "Authorization: Bearer $GRAFANA_API_KEY" \
  -H "Content-Type: application/json" \
  -d @api-performance.json
```

## ⚙️ Configuration

### Required Prometheus Metrics

This dashboard requires the following Prometheus metrics from your FastAPI app:

```python
# In your FastAPI app (apps/api/main.py or middleware)
from prometheus_client import Counter, Histogram

# Request counter
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'path', 'status_code', 'job']
)

# Response time histogram
http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'path', 'job']
)

# Channel metrics (if tracking)
channel_metrics = Gauge(
    'channel_metrics',
    'Channel activity metrics',
    ['channel_id', 'job']
)
```

### Prometheus Configuration

Ensure your `prometheus.yml` includes:

```yaml
scrape_configs:
  - job_name: 'analyticbot-api'
    static_configs:
      - targets: ['api:8000']  # Or your API host:port
    scrape_interval: 10s
    metrics_path: /metrics
```

### Customize Refresh Rate

Edit the dashboard JSON or change in Grafana UI:
- Current: 30 seconds (balanced)
- High-frequency: 10 seconds (more load on Prometheus)
- Low-frequency: 1-5 minutes (reduce load)

### Customize Time Range

Default: Last 1 hour
Options: Last 5m, 15m, 1h, 6h, 24h, 7d

```json
// In dashboard JSON
"time": {
  "from": "now-6h",  // Change this
  "to": "now"
}
```

## 📈 Usage Scenarios

### 1. **Daily Operations Monitoring**
- Check dashboard every morning
- Verify all panels are green
- Note any anomalies from previous day
- Set up alerts for critical thresholds

### 2. **Incident Response**
- Dashboard auto-refreshes during incidents
- Use Error Rate panel to identify when issue started
- Check Endpoint Performance Table to find problematic endpoint
- Use Response Time panel to confirm recovery

### 3. **Performance Optimization**
- Sort Endpoint Performance Table by "p95 (ms)"
- Identify slowest endpoints
- Add caching, optimize queries, or scale those endpoints
- Monitor improvement over time

### 4. **Capacity Planning**
- Track Active Channels growth
- Monitor Request Rate trends
- Identify if scaling is needed
- Plan infrastructure upgrades

### 5. **SLA Verification**
- Check Success Rate gauge (target: >99.5%)
- Verify Error Rate <1%
- Confirm p95 response time <200ms
- Generate monthly reports from historical data

## 🚨 Alerting Recommendations

### Critical Alerts (PagerDuty/On-call)
```yaml
# Prometheus alerting rules
groups:
  - name: api_critical
    rules:
      - alert: HighErrorRate
        expr: (sum(rate(http_requests_total{status_code=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "API error rate >5% for 5 minutes"

      - alert: APIDown
        expr: up{job="analyticbot-api"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "API is down"
```

### Warning Alerts (Slack/Email)
```yaml
  - name: api_warnings
    rules:
      - alert: SlowResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 0.5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "API p95 response time >500ms"

      - alert: ElevatedErrorRate
        expr: (sum(rate(http_requests_total{status_code=~"5.."}[5m])) / sum(rate(http_requests_total[5m]))) > 0.01
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "API error rate >1%"
```

## 🔧 Troubleshooting

### Dashboard shows "No data"
- ✅ Check Prometheus is running: `docker ps | grep prometheus`
- ✅ Verify API is exposing metrics: `curl http://localhost:8000/metrics`
- ✅ Check Prometheus targets: http://localhost:9090/targets
- ✅ Verify job name matches: `job="analyticbot-api"`

### Missing panels/metrics
- ✅ Update FastAPI app to export required metrics (see Configuration section)
- ✅ Check Prometheus scrape config
- ✅ Verify metric names in PromQL queries

### Slow dashboard loading
- ✅ Increase Prometheus retention
- ✅ Add more Prometheus resources (CPU/memory)
- ✅ Reduce scrape frequency in prometheus.yml
- ✅ Reduce dashboard auto-refresh rate

### Incorrect values
- ✅ Check time range (top-right)
- ✅ Verify timezone settings
- ✅ Ensure Prometheus time sync is correct
- ✅ Check for gaps in metric collection

## 📊 Sample Screenshots (Expected Output)

### Healthy System
- Request Rate: Smooth line, 10-50 req/s
- Response Time: p95 <100ms (green zone)
- Error Rate: 0-0.5% (green)
- Success Rate: 99.8% (green gauge)

### Under Load
- Request Rate: Spikes to 100+ req/s
- Response Time: p95 150-250ms (yellow zone)
- Error Rate: Still <1%
- Success Rate: 99%+

### Degraded/Incident
- Request Rate: May drop (users giving up)
- Response Time: p95 >500ms (red zone)
- Error Rate: 3-10% (orange/red)
- Success Rate: <95% (red gauge)

## 🎯 Next Steps

1. **Add More Panels:**
   - Database connection pool status
   - Redis cache hit rate
   - Celery task queue length
   - Memory/CPU usage

2. **Create Alert Rules:**
   - Use Grafana Alerting or Prometheus Alertmanager
   - Configure notification channels (Slack, PagerDuty, Email)

3. **Add Business Metrics:**
   - User registrations per hour
   - Active users
   - Revenue-related metrics

4. **Set Up SLO Dashboard:**
   - Define Service Level Objectives
   - Track SLO compliance
   - Calculate error budgets

## 📚 Resources

- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Query Guide](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [FastAPI Prometheus Integration](https://github.com/trallnag/prometheus-fastapi-instrumentator)
- [AnalyticBot Monitoring Setup](../../README.md)

---

**Dashboard Version:** 1.0
**Last Updated:** November 23, 2025
**Maintained By:** AnalyticBot DevOps Team
