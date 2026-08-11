# ai_service/models.py
"""
AI/ML service models: Configuration, knowledge base, and logging.
"""

from django.db import models

# Import from core app
from core.models import UUIDModel, Workspace, TelegramUser


# ============================================================================
# AI CONFIGURATION
# ============================================================================

class AIModel(UUIDModel):
    """AI model configuration"""
    workspace = models.ForeignKey(
        Workspace, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL, 
        related_name='ai_models'
    )
    name = models.CharField(max_length=200)
    provider = models.CharField(max_length=100)  # e.g. OpenAI, Qwen, Ollama
    model_id = models.CharField(max_length=200)  # model reference
    config = models.JSONField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_model"
        indexes = [
            models.Index(fields=['name'], name='idx_aimodel_name'),
            models.Index(fields=['provider'], name='idx_aimodel_provider'),
        ]


class AIPromptTemplate(UUIDModel):
    """Reusable prompt templates"""
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='prompt_templates')
    name = models.CharField(max_length=200)
    template = models.TextField()
    description = models.TextField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_prompt_template"
        indexes = [
            models.Index(fields=['workspace'], name='idx_prompt_workspace'),
            models.Index(fields=['is_active'], name='idx_prompt_active'),
        ]


# ============================================================================
# KNOWLEDGE BASE
# ============================================================================

class AIDocument(UUIDModel):
    """Document knowledge base"""
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE)
    title = models.CharField(max_length=500, null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    source = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_document"
        indexes = [
            models.Index(fields=['workspace'], name='idx_aidoc_workspace'),
        ]


class AIEmbedding(UUIDModel):
    """Vector embeddings storage"""
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='embeddings')
    chunk = models.TextField()
    vector = models.JSONField()  # store embedding array
    source_type = models.CharField(max_length=50, null=True, blank=True)
    source_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_embedding"
        indexes = [
            models.Index(fields=['workspace'], name='idx_aiembedding_workspace'),
            models.Index(fields=['source_type'], name='idx_aiembedding_source_type'),
        ]


# ============================================================================
# AI REQUEST/RESPONSE LOGGING
# ============================================================================

class AIRequest(UUIDModel):
    """AI request logging"""
    workspace = models.ForeignKey(Workspace, null=True, blank=True, on_delete=models.SET_NULL)
    model = models.ForeignKey(AIModel, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(TelegramUser, null=True, blank=True, on_delete=models.SET_NULL)
    prompt = models.TextField(null=True, blank=True)
    prompt_tokens = models.IntegerField(null=True, blank=True)
    completion_tokens = models.IntegerField(null=True, blank=True)
    total_cost = models.DecimalField(max_digits=12, decimal_places=6, null=True, blank=True)
    latency_ms = models.IntegerField(null=True, blank=True)
    response_preview = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_request"
        indexes = [
            models.Index(fields=['workspace', 'created_at'], name='idx_aireq_workspace_created'),
        ]


class AIResponse(UUIDModel):
    """AI response storage"""
    workspace = models.ForeignKey(Workspace, on_delete=models.CASCADE, related_name='ai_responses')
    user_message = models.CharField(max_length=500)
    ai_answer = models.TextField()
    source_model = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "ai_response"
        indexes = [
            models.Index(fields=['workspace'], name='idx_airesponse_workspace'),
            models.Index(fields=['source_model'], name='idx_airesponse_source'),
        ]


class AIModeration(UUIDModel):
    """AI content moderation logging"""
    ai_response = models.ForeignKey(AIResponse, on_delete=models.CASCADE, related_name='moderations')
    violations = models.JSONField(null=True, blank=True)
    category = models.CharField(max_length=200, null=True, blank=True)
    action_taken = models.CharField(max_length=200, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ai_moderation"
        indexes = [
            models.Index(fields=['ai_response'], name='idx_aimod_response'),
        ]
