// Load configuration from environment or config file
const path = require('path');
const TerserPlugin = require('terser-webpack-plugin');
const CompressionPlugin = require('compression-webpack-plugin');

// Environment variable overrides
const config = {
  disableHotReload: process.env.DISABLE_HOT_RELOAD === 'true',
};

module.exports = {
  webpack: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
    configure: (webpackConfig, { env }) => {
      
      // Production optimizations
      if (env === 'production') {
        // Optimize bundle splitting
        webpackConfig.optimization.splitChunks = {
          chunks: 'all',
          cacheGroups: {
            default: false,
            vendors: false,
            // Vendor chunk for node_modules
            vendor: {
              name: 'vendor',
              chunks: 'all',
              test: /node_modules/,
              priority: 20,
              // Only include vendors that are actually used
              reuseExistingChunk: true,
            },
            // Common chunk for code shared between 2+ chunks
            common: {
              name: 'common',
              minChunks: 2,
              chunks: 'all',
              priority: 10,
              reuseExistingChunk: true,
              enforce: true
            },
            // Separate chunk for React and related libraries
            react: {
              name: 'react',
              chunks: 'all',
              test: /[\\/]node_modules[\\/](react|react-dom|react-router|react-router-dom)[\\/]/,
              priority: 30,
              reuseExistingChunk: true,
            },
            // Separate chunk for UI libraries
            ui: {
              name: 'ui',
              chunks: 'all',
              test: /[\\/]node_modules[\\/](@radix-ui|lucide-react|class-variance-authority|clsx|tailwind-merge)[\\/]/,
              priority: 25,
              reuseExistingChunk: true,
            }
          }
        };
        
        // Enhanced minification
        webpackConfig.optimization.minimizer = [
          new TerserPlugin({
            terserOptions: {
              parse: { ecma: 8 },
              compress: {
                ecma: 5,
                warnings: false,
                inline: 2,
                drop_console: true, // Remove console logs in production
                drop_debugger: true,
                pure_funcs: ['console.log', 'console.info'] // Remove specific function calls
              },
              mangle: { safari10: true },
              output: {
                ecma: 5,
                comments: false,
                ascii_only: true
              }
            }
          })
        ];
        
        // Gzip compression for better transfer size
        webpackConfig.plugins.push(
          new CompressionPlugin({
            algorithm: 'gzip',
            test: /\.(js|css|html|svg)$/,
            threshold: 8192,
            minRatio: 0.8
          })
        );
      }
      
      // Disable hot reload completely if environment variable is set
      if (config.disableHotReload) {
        // Remove hot reload related plugins
        webpackConfig.plugins = webpackConfig.plugins.filter(plugin => {
          return !(plugin.constructor.name === 'HotModuleReplacementPlugin');
        });
        
        // Disable watch mode
        webpackConfig.watch = false;
        webpackConfig.watchOptions = {
          ignored: /.*/, // Ignore all files
        };
      } else {
        // Add ignored patterns to reduce watched directories
        webpackConfig.watchOptions = {
          ...webpackConfig.watchOptions,
          ignored: [
            '**/node_modules/**',
            '**/.git/**',
            '**/build/**',
            '**/dist/**',
            '**/coverage/**',
            '**/public/**',
          ],
        };
      }
      
      return webpackConfig;
    },
  },
};