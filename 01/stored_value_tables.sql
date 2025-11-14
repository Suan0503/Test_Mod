-- Stored Value Wallet Schema (for DBeaver)
CREATE TABLE IF NOT EXISTS stored_value_wallet (
  id SERIAL PRIMARY KEY,
  whitelist_id INTEGER,
  phone VARCHAR(20),
  balance INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_wallet_phone ON stored_value_wallet(phone);
CREATE INDEX IF NOT EXISTS idx_wallet_wl ON stored_value_wallet(whitelist_id);

CREATE TABLE IF NOT EXISTS stored_value_txn (
  id SERIAL PRIMARY KEY,
  wallet_id INTEGER NOT NULL,
  type VARCHAR(20) NOT NULL,
  amount INTEGER NOT NULL,
  remark TEXT,
  coupon_500_count INTEGER NOT NULL DEFAULT 0,
  coupon_300_count INTEGER NOT NULL DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_txn_wallet ON stored_value_txn(wallet_id);
