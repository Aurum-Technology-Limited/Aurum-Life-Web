/**
 * Babel Configuration for Aurum Life Test Environment
 */

module.exports = {
  presets: [
    ['@babel/preset-env', {
      targets: {
        node: 'current',
      },
    }],
    ['@babel/preset-react', {
      runtime: 'automatic',
    }],
    '@babel/preset-typescript',
  ],
  plugins: [
    // Add any additional plugins if needed
  ],
  env: {
    test: {
      presets: [
        ['@babel/preset-env', {
          targets: {
            node: 'current',
          },
        }],
        ['@babel/preset-react', {
          runtime: 'automatic',
        }],
        '@babel/preset-typescript',
      ],
    },
  },
};