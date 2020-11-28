module.exports = {
  purge: [
    './src/**/*.html',
    './src/**/*.jsx',
  ],
  theme: {
    extend: {},
    container: {
      center: true,
    }
  },
  variants: {
    cursor: ["responsive", "hover", "focus"]
  },
  plugins: [
    require('@tailwindcss/forms'),
  ]
};
