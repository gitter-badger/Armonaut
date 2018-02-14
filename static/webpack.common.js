/* Copyright 2018 Seth Michael Larson
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

const path = require('path');

const config = {
    entry: path.resolve(__dirname, 'js/index.js'),
    output: {
        filename: 'armonaut.bundle.js',
        path: path.resolve(__dirname, 'dist')
    },
    resolve: {
        extensions: ['.js', '.css', '.scss']
    },
    module: {
        rules: [{
            test: /\.jsx?/,
            exclude: /node_modules/,
            use: 'babel-loader'
        }, {
            test: /\.s*css/,
            exclude: /node_modules/,
            use: [
                'style-loader',
                'css-loader',
                'sass-loader'
            ]
        }]
    }
};

module.exports = config;
