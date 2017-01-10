var webpack = require('webpack');
var path    = require('path');
var config  = require('./webpack.config');


// Prevent Knockout comment bindings from getting stripped out
config.htmlLoader = {
  ignoreCustomFragments: [
    /<!--\s+\/?ko\s+/
  ]
}

config.plugins = config.plugins.concat([
  // Reduces bundles total size
  new webpack.optimize.UglifyJsPlugin({
    mangle: {
      // You can specify all variables that should not be mangled.
      // For example if your vendor dependency doesn't use modules
      // and relies on global variables. Most of angular modules relies on
      // angular global variable, so we should keep it unchanged
      except: ['$super', '$', 'exports', 'require', 'ko', 'jquery']
    }
  })
]);

module.exports = config;

