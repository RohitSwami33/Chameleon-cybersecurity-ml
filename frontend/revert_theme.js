import fs from 'fs';
import path from 'path';

// Revert Theme back to Blue
const walkDir = (dir, callback) => {
    const items = fs.readdirSync(dir);
    for (const item of items) {
        const itemPath = path.join(dir, item);
        const stat = fs.statSync(itemPath);
        if (stat.isDirectory()) {
            walkDir(itemPath, callback);
        } else if (itemPath.endsWith('.jsx') || itemPath.endsWith('.js') || itemPath.endsWith('.css')) {
            callback(itemPath);
        }
    }
};

let replacedCount = 0;

walkDir('./src', (filePath) => {
    let content = fs.readFileSync(filePath, 'utf-8');
    
    // Switch Red back to Blue
    let newContent = content
        .replace(/#ff2a2a/gi, '#00d4ff')
        .replace(/255,\s*42,\s*42/g, '0, 212, 255')
        .replace(/255,42,42/g, '0,212,255');
        
    // Reverse the index.css specific variable
    newContent = newContent.replace(/--primary:\s*#[a-fA-F0-9]{6}/gi, '--primary: #00d4ff');
    
    if (content !== newContent) {
        fs.writeFileSync(filePath, newContent, 'utf-8');
        console.log(`Reverted theme in: ${filePath}`);
        replacedCount++;
    }
});

console.log(`\nOriginal Blue Theme Restored successfully to ${replacedCount} files.`);
