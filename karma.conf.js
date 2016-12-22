/**
 * Karma runner default confiruation
 *
 * More options available at:
 *    http://karma-runner.github.io/1.0/config/configuration-file.html
 */

'use strict';

var path = require('path');

module.exports = function (config) {
  config.set({

    // Run once by default
    singleRun: true,

    plugins: [
      require('karma-chai'),
      require('karma-coverage'),
      require('karma-mocha'),
      require('karma-mocha-reporter'),
      require('karma-phantomjs-launcher'),
      require('karma-sinon'),
      require('karma-sourcemap-loader'),
      require('karma-webpack')
    ],

    // We will be testing against these browsers
    browsers: ['PhantomJS'],

    // Framworks to load in testing enviroment
    frameworks: ['mocha', 'chai', 'sinon'],

    // How to report test results
    reporters: ['mocha', 'coverage'],

    // "coverage" plugin configuration
    coverageReporter: {
      dir: 'coverage/',
      includeAllSources: true,
      reporters: [
        {type: 'lcov', subdir: '.'},
        {type: 'text-summary'},
        {type: 'text'}
      ]
    },

    // list of files/patterns to load in browser
    files: ['client/**/*.spec.js'],

    // preprocess files before serving
    preprocessors: {'client/**/*.spec.js': ['webpack']},

    // prevent webpack from spamming console
    webpackServer: { noInfo: true },

    // These settigns should be similar thos those in webpack.conf.js
    webpack: {
      resolve: {
        alias: {
          'jquery': 'jquery/src/jquery'
        },
        root: [path.resolve(__dirname, './client')] // Set application root
      },
      module: {
        // Ensure that coverage reports non-transpiled source files
        preLoaders: [
          { test: /\.js$/, loader: 'isparta', include: path.join(__dirname, 'client/') }
        ],
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
    }
  });
};
