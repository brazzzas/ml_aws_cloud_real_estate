# Monitoring

The dashboard is designed for real-time monitoring of the machine learning service.
It allows tracking the correctness of the ML model, API load, as well as the application process status and resource usage.

Monitoring is built on metrics automatically collected by Prometheus, as well as custom metrics added to the application code.

## Metrics from several layers are selected for monitoring:

### Infrastructure Layer

#### Metric: `process_resident_memory_bytes`

This metric reflects the actual RAM consumption by the application process. An increase in value may indicate memory leaks, increased load, or inefficient model operation.

**Gauge** visualization is used, as in this case it is important to see the current state of the resource relative to permissible threshold values.

---

#### Metric: `process_cpu_seconds_total`

The metric shows the total CPU consumption by the application process and allows estimating the computational load created by model inference and HTTP request processing.

**Time series** (linear graph) is used, since it is important to track load changes over time and identify peak values.

---

### Real-time Metrics (ML Level)

#### Metric: Mean prediction value
(`price_histogram_sum / price_histogram_count`)

The metric is used to control model behavior over time. Sharp changes in the mean value may indicate input data distribution shift (data drift) or incorrect model operation.

**Linear graph** is used, as trend analysis is more important than single values.

---

#### Metric: Median prediction (p50)
(`histogram_quantile(0.5, price_histogram_bucket)`)

The median is less sensitive to outliers compared to the mean and allows for more stable tracking of typical model behavior.

**Linear graph** is used, as the median makes sense specifically in dynamics.

---

#### Metric: Number of predictions
(`positive_counter_total`)

The metric reflects the intensity of ML model usage and allows understanding if inference requests are arriving and at what rate.

**Linear graph** is used, as it is important to see the change in load on the model over time.

---

### Application Layer Metrics

#### Metric: Number of HTTP requests
(`http_requests_total`)

The metric is used to analyze total incoming traffic and estimate the load on the service API.

**Linear graph** is used, as it is necessary to track request frequency and possible load spikes.

---

#### Metric: Distribution of HTTP responses by status (2xx / 4xx)
(`http_requests_total` grouped by `status`)

The metric allows identifying request validation errors and problems with client interaction with the API.

**Bar chart** is used, as it clearly displays the structure of requests by response types.

---

#### Metric: Average HTTP response size
(`http_response_size_bytes_sum / http_response_size_bytes_count`)

The metric allows tracking changes in API response size, which may indicate serialization problems or response format changes.

**Stat panel with mini-graph** is used, as it is important to see the current value and its dynamics over a short period of time.

---

## Conclusion

The selected set of metrics allows for comprehensive control of:
- ML model behavior in real-time,
- correctness and stability of API operation,
- application process status and computing resource usage.

The use of various visualization types (Time series, Bar chart, Stat, Gauge) is conditioned by the nature of data and monitoring tasks, making the dashboard clear and convenient for analysis.
