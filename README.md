# curso-web-backend
Repositorio para el Curso de Web Backend de Computer Society ITBA. Continene las diferentes clases del curso y el material necesario.

### Structure

There are 4 main folders in this repository:
- `_layouts` --> Here you can find the available layouts used by `Jekyll`, currently there is only the `default.html` file used by all pages.
- `assets` --> Here you can find stylesheets for the layouts, the themes import the `assets/css/style.scss` by default (DO NOT CHANGE THE NAME, but you can import other scss files). Every declaration in this file must go after:
    ```scss
    ---
    ---

    @import "{{ site.theme }}";

    // DECLARE HERE
    ```
- `clases` --> Here you can find the main files for all the content in the course. It is subdivided into 3 parts:
    + `bases` --> These are ZIP files we can provide people at the beginning of each class in case they couldn't complete the previous class.
    + `resources` --> These are mainly images used in the different classes, referenced by the `.md` files.
    + `clase-` files --> These are the contents of the different classes. There are 4 main classes, a class containing only the requests used, and a class for setup. The `.md` files are converted to HTML by `Jekyll`, and they must have a special header in the first lines of the file:
        ```
        ---
        layout: default
        title:  "Clase 1"
        description: "Clase 1 - Teoría de APIs REST e inicialización del Proyecto"
        principal: false
        ---
        ```
        This headers must contain a `layout` (specifies the layout from `_layouts` to be used), `title` (it's the title shown in the banner), `description` (subtitle shown in the banner), and `principal` (boolean, indicates whether or not the page is the main page in order to show the "Go to Github" button).
- `source` --> Source code for each class, it contains the API of each completed class.

The `index.md` file is the main page file that's shown in the website.

### Resources

Here are some resources useful to building the content and structure:
- [Spell Checking](https://languagetool.org/)
- [Generating Table of Contents](https://ecotrust-canada.github.io/markdown-toc/)
- [Implementing Google Analytics](https://github.com/dwyl/learn-google-analytics)

### Authors

Content and Layout: Gonzalo Hirsch
