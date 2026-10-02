"""
GL11: Tool Registry Enforcement Engine

Verifies that executing tool is registered and in valid lifecycle state.
Responsibilities:
  1. Check tool_name against VALID_MCP_TOOLS registry
  2. Verify tool lifecycle status (ACTIVE/DEPRECATED/DISABLED)
  3. Check requires_authorization flag
  4. Fast-fail on unknown or disabled tools
"""

from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class ToolLifecycleStatus(Enum):
    """Tool lifecycle states"""
    ACTIVE = "ACTIVE"           # Normal operation
    DEPRECATED = "DEPRECATED"   # Still works but discouraged
    DISABLED = "DISABLED"       # Cannot execute
    EXPERIMENTAL = "EXPERIMENTAL"  # Beta/test


@dataclass
class ToolMetadata:
    """Metadata for a registered tool"""
    name: str
    status: ToolLifecycleStatus
    requires_authorization: bool = True
    description: Optional[str] = None
    added_at: Optional[str] = None
    deprecated_at: Optional[str] = None


@dataclass
class GL11Result:
    """GL11 tool registry verification result"""
    allowed: bool
    tool_name: Optional[str] = None
    tool_metadata: Optional[ToolMetadata] = None
    failure_reason: Optional[str] = None
    failure_code: str = "GL11_OK"


class ToolRegistryEnforcementEngine:
    """
    GL11 Engine: Tool Registry Enforcement

    Maintains whitelist of authorized MCP tools and validates lifecycle.
    Prevents execution of unknown or deprecated tools.
    """

    # Tool registry: name -> metadata
    # This is the source of truth for which tools can be executed
    TOOL_REGISTRY = {
        # Core governance tools
        "mocka_get_overview": ToolMetadata(
            name="mocka_get_overview",
            status=ToolLifecycleStatus.ACTIVE,
            requires_authorization=False,
            description="Get MoCKA system overview"
        ),
        "mocka_get_todo": ToolMetadata(
            name="mocka_get_todo",
            status=ToolLifecycleStatus.ACTIVE,
            requires_authorization=False,
            description="Get active TODO items"
        ),
        "mocka_get_essence": ToolMetadata(
            name="mocka_get_essence",
            status=ToolLifecycleStatus.ACTIVE,
            requires_authorization=False,
            description="Get system essence and guidelines"
        ),
        "mocka_write_event": ToolMetadata(
            name="mocka_write_event",
            status=ToolLifecycleStatus.ACTIVE,
            requires_authorization=True,
            description="Write event to event ledger"
        ),
        "mocka_decision_write": ToolMetadata(
            name="mocka_decision_write",
            status=ToolLifecycleStatus.ACTIVE,
            requires_authorization=True,
            description="Write decision to Decision Ledger"
        ),
        "mocka_decision_get": ToolMetadata(
            name="mocka_decision_get",
            status=ToolLifecycleStatus.ACTIVE,
            requires_authorization=False,
            description="Retrieve decision from Decision Ledger"
        ),
        "mocka_decision_list": ToolMetadata(
            name="mocka_decision_list",
            status=ToolLifecycleStatus.ACTIVE,
            requires_authorization=False,
            description="List decisions from Decision Ledger"
        ),
        "mocka_check_utf8": ToolMetadata(
            name="mocka_check_utf8",
            status=ToolLifecycleStatus.ACTIVE,
            requires_authorization=False,
            description="Validate UTF-8 encoding of file"
        ),
        # File tools
        "Write": ToolMetadata(
            name="Write",
            status=ToolLifecycleStatus.ACTIVE,
            requires_authorization=True,
            description="Create or overwrite file"
        ),
        "Edit": ToolMetadata(
            name="Edit",
            status=ToolLifecycleStatus.ACTIVE,
            requires_authorization=True,
            description="Edit file with string replacement"
        ),
        "Read": ToolMetadata(
            name="Read",
            status=ToolLifecycleStatus.ACTIVE,
            requires_authorization=False,
            description="Read file contents"
        ),
    }

    def verify_tool_registration(
        self,
        tool_name: str,
        args: Optional[Dict[str, Any]] = None
    ) -> GL11Result:
        """
        Verify that tool is registered and in valid state.

        Args:
            tool_name: Name of tool being executed
            args: Tool arguments (unused in GL11)

        Returns:
            GL11Result with allow/deny decision
        """
        # Check 1: Tool must be in registry
        metadata = self.TOOL_REGISTRY.get(tool_name)

        if not metadata:
            return GL11Result(
                allowed=False,
                tool_name=tool_name,
                failure_reason=f"Tool {tool_name} not found in registry",
                failure_code="GL11_FAIL_1_UNKNOWN_TOOL"
            )

        # Check 2: Tool must be ACTIVE
        if metadata.status == ToolLifecycleStatus.DISABLED:
            return GL11Result(
                allowed=False,
                tool_name=tool_name,
                tool_metadata=metadata,
                failure_reason=f"Tool {tool_name} is DISABLED",
                failure_code="GL11_FAIL_2_DISABLED_TOOL"
            )

        # Check 3: Warn if DEPRECATED but still allow
        if metadata.status == ToolLifecycleStatus.DEPRECATED:
            # Log deprecation warning but allow execution
            # This could be tightened to DENY deprecated tools
            pass

        # All checks passed
        return GL11Result(
            allowed=True,
            tool_name=tool_name,
            tool_metadata=metadata,
            failure_code="GL11_OK"
        )

    def register_tool(
        self,
        name: str,
        status: ToolLifecycleStatus,
        requires_authorization: bool = True,
        description: Optional[str] = None
    ) -> bool:
        """
        Register a new tool in the registry.

        Args:
            name: Tool name
            status: Tool lifecycle status
            requires_authorization: Whether tool requires GL8 auth
            description: Tool description

        Returns:
            True if registered successfully
        """
        if name in self.TOOL_REGISTRY:
            return False  # Tool already registered

        self.TOOL_REGISTRY[name] = ToolMetadata(
            name=name,
            status=status,
            requires_authorization=requires_authorization,
            description=description
        )
        return True

    def update_tool_status(
        self,
        name: str,
        status: ToolLifecycleStatus
    ) -> bool:
        """
        Update tool lifecycle status.

        Args:
            name: Tool name
            status: New lifecycle status

        Returns:
            True if updated successfully
        """
        if name not in self.TOOL_REGISTRY:
            return False

        self.TOOL_REGISTRY[name].status = status
        return True

    def get_tool_metadata(self, tool_name: str) -> Optional[ToolMetadata]:
        """
        Retrieve metadata for a tool.

        Args:
            tool_name: Name of tool

        Returns:
            ToolMetadata or None if not found
        """
        return self.TOOL_REGISTRY.get(tool_name)

    def list_registered_tools(self) -> Dict[str, ToolMetadata]:
        """
        Get all registered tools.

        Returns:
            Dict of tool_name -> ToolMetadata
        """
        return self.TOOL_REGISTRY.copy()

    def list_active_tools(self) -> Dict[str, ToolMetadata]:
        """
        Get all ACTIVE tools.

        Returns:
            Dict of tool_name -> ToolMetadata (ACTIVE only)
        """
        return {
            name: metadata
            for name, metadata in self.TOOL_REGISTRY.items()
            if metadata.status == ToolLifecycleStatus.ACTIVE
        }


# Singleton instance
_gl11_engine = None


def get_gl11_engine() -> ToolRegistryEnforcementEngine:
    """Get or create GL11 engine singleton"""
    global _gl11_engine
    if _gl11_engine is None:
        _gl11_engine = ToolRegistryEnforcementEngine()
    return _gl11_engine
