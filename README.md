# ecom
By: Brendan Teo, Vipul Gupta, Eric Mar


IMPORTANT INSTRUCTIONS FOR TAs: 

-Note that for CSE 183, we are submitting our py4web zipped file as our submission in the Google form, as we were not able to upload to the cloud. Download and use this zip file from the google form we will submit, as its database is prepopulated with two users and ten specific ebook entries with their own unique information per ebook. Here are some important steps for the TAs for running this project in their own py4web server to test out the site with the zip file that will be submitted in the Google form:

1. Download the zip file

2. Open it and place it in the py4web apps folder.

3. EXTREMELY IMPORTANT: type the command "pip install stripe" in the directory of this project folder. It might not matter where you put the command, as long as you install stripe entering this command in your terminal. 

4. Reload py4web in your editor, or terminal. 

5. go to the url using the project name and the py4web server, and the site should appear to the login page, where you can login and test the site.

*Emphasis on installing stripe using "pip install stripe", this is so the transaction function works. If you do not do this, simply trying to access the site will give you a 404 not found error.




This project is an ebook ecommerce site, from which users can make purchases for selected ebooks. This website was developed using the py4web server, with the back end being in python using sqlite for the databases, and the front end using html and javascript.


The main pages featured on this site are a home page, an index/browsing page, a shopping cart page, a wishlist page, and an info page for each ebook. There is also a purchase button that takes the user to a transaction page that is from the Stripe API.


Important features of our website using vue: 

1. The search bar uses vue, and will show suggested titles from the database based on the substring entered in the search bar. Clicking on the title will redirect to the ebook's specific info page.

2. The review and ratings system works so that the site can have general reviews and ratings on the home page and each individual ebook's reviews and ratings show up on its own specific info page. This info page with display the correct info based on ebook clicked on or title searched for in the search bar. The full review can be deleted by the user who submits the review and the rating is only editable by the user who submitted the rating. All ratings and review are visible to all users.

3. The purchase button uses the Stripe API in order to conduct a transaction for buying ebooks. The shopping cart is cleared once a transaction is complete. Only Stripe testing credit card numbers can be used currently, because the transaction is in testing mode currently. Here is a link to testing credit cards that can be used in the stripe page: https://stripe.com/docs/testing


Overall, our goal was to build an ebook ecommerce website and we feel like we have created something that very closely resembles that with this py4web site. 


Useful Resources: Unit 15, 17, 20, and doing hw5 for the CSE 183 class at UCSC really helped us implement a lot of the major pieces of our site. We stated with starter code from this class and built our pages from there. The starter code basically allows users to log in and create profiles. 


Testing: Testing for this project was done on mac and windows, using the py4web server and the browsers Firefox, Google Chrome, and Microsoft edge.



Work Allocation:
Eric: Front end
Brendan: Back end
Vipul: Back end  
