# Jekyll Conversion for 6-Pack of Care

This project has been converted from static HTML to Jekyll for better maintainability and template sharing.

## Structure

- `_config.yml` - Jekyll configuration
- `_layouts/` - Jekyll layout templates
  - `default.html` - Main layout for homepage and general pages
  - `chapter.html` - Layout for chapter pages
- `_includes/` - Reusable Jekyll includes (currently empty)
- `_sass/` - Sass stylesheets (currently empty)
- `_pages/` - Page collections (currently empty)

## Content Files

- `index.md` - English homepage (replaces `index.html`)
- `ch1.md` - English Chapter 1 (replaces `ch1.html`)
- `tw.md` - Chinese homepage (replaces `tw.html`)
- `tw1.md` - Chinese Chapter 1 (replaces `tw1.html`)

## Key Features

1. **Template Sharing**: Both English and Chinese pages now use shared layouts
2. **Markdown Source**: All content is now in Markdown with YAML front matter
3. **Language Switching**: Automatic language detection and switching
4. **Responsive Design**: Maintains all original styling and responsive features

## Front Matter Structure

Each markdown file includes:
- `layout`: Which Jekyll layout to use
- `title`: Page title
- `lang`: Language code (en/zh-tw)
- `header_title`: Title for the header section
- `subtitle`: Subtitle for the header
- `description`: Page description
- `manifesto_link`: Link to manifesto
- `manifesto_text`: Text for manifesto button
- `next_action`: Next action button configuration
- `alt_lang_url`: URL for alternate language version

## Building the Site

```bash
# Install dependencies
bundle install

# Build the site
bundle exec jekyll build

# Serve locally
bundle exec jekyll serve
```

## Original Files

The original HTML files (`index.html`, `ch1.html`, `tw.html`, `tw1.html`) are preserved for reference but can be removed once the Jekyll build is confirmed working.

## Benefits of Jekyll Conversion

1. **DRY Principle**: No more duplicated HTML structure
2. **Easy Maintenance**: Update layout once, changes everywhere
3. **Content Management**: Markdown is easier to edit than HTML
4. **GitHub Pages**: Native Jekyll support on GitHub Pages
5. **Scalability**: Easy to add new pages and languages
