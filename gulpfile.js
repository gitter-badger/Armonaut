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
