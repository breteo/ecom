// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
    };

    app.pay = function () {
        // When one clicks pay, this contacts the server, to store the fulfillment
        // information and get a Stripe session id, and then redirects to Stripe.
        axios.post(pay_url, {
        }).then(function (r) {
                // The server says: ok, the transaction can be performed.
                let stripe_session_id = r.data.session_id;
                stripe = Stripe(stripe_key);
                stripe.redirectToCheckout({
                    sessionId: stripe_session_id,
                }).then(function (result) {
                    Q.flash(result.error.message);
                });
        });
    };

    // This contains all the methods.
    app.methods = {
        pay: app.pay,
        // Complete as you see fit.
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
    };

    // Call to the initializer.
    app.init();
};

// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);
