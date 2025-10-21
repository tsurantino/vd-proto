/**
 * Simple Node.js server for volumetric display simulator
 * Includes markdown documentation viewer
 */

import express from 'express';
import path from 'path';
import fs from 'fs/promises';
import { fileURLToPath } from 'url';
import { marked } from 'marked';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
const PORT = process.env.PORT || 8000;

// Serve static files
app.use(express.static(__dirname));

// API endpoint to list all markdown files
app.get('/api/docs', async (req, res) => {
    try {
        const docs = [];

        // Root directory markdown files
        const rootFiles = await fs.readdir(__dirname);
        for (const file of rootFiles) {
            if (file.endsWith('.md')) {
                const stats = await fs.stat(path.join(__dirname, file));
                docs.push({
                    name: file.replace('.md', ''),
                    path: file,
                    category: 'Documentation',
                    size: stats.size,
                    modified: stats.mtime
                });
            }
        }

        // TD directory markdown files
        const tdPath = path.join(__dirname, 'td');
        try {
            const tdFiles = await fs.readdir(tdPath);
            for (const file of tdFiles) {
                if (file.endsWith('.md')) {
                    const stats = await fs.stat(path.join(tdPath, file));
                    docs.push({
                        name: file.replace('.md', ''),
                        path: `td/${file}`,
                        category: 'TouchDesigner',
                        size: stats.size,
                        modified: stats.mtime
                    });
                }
            }
        } catch (err) {
            // TD directory doesn't exist or is inaccessible
            console.log('TD directory not found or inaccessible');
        }

        res.json(docs);
    } catch (error) {
        console.error('Error listing docs:', error);
        res.status(500).json({ error: 'Failed to list documentation' });
    }
});

// API endpoint to get markdown file content (raw)
app.get('/api/docs/raw/:path(*)', async (req, res) => {
    try {
        const filePath = path.join(__dirname, req.params.path);

        // Security check: ensure the path is within the project directory
        const resolvedPath = path.resolve(filePath);
        const projectRoot = path.resolve(__dirname);
        if (!resolvedPath.startsWith(projectRoot)) {
            return res.status(403).json({ error: 'Access denied' });
        }

        const content = await fs.readFile(filePath, 'utf-8');
        res.type('text/plain').send(content);
    } catch (error) {
        console.error('Error reading markdown:', error);
        res.status(404).json({ error: 'File not found' });
    }
});

// API endpoint to get rendered markdown HTML
app.get('/api/docs/html/:path(*)', async (req, res) => {
    try {
        const filePath = path.join(__dirname, req.params.path);

        // Security check
        const resolvedPath = path.resolve(filePath);
        const projectRoot = path.resolve(__dirname);
        if (!resolvedPath.startsWith(projectRoot)) {
            return res.status(403).json({ error: 'Access denied' });
        }

        const content = await fs.readFile(filePath, 'utf-8');

        // Configure marked for GitHub-flavored markdown
        marked.setOptions({
            gfm: true,
            breaks: true,
            headerIds: true,
            mangle: false
        });

        const html = marked.parse(content);
        res.type('text/html').send(html);
    } catch (error) {
        console.error('Error rendering markdown:', error);
        res.status(404).json({ error: 'File not found' });
    }
});

// Start server
app.listen(PORT, () => {
    console.log(`\n🚀 Volumetric Display Server running!`);
    console.log(`\n📊 Main Simulator: http://localhost:${PORT}/`);
    console.log(`📚 Documentation Viewer: http://localhost:${PORT}/docs.html`);
    console.log(`\nPress Ctrl+C to stop\n`);
});
