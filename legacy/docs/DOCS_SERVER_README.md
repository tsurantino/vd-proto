# Documentation Server

A simple Node.js server for viewing markdown documentation with rich formatting support.

## Features

- 📚 **Auto-discovery**: Automatically finds all `.md` files in the project
- 🎨 **Rich Formatting**: Full markdown support with syntax highlighting
- 📂 **Organized by Category**: Groups docs by directory (Documentation, TouchDesigner, etc.)
- 🌙 **Dark Theme**: Easy-on-the-eyes dark interface
- ⚡ **Fast & Simple**: Lightweight Express server

## Quick Start

### 1. Install Dependencies

```bash
npm install
```

This will install:
- `express` - Web server framework
- `marked` - Markdown parser

### 2. Start the Server

```bash
npm start
```

Or for development:

```bash
npm run dev
```

### 3. Open in Browser

The server will start on port 8000. You'll see:

```
🚀 Volumetric Display Server running!

📊 Main Simulator: http://localhost:8000/
📚 Documentation Viewer: http://localhost:8000/docs.html

Press Ctrl+C to stop
```

## Available Endpoints

### Web Pages

- **`/`** - Main volumetric display simulator (index.html)
- **`/docs.html`** - Documentation viewer with sidebar navigation

### API Endpoints

- **`GET /api/docs`** - List all available markdown files
  - Returns JSON array of documents with metadata

- **`GET /api/docs/raw/:path`** - Get raw markdown content
  - Example: `/api/docs/raw/README.md`
  - Returns plain text markdown

- **`GET /api/docs/html/:path`** - Get rendered HTML
  - Example: `/api/docs/html/HYBRID_MORPH_SPEC.md`
  - Returns rendered HTML from markdown

## Supported Markdown Features

The documentation viewer supports all standard markdown features:

### Text Formatting
- **Bold**, *italic*, ~~strikethrough~~
- `inline code`
- [Links](https://example.com)

### Code Blocks
```javascript
// Syntax highlighting
const example = "Hello World";
```

### Lists
- Bullet lists
- Numbered lists
- Nested lists

### Tables

| Feature | Status |
|---------|--------|
| Markdown | ✅ |
| Syntax Highlighting | ✅ |
| Auto-discovery | ✅ |

### Headings
# H1 through H6

### Blockquotes
> Important information

### Horizontal Rules
---

## Directory Structure

The server automatically scans these locations:

```
vd-proto/
├── *.md                    # Root markdown files (Documentation category)
└── td/
    └── *.md               # TouchDesigner docs (TouchDesigner category)
```

## Current Documentation

After running the server, the following docs will be available:

### Documentation Category
- **README** - Project overview
- **NEW_FEATURES** - Recent feature additions
- **HYBRID_MORPH_SPEC** - Unified particle system specification

### TouchDesigner Category
- **TOUCHDESIGNER_IMPLEMENTATION** - POPs implementation guide
- **TOUCHDESIGNER_COLOR_EFFECTS** - GLSL shaders and color effects

## Customization

### Adding New Categories

To add new documentation categories, modify `server.js`:

```javascript
// Add a new directory scan
const customPath = path.join(__dirname, 'your-directory');
try {
    const customFiles = await fs.readdir(customPath);
    for (const file of customFiles) {
        if (file.endsWith('.md')) {
            // ... add to docs array with category: 'Your Category'
        }
    }
} catch (err) {
    console.log('Custom directory not found');
}
```

### Styling

Edit `docs.html` to customize:
- Colors (CSS variables in `<style>` section)
- Layout (modify `.sidebar` and `.content` styles)
- Markdown rendering (modify `.markdown-content` styles)

### Markdown Parser Options

Modify `marked` options in `server.js`:

```javascript
marked.setOptions({
    gfm: true,              // GitHub Flavored Markdown
    breaks: true,           // Convert \n to <br>
    headerIds: true,        // Add IDs to headings
    mangle: false,          // Don't mangle email addresses
    smartLists: true,       // Smart list behavior
    smartypants: true       // Smart quotes/dashes
});
```

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, set a custom port:

```bash
PORT=3000 npm start
```

### Dependencies Not Installing

Make sure you have Node.js installed (v16 or higher):

```bash
node --version
npm --version
```

If issues persist, try:

```bash
rm -rf node_modules package-lock.json
npm install
```

### Markdown Not Rendering

Check the browser console for errors. Common issues:
- File path typo in the URL
- File permissions (server can't read the file)
- Invalid markdown syntax

### Files Not Appearing in Sidebar

Ensure:
- Files have `.md` extension
- Files are in root directory or `td/` subdirectory
- Server has read permissions for the directory

## Development

### Project Structure

```
vd-proto/
├── server.js              # Express server with API endpoints
├── docs.html             # Documentation viewer UI
├── package.json          # Dependencies and scripts
├── *.md                  # Markdown documentation files
└── td/
    └── *.md             # TouchDesigner documentation
```

### Adding New Features

The codebase is simple and modular:

1. **Server API** (`server.js`) - Add new endpoints here
2. **UI** (`docs.html`) - Modify the viewer interface
3. **Styling** - All CSS is inline in `docs.html` for simplicity

## License

MIT

---

**Tip**: Keep this server running while working on documentation. The viewer auto-refreshes when you select a document, so you can edit markdown files and immediately see changes by re-selecting the file in the sidebar.
