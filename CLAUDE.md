# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Tinderbox MCP Server is a Model Context Protocol (MCP) server that enables AI assistants to interact with Tinderbox, a macOS knowledge management application. The server uses AppleScript to control Tinderbox documents, allowing AI assistants to create notes, link them, update attributes, and navigate document hierarchies via natural language.

## Build and Development Commands

```bash
# Install dependencies
npm install

# Build the TypeScript project
npm run build

# Run the server (requires built files)
npm run start

# Run with custom AppleScript directory
node build/index.js /path/to/applescripts
```

The build output goes to the `build/` directory. The server accepts one optional argument: the path to the AppleScript files (defaults to `./applescripts`).

## Architecture

### Core Components

**src/index.ts** - Single-file architecture containing:
- **MCP Server Setup**: Creates an MCP server using `@modelcontextprotocol/sdk`
- **Script Registry** (`scriptConfigs`): Maps tool names to their configurations, including descriptions and Zod parameter schemas
- **Script Execution Pipeline**: Uses Node's `child_process.execFile` to call `osascript` with compiled AppleScript files
- **Security Validation** (`validateScriptPath`): Ensures scripts are within the allowed directory and have `.scpt` extension

### AppleScript Integration

The server bridges MCP tools to AppleScript via a registration system:
1. Each entry in `scriptConfigs` defines a tool with its parameters and defaults
2. The `registerScriptTools()` function dynamically registers each configured script as an MCP tool
3. When a tool is called, parameters are validated with Zod schemas (applying defaults), then converted to `key=value` format
4. The corresponding `.scpt` file in `applescripts/` is executed via `osascript`

**Available AppleScript Tools**:
- `create_note` - Creates notes with title, text, parent path
- `read_note` - Retrieves note title and text
- `get_children` - Lists child notes with paths and ChildCount
- `get_siblings` - Lists sibling notes at the same hierarchy level
- `get_links` - Returns outgoing links from a note
- `link_notes` - Creates typed links between notes
- `update_attribute` - Modifies note attributes (WARNING: can overwrite existing content including Name and Text)

All tools require a `document` parameter (defaults to "Playground"). Note paths use forward slashes (e.g., `/Inbox/MyNote`).

### Parameter Handling

Parameters flow through this pipeline:
1. Defined in `scriptConfigs` with Zod schemas and `.default()` values
2. Runtime values are parsed/validated by Zod (missing parameters get defaults)
3. Converted to `key=value` strings and passed as arguments to `osascript`
4. AppleScript files read these via the special variable system

Example from src/index.ts:141-151:
```typescript
const paramsSchema = z.object(Object.fromEntries(Object.entries(config.parameters)));
const validatedParams = paramsSchema.parse(params);
const args = Object.entries(validatedParams).map(([key, value]) => `${key}=${value}`);
```

## Adding New Tools

To extend the server with new Tinderbox operations:

1. Create a new `.scpt` file in `applescripts/` (can edit while server runs, but new files require restart)
2. Add a configuration entry to the `scriptConfigs` object in src/index.ts:24-81
3. Rebuild with `npm run build`
4. Restart the MCP client (e.g., Claude Desktop)

The script configuration must include:
- `description`: String describing what the tool does
- `parameters`: Object mapping parameter names to Zod schemas with `.describe()` and optional `.default()`

## Configuration for Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "tinderbox-mcp": {
      "command": "node",
      "args": ["/absolute/path/to/tinderbox-mcp/build/index.js", "/absolute/path/to/applescripts"]
    }
  }
}
```

Both paths must be absolute. The second argument (applescripts directory) is optional and defaults to `./applescripts` relative to where the server runs.

## Security Considerations

- **Path Validation**: src/index.ts:90-111 ensures scripts cannot escape the configured directory
- **Script Extension Check**: Only `.scpt` files can be executed
- **Destructive Tool**: `update_attribute` can overwrite note content. Consider removing it from `scriptConfigs` or modifying the AppleScript to restrict which attributes can be changed
- **Backup Reminder**: Always keep backups of Tinderbox documents as the server can modify existing notes

## Default Document

The default Tinderbox document name is "Playground" (hardcoded in the `.default("Playground")` values). Change this in src/index.ts:31, 38, 45, 52, 59, 68, 77 if working with different documents.
