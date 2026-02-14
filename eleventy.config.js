import htmlmin from "html-minifier";

export default function (eleventyConfig) {
    // Passthrough copy for static assets
    eleventyConfig.addPassthroughCopy("img");
    eleventyConfig.addPassthroughCopy("audio");
    eleventyConfig.addPassthroughCopy("styles.css");
    eleventyConfig.addPassthroughCopy("CNAME");

    eleventyConfig.addPassthroughCopy("favicon.ico");
    eleventyConfig.addPassthroughCopy(".nojekyll");

    // Minify HTML
    eleventyConfig.addTransform("htmlmin", function (content) {
        if ((this.page.outputPath || "").endsWith(".html")) {
            let minified = htmlmin.minify(content, {
                useShortDoctype: true,
                removeComments: true,
                collapseWhitespace: true,
            });
            return minified;
        }
        return content;
    });

    // Filter for relative_url compatibility with Jekyll
    eleventyConfig.addFilter("relative_url", function (url) {
        if (typeof url !== "string" || !url.length) {
            return "";
        }
        return url;
    });

    // Date filter
    eleventyConfig.addFilter("date", function (date, format) {
        // Date filter supporting Jekyll-style format strings
        if (!date) return "";
        if (typeof format !== "string") {
            return new Date(date).toLocaleDateString("en-US");
        }

        const d = new Date(date);
        // Very basic mapping for the formats used in the templates
        // "%B %-d, %Y" -> Month Day, Year
        // "%Y 年 %-m 月 %-d 日" -> Year 年 Month 月 Day 日

        if (format.includes("%B")) {
            return d.toLocaleDateString("en-US", {
                year: "numeric",
                month: "long",
                day: "numeric",
            });
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
            layouts: "_layouts",
        },
        templateFormats: ["html", "md", "liquid", "njk"],
        markdownTemplateEngine: "liquid",
        htmlTemplateEngine: "liquid",
    };
}
