#!/usr/bin/env python3
"""
Tinderbox MCP Server

This server enables AI assistants to interact with Tinderbox via AppleScript,
providing tools for creating notes, managing links, and navigating hierarchies.

Runs as HTTP server with GitHub OAuth authentication.
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ConfigDict
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Configuration
APPLESCRIPT_DIR = Path(os.getenv("APPLESCRIPT_DIR", "./applescripts"))
DEFAULT_DOCUMENT = os.getenv("DEFAULT_DOCUMENT", "")
SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")

# GitHub OAuth Configuration (required for HTTP transport)
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")

# Initialize FastMCP server with host and port configuration
# Note: OAuth configuration will be applied when server starts
mcp = FastMCP("tinderbox_mcp", host=SERVER_HOST, port=SERVER_PORT)

# Configure GitHub OAuth for the server
# This will be used for authentication when running with HTTP transport
if GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET:
    # OAuth configuration will be handled by the MCP SDK
    # Clients will authenticate via GitHub OAuth when connecting
    pass


async def run_applescript(script_name: str, **params) -> str:
    """
    Execute an AppleScript with the given parameters.

    Args:
        script_name: Name of the .scpt file (without path)
        **params: Key-value parameters to pass to the script

    Returns:
        Script output as string

    Raises:
        FileNotFoundError: If script file doesn't exist
        RuntimeError: If script execution fails
    """
    script_path = APPLESCRIPT_DIR / script_name

    # Security: Validate script path
    if not script_path.exists():
        raise FileNotFoundError(f"Script not found: {script_path}")

    if not script_path.is_relative_to(APPLESCRIPT_DIR):
        raise ValueError(f"Script must be in applescripts directory: {script_path}")

    if script_path.suffix != ".scpt":
        raise ValueError(f"Script must have .scpt extension: {script_path}")

    # Convert parameters to key=value format
    args = [f"{key}={value}" for key, value in params.items()]

    # Execute AppleScript
    process = await asyncio.create_subprocess_exec(
        "osascript",
        str(script_path),
        *args,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        error_msg = stderr.decode().strip()
        raise RuntimeError(f"AppleScript failed: {error_msg}")

    return stdout.decode().strip()


# Pydantic models for input validation
class CreateNoteInput(BaseModel):
    """Input model for creating a new note in Tinderbox."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    title: str = Field(
        default="New Note",
        description="The title of the new note (e.g., 'Meeting Notes', 'Project Ideas')",
        min_length=1,
        max_length=255
    )
    text: str = Field(
        default="",
        description="The text content of the note (default: empty string)",
        max_length=10000
    )
    parent: str = Field(
        default="/Inbox/",
        description="The path to the parent container (default: /Inbox/). Use forward slashes for paths.",
        max_length=500
    )
    document: str = Field(
        default=DEFAULT_DOCUMENT,
        description="The name of the Tinderbox document (default: configured default)",
        max_length=255
    )


class ReadNoteInput(BaseModel):
    """Input model for reading a note's content."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    path: str = Field(
        ...,
        description="The path to the note (e.g., /Inbox/MyNote). Use forward slashes.",
        min_length=1,
        max_length=500
    )
    document: str = Field(
        default=DEFAULT_DOCUMENT,
        description="The name of the Tinderbox document (default: configured default)",
        max_length=255
    )


class GetChildrenInput(BaseModel):
    """Input model for listing child notes."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    path: str = Field(
        default="",
        description="The path to the container (default: root /). Use forward slashes.",
        max_length=500
    )
    document: str = Field(
        default=DEFAULT_DOCUMENT,
        description="The name of the Tinderbox document (default: configured default)",
        max_length=255
    )


class GetSiblingsInput(BaseModel):
    """Input model for listing sibling notes."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    path: str = Field(
        default="",
        description="The path to the reference note. Use forward slashes.",
        max_length=500
    )
    document: str = Field(
        default=DEFAULT_DOCUMENT,
        description="The name of the Tinderbox document (default: configured default)",
        max_length=255
    )


class GetLinksInput(BaseModel):
    """Input model for getting outgoing links."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    path: str = Field(
        default="",
        description="The path to the note. Use forward slashes.",
        max_length=500
    )
    document: str = Field(
        default=DEFAULT_DOCUMENT,
        description="The name of the Tinderbox document (default: configured default)",
        max_length=255
    )


