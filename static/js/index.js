// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        // Complete as you see fit.
        query: "",
        results: [],
        add_post_status: false,
        add_content: "",
        user: "",
        the_reviewer: -1,
        rows: [],
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.set_add_post = function (new_status) {
        app.vue.add_post_status = new_status;
    };

    app.search = function () {
        if (app.vue.query.length > 1) {
            axios.get(search_url, {params: {q: app.vue.query}})
                .then(function (result) {
                    app.vue.results = result.data.results;
                });
        } else {
            app.vue.results = [];
        }
    }

    app.add_post = function () {
        axios.post(add_post_url,
            {
                content: app.vue.add_content,
                //poster_id: app.vue.the_reviewer,
                //author: app.vue.author_name,
                reviewer: app.vue.the_reviewer,
            }).then(function (response) {
            app.vue.rows.push({
                id: response.data.id,
                content: app.vue.add_content,
                author: response.data.author,
                reviewer: app.vue.the_reviewer,
                owner: app.vue.user,
                rating: 0,
                num_stars_display: 0,
            })
            app.enumerate(app.vue.rows);
            app.reset_form();
            app.set_add_post(false);
        });
    };

    app.reset_form = function () {
        app.vue.add_content = "";
    };

    app.delete_post = function(row_idx) {
        let id = app.vue.rows[row_idx].id;
        axios.get(delete_post_url, {params: {id: id}}).then(function (response) {
            for (let i = 0; i < app.vue.rows.length; i++) {
                if (app.vue.rows[i].id === id) {
                    app.vue.rows.splice(i, 1);
                    app.enumerate(app.vue.rows);
                    break;
                }
            }
            });
    };

    app.complete = (rows) => {
        // Initializes useful fields of images.
        rows.map((rw) => {
            rw.rating = 0;
            rw.num_stars_display = 0;
        })
    };


    app.stars_over = (r_idx, num_stars) => {
        let rw = app.vue.rows[r_idx];
        if (rw.reviewer == app.vue.the_reviewer){
           rw.num_stars_display = num_stars;
        }
    };

    app.stars_out = (r_idx) => {
        let rw = app.vue.rows[r_idx];
        if (rw.reviewer == app.vue.the_reviewer){
           if (rw.rating > 0){
              rw.num_stars_display = rw.rating;
           }
           else{
              rw.num_stars_display = 0;
           }
        }
    };

    app.set_stars = (r_idx, num_stars) => {
        let rw = app.vue.rows[r_idx];
        if (rw.reviewer == app.vue.the_reviewer){
           rw.rating = num_stars;
           axios.post(set_rating_url, {post_id: rw.id, rating: rw.rating/*, poster_id: rw.poster_id*/});;
        }
    };



    // This contains all the methods.
    app.methods = {
        // Complete as you see fit.
        add_post: app.add_post,
        delete_post: app.delete_post,
        search: app.search,
        set_add_post: app.set_add_post,
        stars_over: app.stars_over,
        stars_out: app.stars_out,
        set_stars: app.set_stars,
    };

    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        // First we get the images.
        axios.get(my_callback_url)
            .then((result) => {
                // We set them
                let rows = result.data.rows;
                app.enumerate(rows);
                app.complete(rows);
                app.vue.user = result.data.user;
                app.vue.the_reviewer = result.data.the_reviewer;
                console.log(app.vue.the_reviewer)
                app.vue.rows = rows;
            })
            .then(() => {
                for (let r of app.vue.rows) {
                    axios.get(get_rating_url, {params: {"post_id": r.id}})
                        .then((result) => {
                            r.rating = result.data.rating;
                            r.num_stars_display = r.rating;
                            console.log(r);
                            //console.log(r.poster_id)
                        });
                }
            });
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);

var dropdown = document.querySelector('.dropdown');
    dropdown.addEventListener('click', function(event) {
        event.stopPropagation();
        dropdown.classList.toggle('is-active');
    });
