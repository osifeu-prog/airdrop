# 🚀 Airdrop Project with TON Integration

A complete cryptocurrency airdrop system with Telegram bot and TON payment integration.

## Features
- 🤖 Telegram bot for user interaction
- 💰 TON payment integration
- 🎁 Airdrop request management
- 📊 User balance tracking
- 🚀 FastAPI backend

## Setup
1. Set environment variables:
   - `TELEGRAM_TOKEN`: Your bot token
   - `TON_WALLET_ADDRESS`: Your TON wallet
   - `AIRDROP_PRICE_ILS`: Price in Israeli Shekels

2. Deploy to Railway:
   - Connect your GitHub repository
   - Set environment variables
   - Deploy automatically

## API Endpoints
- `POST /api/v1/users/register` - Register user
- `POST /api/v1/airdrop/request` - Request airdrop
- `GET /api/v1/users/{id}/balance` - Get user balance
- `GET /health` - Health check
