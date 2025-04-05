# Tinderbox MCP Server

A Model Context Protocol (MCP) server that enables AI assistants like Claude to interact with [Tinderbox](https://www.eastgate.com/Tinderbox/), a powerful knowledge management application for macOS. This allows you to control Tinderbox with natural language and to connect it to other services that the assistant has access to. In the background, it uses the AppleScript integration of Tinderbox to create and update notes and to navigate the hierarchy of a document.

## Included Tinderbox Operations

The server includes tools for these Tinderbox actions:

- `create_note` - Create a new note in your document
- `link_notes` - Create links between existing notes, optionally with a link type
- `update_attributes` - Change attribute values for specified notes
- `read_note` - Retrieve the content of a note (currently only the title and text of a note)
- `get_siblings` - Find notes at the same hierarchical level (this and the following tools returns the paths of the notes and their ChildCount, to let the assistant know where it can explore further)
- `get_children` - Get all child notes of a specified parent note
- `get_links` - Find all outgoing links from a note

All of these actions require the model to know which document to use. The default document is currently called `Playground`, which is my own test document. This and the other default values can be changed in the script configurations in `/src/index.ts`.

## Prerequisites

- [Tinderbox](https://www.eastgate.com/Tinderbox/)
- Node.js 18 or higher
- An MCP-compatible client (this was only tested with Claude Desktop)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/phkus/tinderbox-mcp.git
cd tinderbox-mcp
```

2. Install dependencies:
```bash
npm install
```

3. Build the project:
```bash
npm run build
```

## Running the Server

Run the server with:

```bash
npm run start
```

## Using with Claude Desktop

1. Add the following configuration to the config file of the Claude Desktop app (located at `~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "tinderbox-mcp": {
      "command": "node",
      "args": ["/absolute/path/to/your/tinderbox-mcp/build/index.js", "/absolute/path/to/your/applescripts"]
    }
  }
}
```

Fill in the path to your installation and to the applescripts directory. The scripts are in the root folder of the installation by default, but can also be stored somewhere else for easier editing.

2. Restart Claude for Desktop

3. Ask Claude to work with your Tinderbox documents, for example:
- “In the Tinderbox document ‘Research project’, create notes based on the main points of our conversation.”
- “In the Tinderbox document ‘Research project’, explore the children of the note ‘path/to/note’ and suggest connections. Confirm the links with me before creating them.”
- “In the Tinderbox document ‘Research project’, create a diagram that reproduces the image that I uploaded. You can set the position of notes on a Tinderbox map using the ‘Xpos’ and ‘Ypos’ attributes. X goes from left to right, Y from top to bottom. Both can have negative numbers and a map has no real boundaries, but as a general guideline, you can assume a top-left corner of 0 and 0, and a bottom right corner of around 40 and 40. Notes can be coloured by changing the ‘Color’ attribute in hex code.”

## Warning

The `update_attribute` tool allows the assistant to overwrite attributes of existing notes, including the Name and Text attributes. The tool description provided to the model asks it to be cautious with this, but it could still lead to loss of content. Keep backups of your Tinderbox documents.

This is the only tool that can change the content of existing notes, because `create_note` will just create a new note with the same name in the same container. For extra security, you could remove the `update_attribute` tool by deleting either the entry in the configuration or the script file. Alternatively, the AppleScript could be changed to only allow editing attributes without any value.

## Extending the Server

The existing script files in the applescripts folder can be edited at any time, even while the server is running. To add custom Tinderbox operations, the server has to be restarted:

1. Create a new AppleScript (.scpt) file in the same location as the others
2. Add a configuration entry in `src/index.ts`
3. Rebuild the project and restart the client

## Roadmap

- [ ] Move the tool configuration, which is currently part of the main code, to a separate file
- [ ] A tool that gives the assistant an overview of parts or the whole of the document, similar to Export -> As Outline
- [ ] Add a similar server for DEVONthink
- [ ] Add a similar server for Bookends

## Acknowledgements

This project was inspired by Josh Rutkowski’s [applescript-mcp](https://github.com/joshrutkowski/applescript-mcp/tree/main) server. The main difference between the two servers is that applescript-mcp passes the full content of the AppleScript to the terminal, whereas this implementation calls separate script files, which solved some problems with special characters like quotes in the parameters.

Thanks to Mark Bernstein, the developer of Tinderbox, for making the app scriptable.

## License

MIT

## Contributing

Feel free to contribute here or by sending me feedback on the Tinderbox forums (username: pkus).

This is basically just a server that executes AppleScript. It can therefore be adapted to do anything else that is scriptable on MacOS.
