import { execFile } from "node:child_process";
import { promisify } from "node:util";
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

const execFileAsync = promisify(execFile);

const CURIE_PATH = "/home/curie/curie";
const WAKE_PREFIX = /^\s*(?:(?:hey|hi|hello|ok(?:ay)?)\s+)?curie\b[\s,:-]*/i;

function extractCurieCommand(text: string | undefined): string | null {
  const trimmed = (text ?? "").trim();
  if (!trimmed || !WAKE_PREFIX.test(trimmed)) {
    return null;
  }
  const command = trimmed.replace(WAKE_PREFIX, "").trim();
  return command || "help";
}

async function runCurie(command: string): Promise<string> {
  const { stdout, stderr } = await execFileAsync(CURIE_PATH, [command], {
    timeout: 45000,
  });
  const output = stdout.trim() || stderr.trim();
  return output || "Curie command finished.";
}

export default definePluginEntry({
  id: "curie-command-router",
  name: "Curie Command Router",
  description: "Runs local Curie robot commands before model dispatch when the user addresses Curie directly.",
  register(api) {
    api.on("before_dispatch", async (event) => {
      const command = extractCurieCommand(event.content || event.body);
      if (!command) {
        return undefined;
      }

      try {
        const text = await runCurie(command);
        return { handled: true, text };
      } catch (error) {
        const message = error instanceof Error ? error.message : String(error);
        api.logger.error(`curie-command-router: command failed: ${message}`);
        return { handled: true, text: `Curie command failed: ${message}` };
      }
    });
  },
});
