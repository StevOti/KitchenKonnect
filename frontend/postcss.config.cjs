// Use the new PostCSS adapter for Tailwind. Install with:
// npm install -D @tailwindcss/postcss
module.exports = {
  plugins: [
    require('@tailwindcss/postcss'),
    require('autoprefixer'),
  ],
}