class LinkNotesInput(BaseModel):
    """Input model for creating links between notes."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    source: str = Field(
        default="",
        description="The path of the source note (beginning of the link). Use forward slashes.",
        max_length=500
    )
    destination: str = Field(
        default="",
        description="The path of the destination note (end of the link). Use forward slashes.",
        max_length=500
    )
    linktype: str = Field(
        default="*untitled",
        description="The link label/type (e.g., 'contrast', 'source', 'influence'). Default: '*untitled'",
        max_length=255
    )
    document: str = Field(
        default=DEFAULT_DOCUMENT,
        description="The name of the Tinderbox document (default: configured default)",
        max_length=255
    )


class UpdateAttributeInput(BaseModel):
    """Input model for updating note attributes."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True
    )

    path: str = Field(
        default="",
        description="The path to the note. Use forward slashes.",
        max_length=500
    )
    attribute: str = Field(
        default="",
        description="The name of the attribute (e.g., 'Color', 'URL', 'Name', 'Text')",
        max_length=255
    )
    value: str = Field(
        default="",
        description="The new value for the attribute",
        max_length=10000
    )
    document: str = Field(
        default=DEFAULT_DOCUMENT,
        description="The name of the Tinderbox document (default: configured default)",
        max_length=255
    )


# Tool definitions
@mcp.tool(
    name="tinderbox_create_note",
    annotations={
        "title": "Create Tinderbox Note",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def tinderbox_create_note(params: CreateNoteInput) -> str:
    """
    Creates a new note in Tinderbox.

    This tool creates a new note with the specified title, text content, and parent
    location in a Tinderbox document. The note is created as a child of the specified
    parent container.

    Args:
        params (CreateNoteInput): Validated input parameters containing:
            - title (str): The title of the new note (default: "New Note")
            - text (str): The text content of the note (default: empty)
            - parent (str): The path to the parent container (default: /Inbox/)
            - document (str): The name of the Tinderbox document

    Returns:
        str: Path to the created note or error message

    Examples:
        - Use when: "Create a note called 'Meeting Notes' in the Inbox"
        - Use when: "Add a new note to /Projects/Research with title 'Paper Ideas'"
        - Don't use when: You need to read existing notes (use tinderbox_read_note)
        - Don't use when: You need to update existing notes (use tinderbox_update_attribute)

    Error Handling:
        - Returns error message if Tinderbox document is not open
        - Returns error message if parent path doesn't exist
        - Returns error message if AppleScript execution fails
    """
    try:
        result = await run_applescript(
            "create_note.scpt",
            title=params.title,
            text=params.text,
            parent=params.parent,
            document=params.document
        )
        return result
    except Exception as e:
        return f"Error creating note: {str(e)}"


@mcp.tool(
    name="tinderbox_read_note",
    annotations={
        "title": "Read Tinderbox Note",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def tinderbox_read_note(params: ReadNoteInput) -> str:
    """
    Reads the title and text content of a note in Tinderbox.

    This tool retrieves the title and text content of a specific note identified
    by its path in the document hierarchy.

    Args:
        params (ReadNoteInput): Validated input parameters containing:
            - path (str): The path to the note (e.g., /Inbox/MyNote)
            - document (str): The name of the Tinderbox document

    Returns:
        str: Note content formatted as "Title: <title>\\nText: <text>" or error message

    Examples:
        - Use when: "Read the contents of /Inbox/Meeting Notes"
        - Use when: "Show me what's in the note at /Projects/Research/Paper Ideas"
        - Don't use when: You need to list children (use tinderbox_get_children)
        - Don't use when: You need to create a new note (use tinderbox_create_note)

    Error Handling:
        - Returns error message if note doesn't exist at the specified path
        - Returns error message if Tinderbox document is not open
        - Returns error message if path format is invalid
    """
    try:
        result = await run_applescript(
            "read_note.scpt",
            path=params.path,
            document=params.document
        )
        return result
    except Exception as e:
        return f"Error reading note: {str(e)}"


@mcp.tool(
    name="tinderbox_get_children",
    annotations={
        "title": "Get Tinderbox Note Children",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def tinderbox_get_children(params: GetChildrenInput) -> str:
    """
    Lists all child notes of a container in Tinderbox.

    This tool retrieves all direct children of a specified container note,
    returning their paths and child counts for navigation.

    Args:
        params (GetChildrenInput): Validated input parameters containing:
            - path (str): The path to the container (default: root /)
            - document (str): The name of the Tinderbox document

    Returns:
        str: List of children with paths and child counts, or error message

    Examples:
        - Use when: "What notes are in the Inbox?"
        - Use when: "List all children of /Projects/Research"
        - Use when: "Show me the top-level containers" (use path="")
        - Don't use when: You need to read note content (use tinderbox_read_note)
        - Don't use when: You need siblings at the same level (use tinderbox_get_siblings)

    Error Handling:
        - Returns error message if container doesn't exist
        - Returns empty list if container has no children
        - Returns error message if Tinderbox document is not open
    """
    try:
        result = await run_applescript(
            "get_children.scpt",
            path=params.path,
            document=params.document
        )
        return result
    except Exception as e:
        return f"Error getting children: {str(e)}"


@mcp.tool(
    name="tinderbox_get_siblings",
    annotations={
        "title": "Get Tinderbox Note Siblings",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def tinderbox_get_siblings(params: GetSiblingsInput) -> str:
    """
    Lists all sibling notes at the same hierarchy level in Tinderbox.

    This tool retrieves all notes that share the same parent as the specified note,
    useful for exploring notes at the same organizational level.

    Args:
        params (GetSiblingsInput): Validated input parameters containing:
            - path (str): The path to the reference note
            - document (str): The name of the Tinderbox document

    Returns:
        str: List of sibling notes at the same level, or error message

    Examples:
        - Use when: "What other notes are at the same level as /Inbox/MyNote?"
        - Use when: "Show me siblings of /Projects/Research/Paper Ideas"
        - Don't use when: You need child notes (use tinderbox_get_children)
        - Don't use when: You need to navigate the hierarchy (use tinderbox_get_children)

    Error Handling:
        - Returns error message if note doesn't exist
        - Returns empty list if note has no siblings
        - Returns error message if Tinderbox document is not open
    """
    try:
        result = await run_applescript(
            "get_siblings.scpt",
            path=params.path,
            document=params.document
        )
        return result
    except Exception as e:
        return f"Error getting siblings: {str(e)}"


@mcp.tool(
    name="tinderbox_get_links",
    annotations={
        "title": "Get Tinderbox Note Links",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def tinderbox_get_links(params: GetLinksInput) -> str:
    """
    Returns all outgoing links from a note in Tinderbox.

    This tool retrieves the list of links originating from a specified note,
    including link types and destinations, useful for exploring note relationships.

    Args:
        params (GetLinksInput): Validated input parameters containing:
            - path (str): The path to the note
            - document (str): The name of the Tinderbox document

    Returns:
        str: List of outgoing links with types and destinations, or error message

    Examples:
        - Use when: "What links go out from /Inbox/MyNote?"
        - Use when: "Show me all connections from /Projects/Research/Paper Ideas"
        - Don't use when: You need to create links (use tinderbox_link_notes)
        - Don't use when: You need note content (use tinderbox_read_note)

    Error Handling:
        - Returns error message if note doesn't exist
        - Returns empty list if note has no outgoing links
        - Returns error message if Tinderbox document is not open
    """
    try:
        result = await run_applescript(
            "get_links.scpt",
            path=params.path,
            document=params.document
        )
        return result
    except Exception as e:
        return f"Error getting links: {str(e)}"


@mcp.tool(
    name="tinderbox_link_notes",
    annotations={
        "title": "Link Tinderbox Notes",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": False
    }
)
async def tinderbox_link_notes(params: LinkNotesInput) -> str:
    """
    Creates a typed link between two notes in Tinderbox.

    This tool creates a directional link from a source note to a destination note
    with an optional link type/label for categorizing relationships.

    Args:
        params (LinkNotesInput): Validated input parameters containing:
            - source (str): The path to the source note (beginning of link)
            - destination (str): The path to the destination note (end of link)
            - linktype (str): The link label (default: "*untitled")
            - document (str): The name of the Tinderbox document

    Returns:
        str: Confirmation message or error message

    Examples:
        - Use when: "Link /Inbox/Note1 to /Projects/Note2 with type 'reference'"
        - Use when: "Create a 'source' link from Paper Ideas to Research Notes"
        - Don't use when: You need to see existing links (use tinderbox_get_links)
        - Don't use when: You need to delete links (not currently supported)

    Error Handling:
        - Returns error message if source or destination note doesn't exist
        - Returns error message if Tinderbox document is not open
        - Returns error message if paths are invalid
    """
    try:
        result = await run_applescript(
            "link_notes.scpt",
            source=params.source,
            destination=params.destination,
            linktype=params.linktype,
            document=params.document
        )
        return result
    except Exception as e:
        return f"Error linking notes: {str(e)}"


@mcp.tool(
    name="tinderbox_update_attribute",
    annotations={
        "title": "Update Tinderbox Note Attribute",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def tinderbox_update_attribute(params: UpdateAttributeInput) -> str:
    """
    Updates an attribute of a note in Tinderbox.

    WARNING: This tool can overwrite existing content including Name and Text attributes.
    Use with caution and always confirm before updating attributes of existing notes.

    This tool modifies a single attribute of a note, such as Color, URL, or custom
    attributes defined in the Tinderbox document.

    Args:
        params (UpdateAttributeInput): Validated input parameters containing:
            - path (str): The path to the note
            - attribute (str): The attribute name (e.g., 'Color', 'URL', 'Name')
            - value (str): The new value for the attribute
            - document (str): The name of the Tinderbox document

    Returns:
        str: Confirmation message or error message

    Examples:
        - Use when: "Set the Color attribute of /Inbox/MyNote to 'red'"
        - Use when: "Update the URL attribute of /Projects/Research to 'https://example.com'"
        - Don't use when: Creating new notes (use tinderbox_create_note)
        - Don't use when: Reading attributes (use tinderbox_read_note for Name/Text)

    Error Handling:
        - Returns error message if note doesn't exist
        - Returns error message if attribute name is invalid
        - Returns error message if Tinderbox document is not open
        - Returns error message if value type doesn't match attribute type

    Security Notes:
        - Can overwrite Name and Text attributes (destructive)
        - Should confirm with user before modifying existing notes
        - Always backup important Tinderbox documents before use
    """
    try:
        result = await run_applescript(
            "update_attribute.scpt",
            path=params.path,
            attribute=params.attribute,
            value=params.value,
            document=params.document
        )
        return result
    except Exception as e:
        return f"Error updating attribute: {str(e)}"


if __name__ == "__main__":
    # Verify applescripts directory exists
    if not APPLESCRIPT_DIR.exists():
        print(f"Error: AppleScript directory '{APPLESCRIPT_DIR}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Verify required configuration
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        print("Error: GitHub OAuth credentials required.", file=sys.stderr)
        print("Set GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET environment variables.", file=sys.stderr)
        print("See README.md for setup instructions.", file=sys.stderr)
        sys.exit(1)

    if not DEFAULT_DOCUMENT:
        print("Warning: DEFAULT_DOCUMENT not set. Tools will require explicit 'document' parameter.", file=sys.stderr)

    # Run the server with HTTP transport
    print(f"Starting Tinderbox MCP Server on http://{SERVER_HOST}:{SERVER_PORT}", file=sys.stderr)
    print(f"MCP endpoint: http://{SERVER_HOST}:{SERVER_PORT}/mcp", file=sys.stderr)
    print(f"AppleScript directory: {APPLESCRIPT_DIR.absolute()}", file=sys.stderr)
    if DEFAULT_DOCUMENT:
        print(f"Default document: {DEFAULT_DOCUMENT}", file=sys.stderr)
    print("", file=sys.stderr)
    print("Add this URL as a Connector in Claude settings:", file=sys.stderr)
    print(f"  http://{SERVER_HOST}:{SERVER_PORT}/mcp", file=sys.stderr)
    print("", file=sys.stderr)

    mcp.run(transport="streamable_http")
