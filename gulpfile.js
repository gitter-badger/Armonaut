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
var gulp = require('gulp');
var sass = require('gulp-sass');
var concat = require('gulp-concat');
var uglify = require('gulp-uglify');
var rename = require('gulp-rename');


gulp.task('sass', function () {
  return gulp.src('./armonaut/static/scss/**/*.scss')
    .pipe(sass({outputStyle: 'compressed'}).on('error', sass.logError))
    .pipe(concat('armonaut.css'))
    .pipe(gulp.dest('./armonaut/static/dist/css'));
});

gulp.task('uglify', function () {
  return gulp.src('./armonaut/static/js/**/*.js')
    .pipe(concat('armonaut.js'))
    .pipe(gulp.dest('./armonaut/static/dist/js'))
    .pipe(rename('armonaut.min.js'))
    .pipe(uglify())
    .pipe(gulp.dest('./armonaut/static/dist/js'));
});

gulp.task('watch', function () {
  gulp.watch('./armonaut/static/scss/**/*.scss', ['sass']);
  gulp.watch('./armonaut/static/js/**/.js', ['uglify']);
});

gulp.task('default', function () {
    gulp.start('sass', 'uglify');
});
