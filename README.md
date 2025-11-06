# Tinderbox MCP Server

A Model Context Protocol (MCP) server that enables AI assistants like Claude to interact with [Tinderbox](https://www.eastgate.com/Tinderbox/), a powerful knowledge management application for macOS. This allows you to control Tinderbox with natural language and to connect it to other services that the assistant has access to. In the background, it uses the AppleScript integration of Tinderbox to create and update notes and to navigate the hierarchy of a document.

## 🔄 Migration Notice: Version 0.2.0

**Version 0.2.0+ has been rewritten in Python using HTTP transport for remote access.**

### Why Python?
The Python rewrite enables **HTTP-based remote access**, allowing you to:
- Connect from Claude Mobile apps using Connectors
- Access your Tinderbox server from anywhere via Tailscale or Ngrok
- Share your Tinderbox server with team members securely
- Use modern OAuth authentication (GitHub) for secure access

### For Existing Users
- **TypeScript version 0.1.x** remains available on the [`typescript`](https://github.com/phkus/tinderbox-mcp/tree/typescript) branch
- **No breaking changes** to tool functionality - all tools work identically
- **Same AppleScript files** - the `.scpt` files are unchanged
- See [UPGRADE.md](UPGRADE.md) for migration guide

---

## Included Tinderbox Operations

The server includes tools for these Tinderbox actions:

- `create_note` - Create a new note in your document
- `link_notes` - Create links between existing notes, optionally with a link type
- `update_attributes` - Change attribute values for specified notes
- `read_note` - Retrieve the content of a note (currently only the title and text of a note)
- `get_siblings` - Find notes at the same hierarchical level (this and the following tools returns the paths of the notes and their ChildCount, to let the assistant know where it can explore further)
- `get_children` - Get all child notes of a specified parent note
- `get_links` - Find all outgoing links from a note

All of these actions require the model to know which document to use. The default document can be configured (see Configuration section below).

## Prerequisites

- [Tinderbox](https://www.eastgate.com/Tinderbox/)
- macOS (for Tinderbox AppleScript integration)
- Python 3.10 or higher
- A GitHub account (for OAuth authentication)
- An MCP-compatible client (this was tested with Claude Desktop and Claude Mobile)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/phkus/tinderbox-mcp.git
cd tinderbox-mcp
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up GitHub OAuth App:
   - Go to https://github.com/settings/developers
   - Click "New OAuth App"
   - Fill in:
     - Application name: `Tinderbox MCP`
     - Homepage URL: `http://localhost:8000`
     - Authorization callback URL: `http://localhost:8000/oauth/callback`
   - Save your Client ID and Client Secret

5. Configure the server (choose one method):

   **Method A: Using .env file** (recommended for most users)
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

   **Method B: Export environment variables** (good for testing)
   ```bash
   export GITHUB_CLIENT_ID="your_client_id"
   export GITHUB_CLIENT_SECRET="your_client_secret"
   export DEFAULT_DOCUMENT="YourDocument"  # Without .tbx extension
   ```

   **Method C: Set inline when launching** (quick one-time testing)
   ```bash
   GITHUB_CLIENT_ID="your_id" GITHUB_CLIENT_SECRET="your_secret" DEFAULT_DOCUMENT="YourDocument" python src/server.py
   ```

## Configuration

### Required Settings

- `GITHUB_CLIENT_ID`: Your GitHub OAuth app client ID
- `GITHUB_CLIENT_SECRET`: Your GitHub OAuth app client secret

### Optional Settings

- `DEFAULT_DOCUMENT`: Name of your Tinderbox document **without the .tbx extension**
  - Example: If your file is `Research.tbx`, set `DEFAULT_DOCUMENT=Research`
  - Leave empty to specify document in each request
- `APPLESCRIPT_DIR`: Path to AppleScript files (default: `./applescripts`)
- `SERVER_PORT`: Server port (default: `8000`)
- `SERVER_HOST`: Server host (default: `localhost`)

**Note**: Environment variables can be set in three ways (see Installation step 5 above). The `.env` file is the most convenient for permanent configuration.

## Running the Server

Start the server in a terminal:

```bash
source venv/bin/activate  # If not already activated
python src/server.py
```

You should see output like:
```
Starting Tinderbox MCP Server on http://localhost:8000
MCP endpoint: http://localhost:8000/mcp
AppleScript directory: /path/to/applescripts
Default document: YourDocument

Add this URL as a Connector in Claude settings:
  http://localhost:8000/mcp
```

**Keep this terminal window open** - the server needs to stay running to handle requests.

## Using with Claude

### Claude Desktop

1. Open Claude Desktop settings
2. Go to the "Connectors" section
3. Click "Add Connector"
4. Enter the URL: `http://localhost:8000/mcp`
5. Authenticate with GitHub when prompted
6. The Tinderbox tools will now be available

### Claude Mobile

1. Open Claude app settings
2. Go to "Connectors"
3. Add new connector with URL: `http://localhost:8000/mcp`
4. Complete GitHub OAuth in browser
5. Start using Tinderbox tools in conversations

### Remote Access (Advanced)

To access your Tinderbox server from anywhere (not just localhost):

**Option 1: Tailscale** (recommended for security)
- Install [Tailscale](https://tailscale.com/) on your Mac and mobile device
- Both devices will share a private network
- Use Tailscale IP instead of `localhost` in connector URL
- Example: `http://100.x.x.x:8000/mcp`

**Option 2: Ngrok** (temporary public access)
- Install [Ngrok](https://ngrok.com/)
- Run: `ngrok http 8000`
- Use the ngrok URL in Claude connector
- Example: `https://abc123.ngrok.io/mcp`
- Note: Free ngrok URLs change on restart

**Security Note**: Always use OAuth authentication for remote access. Never disable authentication when exposing your server beyond localhost.

### Example Usage

Once configured, you can ask Claude to work with your Tinderbox documents:

- "In the Tinderbox document 'Research project', create notes based on the main points of our conversation."
- "In the Tinderbox document 'Research project', explore the children of the note 'path/to/note' and suggest connections. Confirm the links with me before creating them."
- "In the Tinderbox document 'Research project', create a diagram that reproduces the image that I uploaded. You can set the position of notes on a Tinderbox map using the 'Xpos' and 'Ypos' attributes. X goes from left to right, Y from top to bottom. Both can have negative numbers and a map has no real boundaries, but as a general guideline, you can assume a top-left corner of 0 and 0, and a bottom right corner of around 40 and 40. Notes can be coloured by changing the 'Color' attribute in hex code."

## Warning

The `update_attribute` tool allows the assistant to overwrite attributes of existing notes, including the Name and Text attributes. The tool description provided to the model asks it to be cautious with this, but it could still lead to loss of content. Keep backups of your Tinderbox documents.

This is the only tool that can change the content of existing notes, because `create_note` will just create a new note with the same name in the same container. For extra security, you could remove the `update_attribute` tool by deleting either the entry in the configuration or the script file. Alternatively, the AppleScript could be changed to only allow editing attributes without any value.

## Extending the Server

The existing script files in the applescripts folder can be edited at any time, even while the server is running. To add custom Tinderbox operations, the server has to be restarted:

1. Create a new AppleScript (.scpt) file in the same location as the others
2. Add a tool definition with `@mcp.tool()` decorator in `src/server.py`
3. Restart the server

See [CLAUDE.md](CLAUDE.md) for detailed development instructions.

## Roadmap

- [x] Migrate to Python with HTTP transport
- [x] Add GitHub OAuth authentication
- [ ] Move the tool configuration, which is currently part of the main code, to a separate file
- [ ] A tool that gives the assistant an overview of parts or the whole of the document, similar to Export -> As Outline
- [ ] Add a similar server for DEVONthink
- [ ] Add a similar server for Bookends

## Troubleshooting

### Server won't start

**"GitHub OAuth credentials required"**
- Make sure you've created a GitHub OAuth app
- Set `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` environment variables
- Check your `.env` file has the correct values

**"AppleScript directory does not exist"**
- Verify `applescripts/` folder exists in the project root
- Check `APPLESCRIPT_DIR` environment variable if you moved the scripts

### Tools not working

**"Document not found"**
- Make sure the Tinderbox document is open in Tinderbox
- Verify `DEFAULT_DOCUMENT` matches the document name exactly (without .tbx)
- Document names are case-sensitive

**"Script not found"**
- Verify all `.scpt` files exist in the `applescripts/` directory
- Check file permissions allow reading

### Connection issues

**Can't connect from Claude**
- Verify the server is running (check terminal window)
- Test the URL in a browser: `http://localhost:8000/mcp`
- Check firewall isn't blocking port 8000
- For remote access, verify Tailscale/Ngrok is properly configured

## Acknowledgements

This project was inspired by Josh Rutkowski's [applescript-mcp](https://github.com/joshrutkowski/applescript-mcp/tree/main) server. The main difference between the two servers is that applescript-mcp passes the full content of the AppleScript to the terminal, whereas this implementation calls separate script files, which solved some problems with special characters like quotes in the parameters.

Thanks to Mark Bernstein, the developer of Tinderbox, for making the app scriptable.

## License

MIT

## Contributing

Feel free to contribute here or by sending me feedback on the Tinderbox forums (username: pkus).

This is basically just a server that executes AppleScript. It can therefore be adapted to do anything else that is scriptable on MacOS.

---

**Note**: For TypeScript version documentation, see the [`typescript` branch](https://github.com/phkus/tinderbox-mcp/tree/typescript).
