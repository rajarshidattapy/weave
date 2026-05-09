import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

async function generateTree(dirPath: string): Promise<any> {
  const tree: any = {};
  
  try {
    const entries = await fs.readdir(dirPath, { withFileTypes: true });

    for (const entry of entries) {
      // Ignore massive directories to keep the payload size manageable and avoid parsing binaries unnecessarily
      if (entry.name === 'node_modules' || entry.name === '.next' || entry.name === '.git') {
        continue;
      }

      const fullPath = path.join(dirPath, entry.name);

      if (entry.isDirectory()) {
        tree[entry.name] = {
          directory: await generateTree(fullPath),
        };
      } else {
        try {
          // Note: Binary files might fail to be read as utf-8, but Next.js source files are generally safe.
          // For a production app, we would use Uint8Array or base64 for images/fonts.
          const contents = await fs.readFile(fullPath, 'utf-8');
          tree[entry.name] = {
            file: {
              contents,
            },
          };
        } catch (e) {
          console.warn(`Skipping file ${fullPath}: unable to read as utf-8.`);
        }
      }
    }
  } catch (err) {
    console.error(`Failed to read directory: ${dirPath}`, err);
  }

  return tree;
}

export async function GET() {
  try {
    // Determine the path to test-next
    // process.cwd() in Next.js is usually the root of the UI project (c:\Users\asus\Desktop\proj\weave\ui)
    const basePath = path.resolve(process.cwd(), '../test-next');
    
    // Check if it exists
    await fs.access(basePath);
    
    const tree = await generateTree(basePath);
    return NextResponse.json({ tree });
  } catch (error) {
    console.error('Error generating filesystem tree:', error);
    return NextResponse.json({ error: 'Failed to generate filesystem tree' }, { status: 500 });
  }
}
