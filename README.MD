README

tweete project

-tweet app
-account app

-tweet app
--->  it contains tweet related files.

-models.py 
--->  it contains all class which creates table in database related tweet, like, comment, follow and others

-serializers.py
--->  it serializes data (converts queryset or complex data into JSON data) while performing GET request and desrializes data (converts JSON data into python object type data) while performing 	CREATE and UPDATE operation.

	1. TweetCreateSerializer :- it serializes user submitted tweet data and validated tweet content to 200 character only.
	
	2. ReplySerializer :- it serializes reply content submitted by user.

	3. CommentSerializer :- it serializes comment content submitted by user.

	4. TweetSerializer :- it serializes all tweet related data.

	5. TweetListSerializer :- it serializes list of all tweet data.

	6. TweetActionSerializer :- it serializes data given for like, dislike and retweet.

	

-views.py
--->  it is responsible for performing business logic and all business logic is written here.
--->  it imports different classes from different files.
	-here api view is used to see browsable api.
	-different permission classes are used in order to control user accessing some actions.

	1. TweetDetailAPIView :- it is used to get data of single tweet and perfom CRUD operation on it.

	2. TweetCreateView :- logic is wrriten here to create tweet.

	3. tweet_feed_view :- it lists all tweets of login user and those user who followed him.
	
	4. tweet_list_view :- it lists out all tweets.

	5. tweet_like_view :- it handle all activity related like, dislike and retweet. the action of liking, unliking and retweeting entered by user would serialize in TweetActionSerializer 				      and the will be checked for validation. if data will be valid all data passed will be accessed and then tweet of corresponding id would be found from database. 
			      if it will exist and action will be liking then the like will be add and that data will be serialized. if action will be of disliking, the user will be removed, 				      and if action will be of retweeting, then that tweet will be added with parent as tweet_id passed by user.then that tweet will be serialized and corresponding 				      response will be sent.

	6. CommentView :- comment content is created and retrived from here.

	7. ReplyView :- reply content passed by user will be serialized and if it is valid then comment related to that reply will be retrived from database and according to that comment 				id new reply will be created and after serializing it the response will be sent.

	8. user_follow_view :- according to action of following or unfollowing it will follow or unfollow user profile.
 						


-urls.py
--->  it contains all urls of different operaions and api end points.

-settings.py 
--->  it has all project related settings which controlls project's all setting.

-admin.py 
--->  it is project's admin related stuff. we can perfom all operation(CRUD) related to our project here.


-account app 
--->  it contains user related stuff, like login, logout, sign up, password reset and all that.

-serializers.py
--->  it contains UserCreateSerializer, UserLoginSerializer,PasswrodResetSerializer, SetNewPasswordSerializer.
	1. UserCreateSerializer	:- it serializes data given by user.
				  -validate method will validate email and if email already exists it would return some response.
				  -create method will create user and set its password.

	2. UserLoginSerializer :- it serializes login data given by user and its validate method checks data in database and return user.

	3. PasswrodResetSerializer :- it serializes email sent by user.

	4. SetNewPasswordSerializer :- it serializes new given password, decode uidb54 and get user related that uidb64 from database and then check that user's token in database, if token is 					not valid it raises error otherwise it set new password and save user.

-views.py
--->  it contains business logic for user login, logout, sign up, password reset and all that.

	1. UserCreateApiView :- it contains logic related to user creation.

	2. UserLoginApiView :- it contains logic related to user login.

	3. PasswrodResetAPIView :- when user submits email to reset password. it checks that email. if exists, it retrive that user from databse then encode user id.
				   now we need to send a token, so we have to generate user related token. django.contrib.auth.token has PasswordResetTokenGenerator() which has a method called 
				   make_token(user) which generate token related to user passed in and store token in database.then we make url which redirect user to password reset page. this 					   url contains token and encoded id of user.then using send mail function, we send email to user.

	4. PasswordTokenCheckAPIView :- it takes encoded user id and token as get request which is hit when user click on password reset link send to then via email.encoded user id is decoded 					here.then using that id user is fetched from database.django.contrib.auth.token has PasswordResetTokenGenerator() which has a method called 						check_token(user,token) which checks the token given by user is associated to that user saved in database or not. if it is, then it will return success 					response with uidb64 and token.

	5. SetNewPasswordAPIView :- it uses patch method, takes new password submitted by user and then in serializer, it serializes that password, decode encoded user id and then using 					    check_token method it check that token, if valid, it fetches that user and set its password in database using set_password method then save that user.




