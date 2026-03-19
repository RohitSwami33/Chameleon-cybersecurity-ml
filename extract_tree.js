const fs = require('fs');
const path = require('path');

const IGNORE_DIRS = [
  'node_modules',
  '.git',
  '.venv',
  'venv',
  '__pycache__',
  '.pytest_cache',
  'dist',
  'build'
];

function generateTree(dir, prefix = '') {
  let output = '';
  let entries = fs.readdirSync(dir, { withFileTypes: true });

  // Filter and sort entries (directories first, then files)
  entries = entries.filter((file) => {
    return !IGNORE_DIRS.includes(file.name) && !file.name.endsWith('.DS_Store');
  }).sort((a, b) => {
    if (a.isDirectory() && !b.isDirectory()) return -1;
    if (!a.isDirectory() && b.isDirectory()) return 1;
    return a.name.localeCompare(b.name);
  });

  entries.forEach((entry, index) => {
    const isLast = index === entries.length - 1;
    const marker = isLast ? '└── ' : '├── ';
    const childPrefix = isLast ? '    ' : '│   ';

    output += `${prefix}${marker}${entry.name}\n`;

    if (entry.isDirectory()) {
      const childrenTree = generateTree(path.join(dir, entry.name), prefix + childPrefix);
      output += childrenTree;
    }
  });

  return output;
}

const rootDir = process.cwd();
console.log('Generating tree for:', rootDir);
const tree = generateTree(rootDir);

const markdownOutput = `# Chameleon Project Directory Structure
\`\`\`text
Chameleon/
${tree}
\`\`\`
`;

fs.writeFileSync('project_structure.md', markdownOutput, 'utf-8');
console.log('Generated project_structure.md successfully.');
