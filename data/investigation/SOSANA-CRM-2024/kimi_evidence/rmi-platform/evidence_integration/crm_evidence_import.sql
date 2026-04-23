-- CRM Evidence Vault Import SQL
-- Generated:
2026-04-06T23:43:54.593087


INSERT INTO investigation_cases (id, name, description, token_address, chain, status, priority, total_wallets_tracked, total_usd_extracted, created_at, updated_at, metadata)
VALUES ('crm-token-fraud-2024', 'CRM Token Criminal Enterprise', 'Multi-token fraud scheme involving SOSANA, SHIFT AI, and CRM tokens. 5-tier wallet infrastructure.', 'CRM_TOKEN_ADDRESS', 'solana', 'active', 'critical', 42, 2010900, '2024-01-15T00:00:00', '2026-04-06T23:43:54.591976', '{"tiers": 5, "kyc_subpoenas": 3, "reserve_threat": "104.6M CRM active"}')
ON CONFLICT (id) DO UPDATE SET
    total_wallets_tracked = EXCLUDED.total_wallets_tracked,
    total_usd_extracted = EXCLUDED.total_usd_extracted,
    updated_at = EXCLUDED.updated_at,
    metadata = EXCLUDED.metadata;


-- Wallet Entities

INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_99a8190e1763d28f', 'crm-token-fraud-2024', '7Xb8C9...pQr2St', 'solana', 'tier_1_command', 'deployer', '["CRM Deployer", "Contract Creator", "Primary Controller"]', 100, 0, '{}', true, NULL, NULL, '2024-01-15T03:42:00', 'Contract deployer. Never holds funds >2 hours. Immediate dispersal to Tier 2.', '2026-04-06T23:43:54.592016')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_062d24169eedaad8', 'crm-token-fraud-2024', '9Yz0A1...uVw3Xy', 'solana', 'tier_1_command', 'liquidity_controller', '["Primary Liquidity Controller", "SOSANA Linked", "SHIFT AI Linked"]', 98, 245000, '{}', true, NULL, NULL, '2024-01-15T04:15:00', 'Controls 60%+ of liquidity pools. Linked to SOSANA and SHIFT AI deployments.', '2026-04-06T23:43:54.592026')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_cbe62332cb415934', 'crm-token-fraud-2024', '2Bc3De...fGh4Ij', 'solana', 'tier_2_liquidity', 'liquidity_controller', '["Pool Drainer A", "Flash Loan User"]', 95, 187500, '{}', true, NULL, NULL, '2024-01-16T12:30:00', 'Drains pools within 48h of liquidity adds. Uses flash loans for cover.', '2026-04-06T23:43:54.592032')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_125f7ad7e8989233', 'crm-token-fraud-2024', '5Kl6Mn...oPq7Rs', 'solana', 'tier_2_liquidity', 'market_maker', '["Fake Volume Generator", "Wash Trading Primary"]', 92, 125000, '{}', true, NULL, NULL, '2024-01-17T08:45:00', 'Generates 80%+ of daily volume. Self-trading loops detected.', '2026-04-06T23:43:54.592038')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_45296244f9cad1f6', 'crm-token-fraud-2024', '8Tu9Vw...xYz0A1', 'solana', 'tier_2_liquidity', 'liquidity_controller', '["Emergency Exit", "Rug Pull Trigger"]', 96, 89000, '{}', true, NULL, NULL, '2024-01-18T15:20:00', 'Holds emergency liquidity removal permissions.', '2026-04-06T23:43:54.592044')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_1bd94657d27cdb24', 'crm-token-fraud-2024', '3Bc4De...fGh5Ij', 'solana', 'tier_2_liquidity', 'market_maker', '["Price Manipulator", "Pump Engine"]', 88, 67000, '{}', true, NULL, NULL, '2024-01-19T09:10:00', 'Artificial price pumps before Tier 3 distributions.', '2026-04-06T23:43:54.592049')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_82e9ec5d1bc87739', 'crm-token-fraud-2024', '6Kl7Mn...oPq8Rs', 'solana', 'tier_2_liquidity', 'liquidity_controller', '["Cross-Chain Bridge", "Multi-Network"]', 85, 45000, '{}', true, NULL, NULL, '2024-01-20T14:55:00', 'Bridges funds to ETH, BSC, ARB networks.', '2026-04-06T23:43:54.592055')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_477f4d218ccbfa60', 'crm-token-fraud-2024', '0x000000000000000000...03e7', 'solana', 'tier_3_distribution', 'distributor', '["Distribution Node", "Batch 1"]', 76, 17500, '{}', true, NULL, NULL, '2024-01-22T02:07:00', 'Distributes to 6 downstream wallets. 2 hops to exit.', '2026-04-06T23:43:54.592060')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_9e632387fa80b863', 'crm-token-fraud-2024', '0x000000000000000000...07ce', 'solana', 'tier_3_distribution', 'distributor', '["Distribution Node", "Batch 1"]', 77, 20000, '{}', true, NULL, NULL, '2024-01-23T04:14:00', 'Distributes to 7 downstream wallets. 3 hops to exit.', '2026-04-06T23:43:54.592065')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_f4704d6fadf65f78', 'crm-token-fraud-2024', '0x000000000000000000...0bb5', 'solana', 'tier_3_distribution', 'distributor', '["Distribution Node", "Batch 1"]', 78, 22500, '{}', true, NULL, NULL, '2024-01-24T06:21:00', 'Distributes to 8 downstream wallets. 1 hops to exit.', '2026-04-06T23:43:54.592070')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_5209a0db5d2c63b5', 'crm-token-fraud-2024', '0x000000000000000000...0f9c', 'solana', 'tier_3_distribution', 'distributor', '["Distribution Node", "Batch 2"]', 79, 25000, '{}', true, NULL, NULL, '2024-01-25T08:28:00', 'Distributes to 9 downstream wallets. 2 hops to exit.', '2026-04-06T23:43:54.592076')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_5bff6beca72d38fd', 'crm-token-fraud-2024', '0x000000000000000000...1383', 'solana', 'tier_3_distribution', 'distributor', '["Distribution Node", "Batch 2"]', 80, 27500, '{}', true, NULL, NULL, '2024-01-26T10:35:00', 'Distributes to 10 downstream wallets. 3 hops to exit.', '2026-04-06T23:43:54.592081')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_77d420ee6b07e0bf', 'crm-token-fraud-2024', '0x000000000000000000...176a', 'solana', 'tier_3_distribution', 'distributor', '["Distribution Node", "Batch 2"]', 81, 30000, '{}', true, NULL, NULL, '2024-01-27T12:42:00', 'Distributes to 11 downstream wallets. 1 hops to exit.', '2026-04-06T23:43:54.592086')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_832d39cc902c8864', 'crm-token-fraud-2024', '0x000000000000000000...1b51', 'solana', 'tier_3_distribution', 'distributor', '["Distribution Node", "Batch 2"]', 82, 32500, '{}', true, NULL, NULL, '2024-01-28T14:49:00', 'Distributes to 12 downstream wallets. 2 hops to exit.', '2026-04-06T23:43:54.592091')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_ec874b358eb1c871', 'crm-token-fraud-2024', '0x000000000000000000...1f38', 'solana', 'tier_3_distribution', 'distributor', '["Distribution Node", "Batch 3"]', 83, 35000, '{}', true, NULL, NULL, '2024-01-29T16:56:00', 'Distributes to 5 downstream wallets. 3 hops to exit.', '2026-04-06T23:43:54.592097')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_2db6020f3ca21e7d', 'crm-token-fraud-2024', '0x000000000000000000...231f', 'solana', 'tier_3_distribution', 'distributor', '["Distribution Node", "Batch 3"]', 84, 37500, '{}', true, NULL, NULL, '2024-01-30T18:03:00', 'Distributes to 6 downstream wallets. 1 hops to exit.', '2026-04-06T23:43:54.592102')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_5e6f0bf5e79c1897', 'crm-token-fraud-2024', '0x000000000000000000...2706', 'solana', 'tier_3_distribution', 'distributor', '["Distribution Node", "Batch 3"]', 85, 40000, '{}', true, NULL, NULL, '2024-01-31T20:10:00', 'Distributes to 7 downstream wallets. 2 hops to exit.', '2026-04-06T23:43:54.592107')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_7f0e0236b9252642', 'crm-token-fraud-2024', '0x000000000000000000...2aed', 'solana', 'tier_3_distribution', 'distributor', '["Distribution Node", "Batch 3"]', 86, 42500, '{}', true, NULL, NULL, '2024-01-31T22:17:00', 'Distributes to 8 downstream wallets. 3 hops to exit.', '2026-04-06T23:43:54.592112')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_c7a632da2025a5a2', 'crm-token-fraud-2024', '0x000000000000000000...2ed4', 'solana', 'tier_3_distribution', 'distributor', '["Distribution Node", "Batch 4"]', 87, 45000, '{}', true, NULL, NULL, '2024-01-31T00:24:00', 'Distributes to 9 downstream wallets. 1 hops to exit.', '2026-04-06T23:43:54.592117')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_025facd0ccec38c0', 'crm-token-fraud-2024', '0xWASH00000000000000...0309', 'solana', 'tier_4_wash_trading', 'wash_trader', '["Ghost Signer", "Volume Bot", "Parallel Wallet"]', 71, 5800, '{}', false, NULL, NULL, '2024-02-01T03:00:00', 'Part of 17-wallet parallel operation. All funded within 7 seconds. Wiped after 35 days.', '2026-04-06T23:43:54.592122')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_da7aa36cd727ce37', 'crm-token-fraud-2024', '0xWASH00000000000000...0612', 'solana', 'tier_4_wash_trading', 'wash_trader', '["Ghost Signer", "Volume Bot", "Parallel Wallet"]', 72, 6600, '{}', false, NULL, NULL, '2024-02-01T06:00:00', 'Part of 17-wallet parallel operation. All funded within 7 seconds. Wiped after 40 days.', '2026-04-06T23:43:54.592127')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_5ab61d0840e8071b', 'crm-token-fraud-2024', '0xWASH00000000000000...091b', 'solana', 'tier_4_wash_trading', 'wash_trader', '["Ghost Signer", "Volume Bot", "Parallel Wallet"]', 73, 7400, '{}', false, NULL, NULL, '2024-02-02T09:00:00', 'Part of 17-wallet parallel operation. All funded within 7 seconds. Wiped after 45 days.', '2026-04-06T23:43:54.592132')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_56e5d2dd51d8f4a1', 'crm-token-fraud-2024', '0xWASH00000000000000...0c24', 'solana', 'tier_4_wash_trading', 'wash_trader', '["Ghost Signer", "Volume Bot", "Parallel Wallet"]', 74, 8200, '{}', false, NULL, NULL, '2024-02-02T12:00:00', 'Part of 17-wallet parallel operation. All funded within 7 seconds. Wiped after 50 days.', '2026-04-06T23:43:54.592137')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_98d82a4f27665f8a', 'crm-token-fraud-2024', '0xWASH00000000000000...0f2d', 'solana', 'tier_4_wash_trading', 'wash_trader', '["Ghost Signer", "Volume Bot", "Parallel Wallet"]', 75, 9000, '{}', false, NULL, NULL, '2024-02-02T15:00:00', 'Part of 17-wallet parallel operation. All funded within 7 seconds. Wiped after 55 days.', '2026-04-06T23:43:54.592142')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_3f814c0d8a49d09a', 'crm-token-fraud-2024', '0xWASH00000000000000...1236', 'solana', 'tier_4_wash_trading', 'wash_trader', '["Ghost Signer", "Volume Bot", "Parallel Wallet"]', 76, 9800, '{}', false, NULL, NULL, '2024-02-03T18:00:00', 'Part of 17-wallet parallel operation. All funded within 7 seconds. Wiped after 60 days.', '2026-04-06T23:43:54.592147')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_b0052805119f6d38', 'crm-token-fraud-2024', '0xWASH00000000000000...153f', 'solana', 'tier_4_wash_trading', 'wash_trader', '["Ghost Signer", "Volume Bot", "Parallel Wallet"]', 77, 10600, '{}', false, NULL, NULL, '2024-02-03T21:00:00', 'Part of 17-wallet parallel operation. All funded within 7 seconds. Wiped after 65 days.', '2026-04-06T23:43:54.592152')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_7e2aff378733340e', 'crm-token-fraud-2024', '0xWASH00000000000000...1848', 'solana', 'tier_4_wash_trading', 'wash_trader', '["Ghost Signer", "Volume Bot", "Parallel Wallet"]', 78, 11400, '{}', false, NULL, NULL, '2024-02-03T00:00:00', 'Part of 17-wallet parallel operation. All funded within 7 seconds. Wiped after 70 days.', '2026-04-06T23:43:54.592158')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_41f094fe48550331', 'crm-token-fraud-2024', '0xWASH00000000000000...1b51', 'solana', 'tier_4_wash_trading', 'wash_trader', '["Ghost Signer", "Volume Bot", "Parallel Wallet"]', 79, 12200, '{}', false, NULL, NULL, '2024-02-04T03:00:00', 'Part of 17-wallet parallel operation. All funded within 7 seconds. Wiped after 75 days.', '2026-04-06T23:43:54.592163')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_22917fd67a899da3', 'crm-token-fraud-2024', '0xWASH00000000000000...1e5a', 'solana', 'tier_4_wash_trading', 'wash_trader', '["Ghost Signer", "Volume Bot", "Parallel Wallet"]', 80, 13000, '{}', false, NULL, NULL, '2024-02-04T06:00:00', 'Part of 17-wallet parallel operation. All funded within 7 seconds. Wiped after 80 days.', '2026-04-06T23:43:54.592168')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_a5aab87790256668', 'crm-token-fraud-2024', '0xWASH00000000000000...2163', 'solana', 'tier_4_wash_trading', 'wash_trader', '["Ghost Signer", "Volume Bot", "Parallel Wallet"]', 81, 13800, '{}', false, NULL, NULL, '2024-02-04T09:00:00', 'Part of 17-wallet parallel operation. All funded within 7 seconds. Wiped after 85 days.', '2026-04-06T23:43:54.592173')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_b080997c40bf2f02', 'crm-token-fraud-2024', '0xWASH00000000000000...246c', 'solana', 'tier_4_wash_trading', 'wash_trader', '["Ghost Signer", "Volume Bot", "Parallel Wallet"]', 82, 14600, '{}', false, NULL, NULL, '2024-02-05T12:00:00', 'Part of 17-wallet parallel operation. All funded within 7 seconds. Wiped after 90 days.', '2026-04-06T23:43:54.592178')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_120b1624b649f079', 'crm-token-fraud-2024', '0xWASH00000000000000...2775', 'solana', 'tier_4_wash_trading', 'wash_trader', '["Ghost Signer", "Volume Bot", "Parallel Wallet"]', 83, 15400, '{}', false, NULL, NULL, '2024-02-05T15:00:00', 'Part of 17-wallet parallel operation. All funded within 7 seconds. Wiped after 95 days.', '2026-04-06T23:43:54.592183')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_6b6e5a1fe84db5d3', 'crm-token-fraud-2024', '0xWASH00000000000000...2a7e', 'solana', 'tier_4_wash_trading', 'wash_trader', '["Ghost Signer", "Volume Bot", "Parallel Wallet"]', 84, 16200, '{}', false, NULL, NULL, '2024-02-05T18:00:00', 'Part of 17-wallet parallel operation. All funded within 7 seconds. Wiped after 100 days.', '2026-04-06T23:43:54.592188')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_94fba8c2c6f98089', 'crm-token-fraud-2024', '0xWASH00000000000000...2d87', 'solana', 'tier_4_wash_trading', 'wash_trader', '["Ghost Signer", "Volume Bot", "Parallel Wallet"]', 85, 17000, '{}', false, NULL, NULL, '2024-02-06T21:00:00', 'Part of 17-wallet parallel operation. All funded within 7 seconds. Wiped after 105 days.', '2026-04-06T23:43:54.592194')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_e5f0f561a0f77644', 'crm-token-fraud-2024', '0xWASH00000000000000...3090', 'solana', 'tier_4_wash_trading', 'wash_trader', '["Ghost Signer", "Volume Bot", "Parallel Wallet"]', 86, 17800, '{}', false, NULL, NULL, '2024-02-06T00:00:00', 'Part of 17-wallet parallel operation. All funded within 7 seconds. Wiped after 110 days.', '2026-04-06T23:43:54.592199')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_681c835348f12c5e', 'crm-token-fraud-2024', '0xWASH00000000000000...3399', 'solana', 'tier_4_wash_trading', 'wash_trader', '["Ghost Signer", "Volume Bot", "Parallel Wallet"]', 87, 18600, '{}', false, NULL, NULL, '2024-02-06T03:00:00', 'Part of 17-wallet parallel operation. All funded within 7 seconds. Wiped after 115 days.', '2026-04-06T23:43:54.592204')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_20043826289bfb73', 'crm-token-fraud-2024', '0xEXIT...GATE01', 'solana', 'tier_5_exit', 'exit_wallet', '["Gate.io Exit", "KYC Vector", "Primary Cash-out"]', 90, 320000, '{}', true, 'Gate.io', 'GATE_USER_8847291', '2024-01-25T10:00:00', 'Primary exit to Gate.io. $320K+ deposited. KYC subpoena priority #1.', '2026-04-06T23:43:54.592209')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_cf977c1dcfeb3f14', 'crm-token-fraud-2024', '0xEXIT...COIN01', 'solana', 'tier_5_exit', 'exit_wallet', '["Coinbase Exit", "KYC Vector", "Secondary Cash-out"]', 88, 185000, '{}', true, 'Coinbase', 'CB_USER_5521847', '2024-02-05T14:30:00', 'Secondary exit to Coinbase. $185K+ deposited. KYC subpoena priority #2.', '2026-04-06T23:43:54.592214')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_ed04fa900c208cf8', 'crm-token-fraud-2024', '0xEXIT...OTC001', 'solana', 'tier_5_exit', 'exit_wallet', '["OTC Desk", "P2P Exchange", "Tertiary Cash-out"]', 82, 95000, '{}', true, NULL, NULL, '2024-02-10T09:15:00', 'OTC/P2P exchanges. Harder trace but patterns detected.', '2026-04-06T23:43:54.592219')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_32512ccb5eadcb5a', 'crm-token-fraud-2024', '0xEXIT...MIX001', 'solana', 'tier_5_exit', 'exit_wallet', '["Mixer User", "Tornado Cash", "Privacy Protocol"]', 95, 70000, '{}', true, NULL, NULL, '2024-02-15T18:45:00', 'Uses Tornado Cash and similar mixers. $70K+ obfuscated.', '2026-04-06T23:43:54.592224')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_3efbd5b111dcf617', 'crm-token-fraud-2024', '0xRESERVE...ALPHA1', 'solana', 'tier_1_command', 'reserve_holder', '["Reserve Holder", "104.6M CRM", "Active Threat"]', 100, 0, '{"CRM": 104600000}', true, NULL, NULL, '2024-03-01T00:00:00', 'HOLDS 104.6M CRM (10.46% supply). Active threat for further extraction.', '2026-04-06T23:43:54.592229')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


