/**
 * @type {import('gatsby').GatsbyConfig}
 */
module.exports = {
  siteMetadata: {
    title: `Fantasy Forecaster`,
    siteUrl: `https://www.yourdomain.tld`
  },
  plugins: [
    "gatsby-plugin-styled-components",
    {
      resolve: `gatsby-plugin-manifest`,
      options: {
        name: "Fantasy Forecaster",
        short_name: "Fantasy Forecaster",
        start_url: "/",
        background_color: "#0D830F",
        theme_color: "#000000",
        display: "standalone",
        icon: "src/images/icon.png",
      },
    },
  ]
};