# LocoBike Scalable Backend Architecture (Bonus Question)
## Requirement
Scale the bike ride service to **50,000 bikes** and **500,000 users** across a smart-mobility platform, support ride start/end, pricing, and smart lock communication. Design component boundaries, data flow, and handle at least two failure scenarios.

---

## Core Design Principles
- **Microservices Architecture**: Split monolithic service into independent microservices (single responsibility)
- **Asynchronous Communication**: Use message queue for smart lock/bike interaction (high concurrency)
- **Distributed Storage**: Separate relational database (transactional data) and cache (hot data)
- **Fault Tolerance**: Circuit breaker, retry, fallback for critical services
- **Scalability**: Stateless services for horizontal scaling, sharded data for large datasets

---

## 1. Component Boundaries (Microservices)
All services are **stateless** (supports horizontal scaling) and deployed on Kubernetes for orchestration.

### a. API Gateway
- **Responsibility**: Request routing, load balancing, authentication/authorization, rate limiting, API versioning.
- **Tool**: Nginx / Cloudflare / AWS API Gateway.
- **Key**: Single entry point for all client requests, shields microservices from direct external access.

### b. Ride Service (Core)
- **Responsibility**: Ride start/end, ride detail retrieval, ride state management, smart lock event sync.
- **Key**: Handles ride transaction logic, interacts with Lock Communication Service and Pricing Service.

### c. Pricing Service
- **Responsibility**: Real-time ride cost calculation, pricing rule management (dynamic update), daily cap enforcement, billing data generation.
- **Key**: Stateless, can be updated independently without affecting other services (e.g., adjust pricing rules).

### d. User Service
- **Responsibility**: User authentication, user profile management, user balance/wallet, ride history query.
- **Key**: Integrates with payment gateways for fare deduction, provides user-level access control.

### e. Lock Communication Service
- **Responsibility**: Asynchronous communication with smart bike locks, lock state sync (unlock/lock), bike status monitoring (battery, location).
- **Key**: Consumes Kafka messages from smart locks, converts device-level events to ride service events (e.g., lock unlock → ride start).

### f. Data Storage Layer
- **PostgreSQL Cluster**: Master-slave replication for read-write separation, **sharded by ride ID/user ID** (avoid single database bottleneck). Stores transactional data (ride records, user data, pricing rules).
- **Redis Cluster**: Caches hot ride data (e.g., active rides), distributed lock (prevent duplicate ride start/end), rate limiting, session storage. TTL for inactive ride data (reduce memory usage).
- **Data Warehouse**: Stores historical ride data for analytics, billing, and business intelligence (e.g., ride frequency, peak hours).

### g. Message Queue (Kafka)
- **Responsibility**: Asynchronous communication between smart locks and backend services, decouples device layer from application layer.
- **Topics**: `lock_unlock`, `lock_lock`, `bike_status`, `ride_event`.
- **Key**: Buffers high concurrency events from 50k smart locks, avoids backend service overload.

### h. Monitoring/Logging
- **Prometheus + Grafana**: Real-time monitoring of service health, performance metrics (QPS, latency), bike lock online status, database load.
- **ELK Stack (Elasticsearch + Logstash + Kibana)**: Centralized logging, distributed tracing, error alerting.

---

## 2. Data Flow (Key Scenarios)
### Scenario 1: User Starts a Ride (App → Bike → Backend)
1. User clicks "Start Ride" on the app → Request sent to API Gateway → Authenticated by User Service.
2. API Gateway routes request to Ride Service → Ride Service creates a ride record in PostgreSQL, caches it in Redis (active ride).
3. Ride Service sends an **unlock command** to Kafka `lock_unlock` topic.
4. Lock Communication Service consumes the message → Sends MQTT/HTTP request to the target smart bike lock.
5. Smart lock unlocks → Sends a **lock unlocked** confirmation to Kafka → Lock Communication Service syncs the state to Ride Service.
6. Ride Service updates the ride state to "active" in PostgreSQL/Redis → Returns success to the user app.

