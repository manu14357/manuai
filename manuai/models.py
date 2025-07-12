import os
from typing import Any, Dict, List, Optional

import requests
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import (AIMessage, BaseMessage, HumanMessage,
                                     SystemMessage)
from langchain_core.outputs.llm_result import LLMResult
from langchain_ollama import ChatOllama

from manuai.config import ModelConfig, ModelProvider
from manuai.optimizations import TokenOptimizationPipeline


class OptimizedChatOllama(ChatOllama):
    """Optimized Ollama chat model with token and parameter optimization."""

    def __init__(
        self,
        model: str,
        temperature: float = 0.0,
        base_url: str = "http://localhost:11434",
        **kwargs,
    ):
        """Initialize optimized Ollama chat model.

        Args:
            model: Model ID to use
            temperature: Temperature parameter (0.0-1.0)
            base_url: Ollama server base URL
        """
        super().__init__(
            model=model,
            temperature=temperature,
            base_url=base_url,
            **kwargs,
        )

    def _call(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs,
    ) -> str:
        """Call the Ollama API with optimization.

        Args:
            messages: List of chat messages
            stop: Optional list of stop sequences
            run_manager: Optional callback manager

        Returns:
            Generated text response
        """
        # Create token optimizer when needed instead of storing as an instance attribute
        token_optimizer = TokenOptimizationPipeline()

        # Apply token optimization to the last user message if it exists
        optimized_messages = list(messages)
        for i in range(len(optimized_messages) - 1, -1, -1):
            if isinstance(optimized_messages[i], HumanMessage):
                original_content = optimized_messages[i].content
                optimized_content = token_optimizer.refine_query(original_content)
                optimized_messages[i] = HumanMessage(content=optimized_content)
                break

        # Prune conversation history if needed
        if len(optimized_messages) > 10:  # arbitrary threshold
            system_messages = [m for m in optimized_messages if isinstance(m, SystemMessage)]
            recent_messages = optimized_messages[-9:]  # Keep last 9 messages

            # Make sure we keep at least one system message if it exists
            if system_messages and not any(isinstance(m, SystemMessage) for m in recent_messages):
                optimized_messages = [system_messages[0]] + recent_messages
            else:
                optimized_messages = recent_messages

        # Call the parent implementation with optimized messages
        return super()._call(
            messages=optimized_messages, stop=stop, run_manager=run_manager, **kwargs
        )


def create_llm(model_config: ModelConfig) -> BaseChatModel:
    """Create a language model based on the model configuration.

    Args:
        model_config: Model configuration

    Returns:
        BaseChatModel: Configured language model
    """
    if model_config.provider == ModelProvider.OLLAMA:
        return OptimizedChatOllama(
            model=model_config.name,
            temperature=model_config.temperature,
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
    else:
        raise ValueError(f"Unsupported model provider: {model_config.provider}")
