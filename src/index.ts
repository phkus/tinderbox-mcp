#!/usr/bin/env node

import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import * as fs from "fs";
import * as path from "path";
import { execFile } from "child_process";
import { promisify } from "util";

// Create a promisified version of execFile
const execFileAsync = promisify(execFile);

// Get the scripts directory from command line args or use a default
const scriptsDir = process.argv[2] || "./applescripts";

// Define a type for script configurations
type ScriptConfig = {
  description: string;
  parameters: Record<string, z.ZodType<any>>;
};

// Registry of script configurations
const scriptConfigs: Record<string, ScriptConfig> = {
  "create_note": {
    description: "Creates a new note",
    parameters: {
      title: z.string().describe("The title of the note").default("New Note"),
	  text: z.string().describe("The text of the note").default(""),
	  parent: z.string().describe("The path of the parent note").default("/Inbox/"),
	  document: z.string().describe("The name of the Tinderbox document").default("Playground"),
    },
  },
  "read_note": {
  	description: "Reads the content of a note",
  	parameters: {
  	  path: z.string().describe("The path of the note to read"),
  	  document: z.string().describe("The name of the Tinderbox document").default("Playground"),
  	},
  },
  "get_children": {
  	description: "Gets the children of a note",
  	parameters: {
  	  path: z.string().describe("The path of the note").default(""),
  	  document: z.string().describe("The name of the Tinderbox document").default("Playground"),
  	},
  },
  "get_links": {
  	description: "Gets the outgoing links from a note",
  	parameters: {
  	  path: z.string().describe("The path of the note").default(""),
  	  document: z.string().describe("The name of the Tinderbox document").default("Playground"),
  	},
  },
  "get_siblings": {
  	description: "Gets the siblings of a note",
  	parameters: {
  	  path: z.string().describe("The path of the note").default(""),
  	  document: z.string().describe("The name of the Tinderbox document").default("Playground"),
  	},
  },
  "link_notes": {
  	description: "Creates a link between two notes",
  	parameters: {
  	  source: z.string().describe("The path of the beginning of the link").default(""),
  	  destination: z.string().describe("The path of the destination of the link").default(""),
  	  linktype: z.string().describe("The optional link label, for example 'contrast', 'source' or 'influence'").default("*untitled"),
  	  document: z.string().describe("The name of the Tinderbox document").default("Playground"),
  	},
  },
  "update_attribute": {
  	description: "Updates an attribute of a note. Be careful with this tool as it allows overwriting the attributes of existing notes. Ask for confirmation before updating attributes of notes that already existed before this conversation.",
  	parameters: {
  	  path: z.string().describe("The path of the note").default(""),
  	  attribute: z.string().describe("The name of the attribute, e.g. 'Color' or 'URL'").default(""),
  	  value: z.string().describe("The value of the attribute").default(""),
  	  document: z.string().describe("The name of the Tinderbox document").default("Playground"),
  	},
  },
  // Add more script configurations as needed
};

// Ensure the scripts directory exists
if (!fs.existsSync(scriptsDir)) {
  console.error(`Scripts directory ${scriptsDir} does not exist.`);
  process.exit(1);
}

// Validate that a script is within the allowed directory
function validateScriptPath(scriptPath: string): string {
  // Resolve to absolute paths for comparison
  const absoluteScriptsDir = path.resolve(scriptsDir);
  const absoluteScriptPath = path.resolve(absoluteScriptsDir, scriptPath);
  
  // Security check: ensure the script is within the scripts directory
  if (!absoluteScriptPath.startsWith(absoluteScriptsDir)) {
    throw new Error("Script path must be within the configured scripts directory");
  }
  
  // Check if the script exists
  if (!fs.existsSync(absoluteScriptPath)) {
    throw new Error(`Script ${scriptPath} does not exist`);
  }
  
  // Check if it has .scpt extension
  if (!absoluteScriptPath.endsWith('.scpt')) {
    throw new Error("Script must have .scpt extension");
  }
  
  return absoluteScriptPath;
}

// Create the MCP server
const server = new McpServer({
  name: "AppleScript-Runner",
  version: "1.0.0"
});

// Register a tool for each configured script
function registerScriptTools() {
  // Only register scripts that have configurations
  for (const [scriptName, config] of Object.entries(scriptConfigs)) {
    // Skip if the script file doesn't exist
    try {
      validateScriptPath(`${scriptName}.scpt`);
    } catch (error) {
      console.error(`Script ${scriptName} not found in ${scriptsDir}. Skipping.`);
      continue;
    }
    
    // Register the tool with its specific parameters
    server.tool(
      scriptName,
      config.description,
      config.parameters,
      async (params) => {
        try {
          const scriptPath = validateScriptPath(`${scriptName}.scpt`);
	
		  // Create a schema object from the parameters
	      const paramsSchema = z.object(
	        Object.fromEntries(
	          Object.entries(config.parameters)
	        )
	      );
      
	      // Parse params with the schema - this will apply defaults automatically
	      const validatedParams = paramsSchema.parse(params);
      
	      // Convert parameters to key=value format
	      const args = Object.entries(validatedParams).map(([key, value]) => `${key}=${value}`);
          
          // Execute the AppleScript with osascript
          const { stdout, stderr } = await execFileAsync('osascript', [scriptPath, ...args]);
          
          const result = stdout.trim();
          const errors = stderr.trim();
          
          if (errors) {
            return {
              content: [{ 
                type: "text", 
                text: `Script execution had errors:\n${errors}${result ? `\n\nOutput:\n${result}` : ''}` 
              }],
              isError: true
            };
          }
          
          return {
            content: [{ 
              type: "text", 
              text: result || "Script executed successfully with no output."
            }]
          };
        } catch (error) {
          console.error(`Error running ${scriptName} script:`, error);
          return {
            content: [{ type: "text", text: `Error running ${scriptName} script: ${error}` }],
            isError: true
          };
        }
      }
    );
    
    console.error(`Registered tool for script: ${scriptName}`);
  }
}

// Register the configured script tools
registerScriptTools();

// Initialize and connect the server
async function main() {
  try {
    console.error(`AppleScript Runner MCP Server`);
    console.error(`Using scripts directory: ${path.resolve(scriptsDir)}`);
    console.error(`Registered scripts: ${Object.keys(scriptConfigs).join(', ')}`);
    
    const transport = new StdioServerTransport();
    await server.connect(transport);
    console.error("Server connected to transport");
  } catch (error) {
    console.error("Error starting server:", error);
    process.exit(1);
  }
}

main().catch(console.error);