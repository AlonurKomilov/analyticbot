#!/usr/bin/env node
/**
 * Automated Import Path Fixer
 * Converts deep relative imports to path aliases
 *
 * Usage: node scripts/fix-import-paths.js
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Import patterns to fix
const importPatterns = [
  {
    pattern: /from ['"]\.\.\/\.\.\/\.\.\/\.\.\/components\/(.*?)['"]/g,
    replacement: "from '@components/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/\.\.\/components\/(.*?)['"]/g,
    replacement: "from '@components/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/components\/(.*?)['"]/g,
    replacement: "from '@components/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/\.\.\/\.\.\/utils\/(.*?)['"]/g,
    replacement: "from '@utils/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/\.\.\/utils\/(.*?)['"]/g,
    replacement: "from '@utils/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/utils\/(.*?)['"]/g,
    replacement: "from '@utils/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/\.\.\/\.\.\/hooks\/(.*?)['"]/g,
    replacement: "from '@hooks/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/\.\.\/hooks\/(.*?)['"]/g,
    replacement: "from '@hooks/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/hooks\/(.*?)['"]/g,
    replacement: "from '@hooks/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/\.\.\/\.\.\/store\/(.*?)['"]/g,
    replacement: "from '@store/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/\.\.\/store\/(.*?)['"]/g,
    replacement: "from '@store/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/store\/(.*?)['"]/g,
    replacement: "from '@store/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/\.\.\/\.\.\/contexts\/(.*?)['"]/g,
    replacement: "from '@/contexts/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/\.\.\/contexts\/(.*?)['"]/g,
    replacement: "from '@/contexts/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/contexts\/(.*?)['"]/g,
    replacement: "from '@/contexts/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/\.\.\/\.\.\/api\/(.*?)['"]/g,
    replacement: "from '@api/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/\.\.\/api\/(.*?)['"]/g,
    replacement: "from '@api/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/api\/(.*?)['"]/g,
    replacement: "from '@api/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/\.\.\/\.\.\/services\/(.*?)['"]/g,
    replacement: "from '@services/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/\.\.\/services\/(.*?)['"]/g,
    replacement: "from '@services/$1'"
  },
  {
    pattern: /from ['"]\.\.\/\.\.\/services\/(.*?)['"]/g,
    replacement: "from '@services/$1'"
  },
];

// File extensions to process
const extensions = ['.js', '.jsx', '.ts', '.tsx'];

// Statistics
let stats = {
  filesProcessed: 0,
  filesModified: 0,
  importsFixed: 0
};

/**
 * Recursively get all files in directory
 */
function getAllFiles(dirPath, arrayOfFiles = []) {
  const files = fs.readdirSync(dirPath);

  files.forEach(file => {
    const filePath = path.join(dirPath, file);

    if (fs.statSync(filePath).isDirectory()) {
      // Skip node_modules, dist, build
      if (!['node_modules', 'dist', 'build', '.git'].includes(file)) {
        arrayOfFiles = getAllFiles(filePath, arrayOfFiles);
      }
    } else {
      // Only process JS/JSX/TS/TSX files
      if (extensions.some(ext => filePath.endsWith(ext))) {
        arrayOfFiles.push(filePath);
      }
    }
  });

  return arrayOfFiles;
}

/**
 * Fix imports in a file
 */
function fixImportsInFile(filePath) {
  stats.filesProcessed++;

  let content = fs.readFileSync(filePath, 'utf8');
  let originalContent = content;
  let fixesInThisFile = 0;

  // Apply all patterns
  importPatterns.forEach(({ pattern, replacement }) => {
    const matches = content.match(pattern);
    if (matches) {
      fixesInThisFile += matches.length;
      content = content.replace(pattern, replacement);
    }
  });

  // Only write if content changed
  if (content !== originalContent) {
    fs.writeFileSync(filePath, content, 'utf8');
    stats.filesModified++;
    stats.importsFixed += fixesInThisFile;

    const relativePath = path.relative(process.cwd(), filePath);
    console.log(`✅ Fixed ${fixesInThisFile} import(s) in: ${relativePath}`);
  }
}

/**
 * Main execution
 */
function main() {
  console.log('🔧 Starting import path fixing...\n');

  const srcDir = path.join(path.dirname(__dirname), 'src');

  if (!fs.existsSync(srcDir)) {
    console.error('❌ Error: src directory not found');
    process.exit(1);
  }

  const files = getAllFiles(srcDir);
  console.log(`📁 Found ${files.length} files to process\n`);

  files.forEach(filePath => {
    try {
      fixImportsInFile(filePath);
    } catch (error) {
      console.error(`❌ Error processing ${filePath}:`, error.message);
    }
  });

  console.log('\n📊 Summary:');
  console.log(`   Files processed: ${stats.filesProcessed}`);
  console.log(`   Files modified: ${stats.filesModified}`);
  console.log(`   Imports fixed: ${stats.importsFixed}`);
  console.log('\n✨ Import path fixing complete!');
}

// Run the script
main();
