# Marketplace API Endpoints

## Services (Subscriptions)
- **GET** `/services` - Get service catalog
  - Query params: `category`, `featured`, `search`
  - Response: `{ services: [], total: number, categories: [] }`

- **GET** `/services/{service_key}` - Get service details
  - Returns: Service details with pricing

- **POST** `/services/{service_key}/purchase` - Purchase service
  - Body: `{ billing_cycle: "monthly" | "yearly" }`
  - Returns: `{ success, subscription_id, credits_spent, expires_at, ... }`

- **GET** `/services/user/active` - Get user's subscriptions
  - Query params: `include_expired`
  - Returns: `{ subscriptions: [], total, active_count }`

## Marketplace Items (One-time purchases)
- **GET** `/marketplace/items` - Get marketplace items
  - Query params: `category`, `is_featured`, `is_premium`, `search`
  - Response: `{ items: [] }`

- **POST** `/marketplace/purchase` - Purchase item
  - Body: `{ item_id: number }`
  - Returns: Purchase confirmation

- **GET** `/marketplace/purchases` - Get user's purchases
  - Returns: `{ purchases: [{ item_id }] }`

## Credits
- **GET** `/credits/balance` - Get user credit balance
  - Returns: `{ balance: number }`
