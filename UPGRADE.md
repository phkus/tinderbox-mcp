# Upgrading from v0.1.x (TypeScript) to v0.2.x (Python)

This guide will help you migrate from the TypeScript version to the new Python version of Tinderbox MCP Server.

## What Changed in v0.2.0

### Major Changes
- **Language**: TypeScript → Python 3.10+
- **SDK**: Custom TypeScript implementation → Official MCP Python SDK with FastMCP
- **Transport**: Stdio only → Stdio (default) + HTTP/SSE (optional)
- **Configuration**: Command-line args → Environment variables

### What Stayed the Same
- **Tool functionality**: All tools work identically
- **AppleScript files**: No changes to `.scpt` files
- **Tool parameters**: Same parameter names and defaults
- **Claude Desktop compatibility**: Still works seamlessly

## Why Migrate?

1. **Official SDK**: Uses Anthropic's official Python SDK with ongoing support
2. **Simpler codebase**: Decorator-based tool registration is more maintainable
3. **Better extensibility**: Easier to add new tools and features
4. **Future-ready**: HTTP transport available for remote access scenarios
5. **Active ecosystem**: Benefits from MCP Python SDK improvements

## Should I Migrate?

### Migrate if:
- ✅ You want the latest features and improvements
- ✅ You're comfortable with Python or want to learn it
- ✅ You want easier customization and extension
- ✅ You want official MCP SDK support

### Stay on TypeScript if:
- ⏸️ Your current setup works perfectly and you don't need new features
- ⏸️ You have extensive TypeScript customizations
- ⏸️ You strongly prefer TypeScript over Python

