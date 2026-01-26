import fs from "fs";
import path from "path";
import { Codex } from "@openai/codex-sdk";

type Task = {
  id: string;
  title: string;
  milestone: string;
  prompt: string;
  sourceFile: string;
};

const TASKS_DIR = path.join(process.cwd(), ".tasks");
const SELECTED_MILESTONE = process.env.MILESTONE ?? "M0";
const OUTPUT_ROOT = path.join(process.cwd(), "codex_output");
const TASK_HEADER = /^##\s+(M\d+[a-z]?\.T\d+)\s*-\s*(.+)$/gm;

function listTaskFiles(): string[] {
  if (!fs.existsSync(TASKS_DIR)) {
    return [];
  }

  return fs
    .readdirSync(TASKS_DIR)
    .filter(name => name.endsWith(".md") && name !== "00-overview.md")
    .sort()
    .map(name => path.join(TASKS_DIR, name));
}

function parseTasksFromFile(filePath: string): Task[] {
  const content = fs.readFileSync(filePath, "utf8");
  const matches = Array.from(content.matchAll(TASK_HEADER));

  return matches.map((match, index) => {
    const start = match.index ?? 0;
    const end =
      index + 1 < matches.length
        ? matches[index + 1].index ?? content.length
        : content.length;

    const block = content.slice(start, end).trim();
    const id = match[1];
    const title = match[2].trim();
    const milestone = id.split(".")[0];

    return {
      id,
      title,
      milestone,
      prompt: block,
      sourceFile: path.basename(filePath)
    };
  });
}

function loadTasks(): Task[] {
  const files = listTaskFiles();
  return files.flatMap(file => parseTasksFromFile(file));
}

function filterTasks(tasks: Task[]): Task[] {
  if (SELECTED_MILESTONE.toLowerCase() === "all") {
    return tasks;
  }

  return tasks.filter(task => task.milestone === SELECTED_MILESTONE);
}

function listMilestones(tasks: Task[]): string[] {
  return Array.from(new Set(tasks.map(task => task.milestone))).sort();
}

async function run() {
  const codex = new Codex({
    defaultModel: "gpt-5.2-codex-extra-high"
  });

  const allTasks = loadTasks();
  if (allTasks.length === 0) {
    throw new Error("No tasks found in .tasks directory.");
  }

  const milestoneTasks = filterTasks(allTasks);
  if (milestoneTasks.length === 0) {
    const available = listMilestones(allTasks).join(", ");
    throw new Error(
      `No tasks found for milestone '${SELECTED_MILESTONE}'. Available: ${available}`
    );
  }

  console.log(
    `Running milestone: ${SELECTED_MILESTONE} with ${milestoneTasks.length} tasks`
  );

  const outputDir = path.join(OUTPUT_ROOT, SELECTED_MILESTONE);
  fs.mkdirSync(outputDir, { recursive: true });

  for (const task of milestoneTasks) {
    console.log(`Running task ${task.id}: ${task.title}`);

    const thread = codex.startThread();

    const result = await thread.run(`
Source: ${task.sourceFile}
${task.prompt}

Please complete this task. Follow AGENTS.md and .tasks/00-overview.md. Provide code, explanations, and notes.
`);

    const filename = path.join(outputDir, `${task.id}.txt`);
    fs.writeFileSync(filename, result.text, { encoding: "utf8" });
    console.log(`Saved output: ${filename}`);

    await thread.end();
  }

  console.log("Milestone completed.");
}

run().catch(err => {
  console.error("Error executing task loop:", err);
  process.exit(1);
});