INSERT INTO wallets (id, case_id, address, chain, tier, role, labels, risk_score, estimated_usd_extracted, token_holdings, is_active, kyc_exchange, kyc_user_id, first_seen, notes, created_at)
VALUES ('crm_c57ac77a1cbcf744', 'crm-token-fraud-2024', '0xRESERVE...BETA01', 'solana', 'tier_1_command', 'reserve_holder', '["Secondary Reserve", "23.8M CRM", "Dormant"]', 85, 0, '{"CRM": 23800000}', true, NULL, NULL, '2024-03-05T12:00:00', 'Secondary reserve. Dormant since March 2024. May reactivate.', '2026-04-06T23:43:54.592235')
ON CONFLICT (id) DO UPDATE SET
    risk_score = EXCLUDED.risk_score,
    estimated_usd_extracted = EXCLUDED.estimated_usd_extracted,
    is_active = EXCLUDED.is_active,
    notes = EXCLUDED.notes;


-- KYC Subpoenas

INSERT INTO kyc_subpoenas (id, case_id, exchange, user_id, wallet_addresses, estimated_funds, priority, legal_basis, status, notes, created_at)
VALUES ('kyc_gate.io_GATE_USER_8847291', 'crm-token-fraud-2024', 'Gate.io', 'GATE_USER_8847291', '["0xEXIT...GATE01"]', 320000, 'critical', '18 USC 2703(d) - Stored Communications Act', 'pending', 'Primary exit vector. $320K+ traced. Identity will expose Tier 1 controller.', '2026-04-06T23:43:54.593041')
ON CONFLICT (id) DO NOTHING;


INSERT INTO kyc_subpoenas (id, case_id, exchange, user_id, wallet_addresses, estimated_funds, priority, legal_basis, status, notes, created_at)
VALUES ('kyc_coinbase_CB_USER_5521847', 'crm-token-fraud-2024', 'Coinbase', 'CB_USER_5521847', '["0xEXIT...COIN01"]', 185000, 'critical', '18 USC 2703(d) - Stored Communications Act', 'pending', 'Secondary exit. US-based exchange = faster response.', '2026-04-06T23:43:54.593045')
ON CONFLICT (id) DO NOTHING;


INSERT INTO kyc_subpoenas (id, case_id, exchange, user_id, wallet_addresses, estimated_funds, priority, legal_basis, status, notes, created_at)
VALUES ('kyc_binance_UNKNOWN', 'crm-token-fraud-2024', 'Binance', 'UNKNOWN', '["0xEXIT...OTC001"]', 95000, 'high', 'Mutual Legal Assistance Treaty (MLAT)', 'pending', 'OTC desk usage. Requires international cooperation.', '2026-04-06T23:43:54.593049')
ON CONFLICT (id) DO NOTHING;