**Note**: The TypeScript version remains available on the [`typescript`](https://github.com/phkus/tinderbox-mcp/tree/typescript) branch and will continue to work.

## Migration Steps

### Step 1: Backup Your Configuration

Save your current Claude Desktop configuration:

```bash
# Backup your config
cp ~/Library/Application\ Support/Claude/claude_desktop_config.json \
   ~/Library/Application\ Support/Claude/claude_desktop_config.json.backup
```

### Step 2: Install Python Dependencies

If you haven't already, make sure you have Python 3.10+ installed:

```bash
python3 --version  # Should be 3.10 or higher
```

Navigate to your tinderbox-mcp directory and install dependencies:

```bash
cd /path/to/tinderbox-mcp
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 3: Remove Old Configuration and Start Server

The Python version uses HTTP transport with Connectors instead of the stdio configuration in `claude_desktop_config.json`.

#### Old Configuration (TypeScript - stdio)
```json
{
  "mcpServers": {
    "tinderbox-mcp": {
      "command": "node",
      "args": [
        "/absolute/path/to/tinderbox-mcp/build/index.js",
        "/absolute/path/to/applescripts"
      ]
    }
  }
}
```

You can **remove this entire section** from your `claude_desktop_config.json` file, as the Python version doesn't use it.

#### New Configuration (Python - HTTP Connector)

The Python version runs as a separate HTTP server that you connect to via Connectors:

1. **Start the server** in a terminal:
   ```bash
   cd /path/to/tinderbox-mcp
   source venv/bin/activate
   python src/server.py
   ```

2. **Add as Connector** in Claude Desktop:
   - Open Claude Desktop settings
   - Go to "Connectors" section
   - Click "Add Connector"
   - Enter URL: `http://localhost:8000/mcp`
   - Authenticate with GitHub when prompted

**Key changes**:
- No more `claude_desktop_config.json` editing
- Server runs independently in terminal
- Configuration via environment variables (.env file)
- Connect using URL instead of command/args
- Works with both Claude Desktop and Mobile

### Step 4: Optional Environment Configuration

If you want to customize settings, create a `.env` file:

```bash
cd /path/to/tinderbox-mcp
cp .env.example .env
```

Edit `.env` to customize:

```env
DEFAULT_DOCUMENT=YourDocumentName  # Without .tbx extension
APPLESCRIPT_DIR=./applescripts
GITHUB_CLIENT_ID=your_github_client_id
GITHUB_CLIENT_SECRET=your_github_client_secret
```

### Step 5: Verify Connection

1. Make sure the server is running in your terminal
2. In Claude Desktop, verify the connector shows as "Connected"
3. The Tinderbox tools should now be available in conversations

### Step 6: Test the Migration

Try a simple command to verify everything works:

```
In Tinderbox document 'Playground', create a note called 'Migration Test' in the Inbox
```

If successful, you should see the note appear in Tinderbox!

## Tool Name Changes

All tools now have a `tinderbox_` prefix to avoid conflicts with other MCP servers:

| Old Name (v0.1.x) | New Name (v0.2.x) |
|-------------------|-------------------|
| `create_note` | `tinderbox_create_note` |
| `read_note` | `tinderbox_read_note` |
| `get_children` | `tinderbox_get_children` |
| `get_siblings` | `tinderbox_get_siblings` |
| `get_links` | `tinderbox_get_links` |
| `link_notes` | `tinderbox_link_notes` |
| `update_attribute` | `tinderbox_update_attribute` |

**Impact**: This change is transparent to users. Claude will automatically use the new names. No changes needed to your prompts.

## Parameter Changes

**Good news**: All parameters remain identical! The tools accept the same arguments with the same names and defaults.

### Example: No Changes Needed

**v0.1.x (TypeScript)**:
```javascript
create_note({
  title: "My Note",
  text: "Content here",
  parent: "/Inbox/",
  document: "Playground"
})
```

**v0.2.x (Python)**:
```python
tinderbox_create_note({
  title: "My Note",
  text: "Content here",
  parent: "/Inbox/",
  document: "Playground"
})
```

Parameters are identical—only the tool name changed!

## Configuration Comparison

### Old: Stdio with claude_desktop_config.json
```json
{
  "mcpServers": {
    "tinderbox-mcp": {
      "command": "node",
      "args": ["/path/to/build/index.js", "/path/to/applescripts"]
    }
  }
}
```

### New: HTTP Server with Environment Variables
```bash
# Configure via .env file
DEFAULT_DOCUMENT=Playground
APPLESCRIPT_DIR=./applescripts
GITHUB_CLIENT_ID=your_id
GITHUB_CLIENT_SECRET=your_secret

# Run server independently
python src/server.py

# Connect via URL in Claude settings (Connectors)
# http://localhost:8000/mcp
```

**Advantages**:
- Server runs independently, can restart without restarting Claude
- Works with both Claude Desktop and Mobile
- Easier to configure and test
- Enables remote access via Tailscale/Ngrok

## Troubleshooting Migration Issues

### Issue: Server won't start

**Cause**: Missing dependencies or configuration

**Solution**:
```bash
# Make sure you're in the project directory
cd /path/to/tinderbox-mcp

# Activate virtual environment
source venv/bin/activate

# Verify dependencies are installed
pip install -r requirements.txt

# Check your .env file has GitHub OAuth credentials
cat .env

# Try starting server with verbose output
python src/server.py
```

### Issue: Tools not appearing in Claude

**Cause**: Server not running or connector not configured

**Solution**:
1. Verify the server is running in terminal
2. Check the server shows `Starting Tinderbox MCP Server...` message
3. In Claude, go to Settings → Connectors
4. Verify `http://localhost:8000/mcp` is added and shows "Connected"
5. Try removing and re-adding the connector
6. Complete GitHub OAuth authentication if prompted

### Issue: "Module not found" errors

**Cause**: Dependencies not installed or wrong Python version

**Solution**:
```bash
cd /path/to/tinderbox-mcp
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Issue: AppleScript errors

**Cause**: AppleScript directory path incorrect

**Solution**:
1. Verify `applescripts/` directory exists in project root
2. Check environment variable: `APPLESCRIPT_DIR=./applescripts`
3. Test manually: `osascript applescripts/create_note.scpt title=Test document=Playground`

### Issue: Want to use a different Python version

**Solution**:
```bash
# Remove old venv
rm -rf venv

# Create new venv with specific Python version
python3.11 -m venv venv  # Or python3.12, etc.
source venv/bin/activate
pip install -r requirements.txt
```

## Reverting to TypeScript Version

If you need to revert to the TypeScript version:

### Option 1: Use the TypeScript Branch

```bash
cd /path/to/tinderbox-mcp
git checkout typescript
npm install
npm run build
```

Then restore your old Claude Desktop configuration.

### Option 2: Use Tagged Version

```bash
cd /path/to/tinderbox-mcp
git checkout v0.1.0
npm install
npm run build
```

### Option 3: Keep Both Versions

You can run both versions simultaneously:

**TypeScript** (stdio via config file):
```json
// In claude_desktop_config.json
{
  "mcpServers": {
    "tinderbox-typescript": {
      "command": "node",
      "args": ["/path/to/typescript/build/index.js"]
    }
  }
}
```

**Python** (HTTP via connector):
1. Run: `python src/server.py` (different directory)
2. Add connector in Claude: `http://localhost:8000/mcp`

Both will be available simultaneously in Claude.

## Getting Help

If you encounter issues during migration:

1. **Check the main README**: [README.md](README.md)
2. **Review troubleshooting section**: Common issues and solutions
3. **Open an issue**: [GitHub Issues](https://github.com/phkus/tinderbox-mcp/issues)
4. **Tinderbox forums**: Post on [forum.tinderbox.com](https://forum.tinderbox.com/) (username: pkus)

## Benefits After Migration

Once migrated, you'll enjoy:

- ✅ **Cleaner codebase**: Easier to understand and modify
- ✅ **Better error messages**: More descriptive validation errors
- ✅ **Faster development**: Add new tools with less boilerplate
- ✅ **HTTP transport ready**: Enable remote access when needed
- ✅ **Official SDK updates**: Benefit from ongoing MCP improvements
- ✅ **Better documentation**: Comprehensive docstrings and type hints

## Advanced: Customizing Your Migration

### Custom AppleScript Directory

If your `.scpt` files are in a different location, set the environment variable:

```env
# In .env file
APPLESCRIPT_DIR=/absolute/path/to/scripts
```

Or export before running:
```bash
export APPLESCRIPT_DIR=/path/to/custom/scripts
python src/server.py
```

### Multiple Tinderbox Documents

For different documents, you can:

**Option 1**: Change default in .env
```env
DEFAULT_DOCUMENT=Research
```

**Option 2**: Specify document in each command
```
In Tinderbox document 'WorkNotes', create a note...
```

**Option 3**: Run multiple server instances
```bash
# Terminal 1 - Research server on port 8000
DEFAULT_DOCUMENT=Research python src/server.py

# Terminal 2 - Work server on port 8001
DEFAULT_DOCUMENT=WorkNotes SERVER_PORT=8001 python src/server.py
```

Then add both as connectors in Claude:
- `http://localhost:8000/mcp` (Research)
- `http://localhost:8001/mcp` (WorkNotes)

## Feedback Welcome

Your migration experience helps improve this guide! Please share:
- Any issues you encountered
- Solutions you discovered
- Suggestions for this guide

Open an issue or post on the Tinderbox forums.

---

**Need more help?** See the main [README.md](README.md) or open an [issue](https://github.com/phkus/tinderbox-mcp/issues).
