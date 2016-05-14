var gulp = require('gulp'),
    watch = require('gulp-watch'),
    autoprefixer = require('gulp-autoprefixer'),
    //concat = require('gulp-concat'),
    //sourcemaps = require('gulp-sourcemaps'),
    source = require('vinyl-source-stream'),
    browserSync = require("browser-sync"),
    cssmin = require('gulp-cssmin'),
    browserify = require('browserify'),
    sass = require('gulp-sass'),
    reload = browserSync.reload;


var path = {
    build: {
        fav: './client/build/',
        html: './client/build/',
        views: './client/build/views/',
        js: './client/build/js/',
        css: './client/build/css/',
        images: './client/build/images/',
        fonts: './client/build/fonts/',
        libs: './client/build/libs/'
    },
    src: {
        fav: './client/src/*.ico',
        html: './client/src/**/*.html',
        views: './client/src/views/**/*.html',
        js: './client/src/js/main.js',
        css: './client/src/scss/main.scss',
        images: './client/src/images/**/*.*',
        fonts: './client/src/fonts/**/*.*',
        bc: './bower_components/',
        nm: './node_modules/',
        test: './client/test/**/*.js'
    },
    watch: {
        html: './client/src/**/*.html',
        views: './client/src/views/**/*.html',
        js: './client/src/js/**/*.js',
        css: './client/src/scss/**/*.scss',
        images: './client/src/images/**/*.*',
        fonts: './client/src/fonts/**/*.*'
    },
    clean: './client/build'
};

gulp.task('html:build', function(){
    gulp.src(path.src.html)
        .pipe(gulp.dest(path.build.html))
});
gulp.task('images:build', function(){
    gulp.src(path.src.images)
        .pipe(gulp.dest(path.build.images))
        .pipe(browserSync.stream())
});

gulp.task('css:build', function () {
    gulp.src(path.src.css)
        .pipe(sass())
        .pipe(autoprefixer())
        .pipe(cssmin())
        .pipe(gulp.dest(path.build.css))
});

gulp.task('views:build', function(){
    gulp.src(path.src.views)
        .pipe(gulp.dest(path.build.views))
});

// gulp.task('fonts:build', function(){
//     gulp.src(path.src.bc+'font-awesome/fonts/**/*.*')
//         .pipe(gulp.dest(path.build.libs+'font-awesome/fonts'))
// });
// gulp.task('favicon:build', function(){
//     gulp.src(path.src.fav)
//         .pipe(gulp.dest(path.build.fav))
// });

gulp.task('libs:build', function(){
    // gulp.src(path.src.bc+'jquery/dist/jquery.min.js')
    //     .pipe(gulp.dest(path.build.libs+'jquery/'));

    // gulp.src(path.src.bc+'bootstrap-sass/assets/**/*.*')
    //     .pipe(gulp.dest(path.build.libs+'bootstrap/'));

    // gulp.src(path.src.bc+'angular-material/**/*.*')
    //     .pipe(gulp.dest(path.build.libs+'angular-material/'));
    
    // gulp.src(path.src.bc+'angular-ui-notification/dist/*.*')
    //     .pipe(gulp.dest(path.build.libs+'angular-ui-notification/'));

    // gulp.src(path.src.bc+'animate-sass/**/*.*')
    //     .pipe(gulp.dest(path.build.libs+'animate-sass/'));
      
    // gulp.src(path.src.bc+'material-design-fonticons/**/*.*')
    //     .pipe(gulp.dest(path.build.libs+'material-design-fonticons/'));

    // gulp.src(path.src.bc+'moment/**/*.*')
    //     .pipe(gulp.dest(path.build.libs+'moment/'));

    // gulp.src(path.src.bc+'normalize-css/normalize.css')
    //     .pipe(gulp.dest(path.build.libs+'normalize/'));

    // gulp.src(path.src.bc+'font-awesome/css/font-awesome.css')
    //     .pipe(gulp.dest(path.build.libs+'font-awesome/css'));
    


    gulp.src(path.src.nm+'angular/angular.min.js'
            // path.src.bc+'angular-animate/angular-animate.min.js',
            // path.src.bc+'angular-aria/angular-aria.min.js',
            // path.src.bc+'angular-messages/angular-messages.min.js',
            // path.src.bc+'angular-mocks/angular-mocks.min.js',
            // path.src.bc+'angular-moment/**/*.*',
            // path.src.bc+'angular-ui-router/release/angular-ui-router.min.js',
            // path.src.bc+'angular-ui-router/release/angular-ui-notification.min.js',
            // path.src.bc+'ng-file-upload/ng-file-upload.min.js',
            // path.src.bc+'ng-file-upload/ng-file-upload-shim.min.js'
          )
      // .pipe(concat('angular.concat.js'))
      .pipe(gulp.dest(path.build.libs+'angular/'));
});

gulp.task('browserify', function() {
    return browserify(path.src.js)
        .bundle()
        .pipe(source('bundle.js'))
        // .pipe(buffer())
        // .pipe(uglify())
        .pipe(gulp.dest(path.build.js));
});

gulp.task('webServer', function() {
    browserSync.init({
        server: "./client/build"
    });
    gulp.watch(path.watch.css, ['css:build']);
    gulp.watch(path.watch.html, ['html:build']);
    gulp.watch(path.watch.views, ['views:build']);
    gulp.watch(path.watch.js, ['browserify']);
    gulp.watch(path.watch.images, ['images:build']);
});

gulp.task('watch', function() {
    gulp.watch(path.watch.css, ['css:build']);
    gulp.watch(path.watch.html, ['html:build']);
    gulp.watch(path.watch.views, ['views:build']);
    gulp.watch(path.watch.js, ['browserify']);
    gulp.watch(path.watch.images, ['images:build']);
});




gulp.task('build', ['html:build', 'views:build', 'libs:build','images:build', 'browserify', 'css:build']);
gulp.task('default', ['build', 'webServer']);
//gulp.task('default', ['build', 'watch']);

