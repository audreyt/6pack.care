export default function (eleventyConfig) {
    // Passthrough copy for static assets
    eleventyConfig.addPassthroughCopy("img");
eleventyConfig.addPassthroughCopy("audio");
    eleventyConfig.addPassthroughCopy("styles.css");
    eleventyConfig.addPassthroughCopy("CNAME");

    eleventyConfig.addPassthroughCopy("favicon.ico");
    eleventyConfig.addPassthroughCopy(".nojekyll");

    // Filter for relative_url compatibility with Jekyll
    eleventyConfig.addFilter("relative_url", function (url) {
        // In 11ty, we can usually just return the URL as is if we're at the root,
        // or prepend a base URL if needed. For now, let's just return it.
        // If baseurl is set in site data, we could use it.
        return url;
    });

    // Date filter
    eleventyConfig.addFilter("date", function (date, format) {
        // Basic date formatting - can be improved with luxon if needed
        // For now, just return the date string or use a simple formatter
        // This is a placeholder for the Jekyll date filter
        if (!date) return "";
        const d = new Date(date);
        // Very basic mapping for the formats used in the templates
        // "%B %-d, %Y" -> Month Day, Year
        // "%Y 年 %-m 月 %-d 日" -> Year 年 Month 月 Day 日

        if (format.includes("%B")) {
            return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
        }
        if (format.includes("年")) {
            return `${d.getFullYear()} 年 ${d.getMonth() + 1} 月 ${d.getDate()} 日`;
        }
        return d.toDateString();
    });

    return {
        dir: {
            input: ".",
            output: "docs",
            layouts: "_layouts"
        },
        templateFormats: ["html", "md", "liquid"],
        markdownTemplateEngine: "liquid",
        htmlTemplateEngine: "liquid"
    };
};