### Scenario 2: User Ends a Ride (App → Bike → Backend → Pricing)
1. User clicks "End Ride" on the app → Request sent to API Gateway → Route to Ride Service.
2. Ride Service sends a **lock command** to Kafka → Smart lock locks → Sends confirmation to Kafka.
3. Ride Service updates ride state to "completed", records end time in PostgreSQL/Redis.
4. Ride Service calls Pricing Service **synchronously** to calculate the ride fare.
5. Pricing Service retrieves ride duration from Redis/PostgreSQL, calculates cost per pricing rules, applies daily cap → Returns cost detail to Ride Service.
6. Ride Service stores total cost in PostgreSQL, generates billing data → Sends to Data Warehouse for billing.
7. Ride Service returns ride detail + total cost to the user app.

---

## 3. Failure Scenario Handling (At Least Two)
### Scenario 1: Smart Lock Communication Failure (No Unlock/Lock Confirmation)
**Problem**: Backend sends an unlock command to a smart lock, but no confirmation is received (e.g., bike is offline, network failure, lock malfunctions).
**Solutions**:
1. **Asynchronous Retry with Exponential Backoff**: Lock Communication Service retries the unlock command 3 times with exponential backoff (1s → 2s → 4s) – avoids overwhelming the lock/network.
2. **Distributed Lock in Redis**: Ride Service sets a distributed lock on the ride ID (TTL 30s) to prevent duplicate unlock requests.
3. **Fallback & State Reconciliation**: If retries fail, Ride Service marks the ride state as "pending" and sends a push notification to the user (e.g., "Bike offline, please try again"). A **scheduled reconciliation job** checks pending rides every minute and syncs lock state with the bike (when online).
4. **Monitoring & Alerting**: Prometheus triggers an alert if the lock communication failure rate exceeds 1% – engineers can investigate the bike/network issue in real time.

### Scenario 2: Ride Service Node Crashes (High Concurrency)
**Problem**: A Ride Service node crashes due to high concurrency (e.g., peak hour, 10k+ ride requests per second) – partial user requests fail.
**Solutions**:
1. **Stateless Service + Horizontal Scaling**: All Ride Service nodes are stateless – Kubernetes automatically reschedules the crashed node and scales out additional nodes to handle load.
2. **API Gateway Load Balancing**: API Gateway routes requests to healthy Ride Service nodes only – no requests are sent to the crashed node.
3. **Database Transaction Atomicity**: All ride record operations (create/update) use PostgreSQL **ACID transactions** – no partial ride records are created (e.g., ride start without lock unlock).
4. **Redis Cache Consistency**: A **cache invalidation job** runs every 10s to sync active ride data between Redis and PostgreSQL – ensures cache consistency after node crash.
5. **Circuit Breaker**: Use Resilience4j to implement a circuit breaker between API Gateway and Ride Service – if the failure rate exceeds 50%, the circuit breaker opens (rejects requests temporarily) and retries after a timeout – avoids cascading failure to other services.

### Bonus Failure Scenario: PostgreSQL Master Node Down
**Problem**: PostgreSQL master node (write) crashes – no new ride records can be created.
**Solutions**:
1. **Master-Slave Automatic Failover**: Use Patroni to manage PostgreSQL cluster – automatic failover to a slave node (promoted to master) in <30s – minimal downtime.
2. **Read-Write Separation**: All read requests (e.g., get ride detail) are routed to slave nodes – read operations continue even if master is down.
3. **Data Sharding**: PostgreSQL is sharded by user ID – a single shard failure only affects a subset of users (not the entire system).

---

## 4. Additional Scalability Optimizations
1. **Bike Geo-Sharding**: Smart bike locks are sharded by geographic region (e.g., city/zone) – Lock Communication Service only consumes messages from its assigned region (reduces message processing load).
2. **Pricing Rule Caching**: Pricing rules (unlock fee, daily cap) are cached in Redis – Pricing Service does not need to query PostgreSQL for every cost calculation (reduces database load).
3. **Active Ride TTL**: Active ride data in Redis has a TTL of 24 hours – inactive ride data is automatically evicted (reduces Redis memory usage).
4. **Bulk Processing**: Billing data is sent to the Data Warehouse in bulk (every 5 minutes) – avoids frequent small writes to the data warehouse.

