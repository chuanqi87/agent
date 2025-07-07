from typing import Any, Dict, List, Optional, Union, Literal
from pydantic import BaseModel, Field
from enum import Enum
import time
import uuid

class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    FUNCTION = "function"
    TOOL = "tool"

class ToolType(str, Enum):
    FUNCTION = "function"

class FunctionDefinition(BaseModel):
    name: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None

class Tool(BaseModel):
    type: ToolType = ToolType.FUNCTION
    function: FunctionDefinition

class ToolCall(BaseModel):
    id: str
    type: ToolType = ToolType.FUNCTION
    function: Dict[str, Any]

class Message(BaseModel):
    role: Role
    content: Optional[str] = None
    name: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[Message]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    logit_bias: Optional[Dict[str, int]] = None
    user: Optional[str] = None
    tools: Optional[List[Tool]] = None
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None

class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: Optional[str] = None

class ChatCompletionResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:29]}")
    object: str = "chat.completion"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[Choice]
    usage: Usage

class Delta(BaseModel):
    role: Optional[Role] = None
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None

class StreamChoice(BaseModel):
    index: int
    delta: Delta
    finish_reason: Optional[str] = None

class ChatCompletionStreamResponse(BaseModel):
    id: str = Field(default_factory=lambda: f"chatcmpl-{uuid.uuid4().hex[:29]}")
    object: str = "chat.completion.chunk"
    created: int = Field(default_factory=lambda: int(time.time()))
    model: str
    choices: List[StreamChoice]

class ModelInfo(BaseModel):
    id: str
    object: str = "model"
    created: int = Field(default_factory=lambda: int(time.time()))
    owned_by: str = "langserve"

class ModelListResponse(BaseModel):
    object: str = "list"
    data: List[ModelInfo]

class ErrorResponse(BaseModel):
    error: Dict[str, Any]
    
class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str = "1.0.0"
    timestamp: int = Field(default_factory=lambda: int(time.time()))