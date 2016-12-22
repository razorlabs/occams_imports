'use strict';

var path              = require('path');
var webpack           = require('webpack');

module.exports = {
  devtool: 'source-map',
  entry: [
    'babel-polyfill',
    path.join(__dirname, 'client/app.js')
  ],
  resolve: {
    alias: {
      // Configure how jQuery is bundled
      'jquery': 'jquery/src/jquery'
    },
    root: [ path.resolve(__dirname, './client') ] // Set module root
  },
  output: {
    filename: '[name].bundle.js',
    publicPath: '/imports/static/',
    // Serve form pyramid's static directory
    path: path.resolve(__dirname, 'occams_imports/static')
  },
  module: {
    loaders: [
       { test: /\.js$/, exclude: [/node_modules/], loader: 'babel' },
       { test: /\.html$/, loader: 'html' },
       { test: /\.scss$/, loader: 'style!css!resolve-url!sass' },
       { test: /\.css$/, loader: 'style!css!resolve-url' },
       { test: /\.(png|gif)$/, loader: 'url?limit=100000' },
       { test: /\.woff(2)?(\?v=\d+\.\d+\.\d+)?$/, loader: "url?limit=10000&mimetype=application/font-woff" },
       { test: /\.ttf(\?v=\d+\.\d+\.\d+)?$/, loader: "url?limit=10000&mimetype=application/octet-stream" },
       { test: /\.eot(\?v=\d+\.\d+\.\d+)?$/, loader: "file" },
       { test: /\.svg(\?v=\d+\.\d+\.\d+)?$/, loader: "url?limit=10000&mimetype=image/svg+xml" },
    ]
  },
  plugins: [
    // Automatically move all modules defined outside of application directory to vendor bundle.
    // If you are using more complicated project structure, consider to specify common chunks manually.
    new webpack.optimize.CommonsChunkPlugin({
      name: 'vendor',
      minChunks: function (module, count) {
        return module.resource && module.resource.indexOf(path.resolve(__dirname, 'client')) === -1;
      }
    })
  ],
};
