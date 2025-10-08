---
name: ⚡ Performance Issue
about: Report performance problems or optimization opportunities
title: "[PERFORMANCE] "
labels: ["performance", "needs-testing"]
assignees: []
---

## Performance Issue Type
- [ ] Slow response times
- [ ] High memory usage
- [ ] High CPU usage
- [ ] Database performance
- [ ] Network latency
- [ ] Frontend rendering
- [ ] Large payload sizes
- [ ] Inefficient algorithms
- [ ] Memory leaks
- [ ] Slow startup time

## Problem Description
**Describe the performance issue in detail:**

## Performance Metrics
**Current performance measurements:**

### Response Times
- Current average: [X]ms
- Current p95: [X]ms
- Current p99: [X]ms
- Expected/target: [X]ms

### Resource Usage
- Memory usage: [X]MB
- CPU usage: [X]%
- Database query time: [X]ms
- Network payload size: [X]KB

### Throughput
- Current RPS: [X]
- Expected RPS: [X]
- Concurrent users affected: [X]

## Steps to Reproduce
**How to reproduce the performance issue:**

1.
2.
3.

## Environment Information
- **Environment:** Production/Staging/Development
- **Load:** [Number of concurrent users/requests]
- **Time of day:** [When the issue occurs]
- **Duration:** [How long the issue persists]

### System Specs
- CPU: [cores, type]
- Memory: [amount]
- Storage: [type, specs]
- Network: [connection type]

### Application Info
- Application version:
- Database version:
- Cache configuration:
- Load balancer configuration:

## Monitoring Data
**Include relevant monitoring information:**

### Screenshots/Graphs
[Attach performance monitoring screenshots]

### Log Snippets
```
[Relevant log entries showing slow operations]
```

### Database Queries
```sql
-- Slow queries identified
```

## Impact Assessment
- [ ] Critical - Application unusable
- [ ] High - Significant user impact
- [ ] Medium - Noticeable slowness
- [ ] Low - Minor performance concern

**Users Affected:** [number or percentage]
**Business Impact:** [revenue, user experience, etc.]

## Analysis Done
**What investigation has been completed?**

- [ ] Profiling completed
- [ ] Database query analysis
- [ ] Network analysis
- [ ] Memory profiling
- [ ] Load testing performed
- [ ] Code review completed

## Potential Root Causes
**What might be causing the performance issue?**

1.
2.
3.

## Proposed Solutions
**If you have ideas for fixing the performance issue:**

### Short-term fixes:
1.
2.

### Long-term optimizations:
1.
2.

## Benchmarking
**Performance benchmarks to validate fixes:**

- [ ] Load testing with [X] concurrent users
- [ ] Memory usage under [X] conditions
- [ ] Response time targets: [X]ms p95
- [ ] Throughput targets: [X] RPS

---

### For Performance Team

**Priority:**
- [ ] P0 - Critical performance degradation
- [ ] P1 - High impact performance issue
- [ ] P2 - Medium performance concern
- [ ] P3 - Optimization opportunity

**Investigation Required:**
- [ ] Profiling with tools (py-spy, memory-profiler)
- [ ] Database query optimization
- [ ] Load testing
- [ ] Code review for algorithms
- [ ] Infrastructure scaling assessment

**Success Criteria:**
- [ ] Response time improved by [X]%
- [ ] Memory usage reduced by [X]%
- [ ] Throughput increased by [X]%
- [ ] User experience metrics improved
