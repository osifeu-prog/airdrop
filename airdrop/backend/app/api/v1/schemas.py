from decimal import Decimal
from pydantic import BaseModel, Field

class TelegramAuthIn(BaseModel):
    telegram_id: int = Field(..., description="Telegram user id (from WebApp initData user.id)")
    init_data: str = Field(..., description="Telegram WebApp initData string")

class UserInfoOut(BaseModel):
    id: int
    telegram_id: int
    role: str

class WalletBalanceOut(BaseModel):
    balance: Decimal

class AirdropRequestIn(BaseModel):
    amount: Decimal = Field(..., gt=0)

class AirdropOut(BaseModel):
    id: int
    user_id: int
    amount: Decimal
    status: str

class AirdropApproveIn(BaseModel):
    airdrop_id: int

class TokenPriceOut(BaseModel):
    price: Decimal
    max_airdrop_per_user: int

class TokenPriceSetIn(BaseModel):
    price: Decimal | None = None
    max_airdrop_per_user: int | None = None

class FeatureFlagSetIn(BaseModel):
    key: str
    enabled: bool
