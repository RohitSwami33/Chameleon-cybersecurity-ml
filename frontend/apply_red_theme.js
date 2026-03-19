import fs from 'fs';
import path from 'path';

// Red Theme details
// Blue: #00d4ff (HEX), 0, 212, 255 (RGB), 0,212,255 (RGB Spaceless)
// Red:  #ff2a2a (HEX), 255, 42, 42 (RGB), 255,42,42 (RGB Spaceless)

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
    
    // Perform case-insensitive replacements
    let newContent = content
        .replace(/#00d4ff/gi, '#ff2a2a')
        .replace(/0,\s*212,\s*255/g, '255, 42, 42')
        .replace(/0,212,255/g, '255,42,42');
        
    // Also the primary text-shadow/glow variable in index.css
    newContent = newContent.replace(/--primary:\s*#[a-fA-F0-9]{6}/gi, '--primary: #ff2a2a');
    
    if (content !== newContent) {
        fs.writeFileSync(filePath, newContent, 'utf-8');
        console.log(`Updated theme in: ${filePath}`);
        replacedCount++;
    }
});

console.log(`\nRed Theme Applied successfully to ${replacedCount} files.`);
