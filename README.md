WatchHouse

This is the ecommerce platform for the buying of the watches sorry because of database problem I was not unable to upload into remder or other webpage.

Here i used the django framework from python to implement this and make it workable.
This has got the features of creating the account, logging in.out, adding to the cart, contact to the user


For the db, i have provide the csv filefor db
use web_brand: brand_id(PK), brand_name
use web_type: type_id(PK), type_name
use web_gender: gender_id(PK), gender_name
use web_watch: id(PK, AI), title, brand_id, image_url, price, type_id, gender_id
use auth_user: id(int AI PK ),password,last_login,is_superuser,username,first_name,last_name,email,is_staff,is_active,date_joined
