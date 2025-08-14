/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,ts,jsx,tsx}", // hoặc "app" tùy bạn đặt tên folder
  ],
  theme: {
    extend: {},
  },
  plugins: [
    require("tailwindcss-animate"), // thêm plugin animation
  ],
}
