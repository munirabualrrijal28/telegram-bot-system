
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os

# =============================================================================
# IMPORTANT: Models have been reorganized!
# =============================================================================
# Most models have been moved to specialized apps:
# - core: UUIDModel, Pharmacy, SystemAdmin, TelegramUser, AuditLog, Subscription, Attachment
# - ecom: Category, Medicine, PriceHistory, InventoryTransaction, Order, OrderItem
# - ai_service: AIModel, AIPromptTemplate, AIDocument, AIEmbedding, AIRequest, AIResponse, AIModeration
# - bot_app: BotConfig, BotLog, ChatSession, ChatMessage, MediaFile
#
# To import these models, use:
#   from core.models import Pharmacy, TelegramUser
#   from ecom.models import Medicine, Category
#   from ai_service.models import AIModel
#   from bot_app.models import BotSettings (formerly BotConfig)
# =============================================================================

