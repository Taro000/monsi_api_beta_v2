# MONSI API Beta V2  
## ER図
![Monsi_Django_Models_for_Betaのコピー](https://user-images.githubusercontent.com/30229356/86890987-17835100-c139-11ea-83e5-380a88cfa54f.png)
## UI
### カスタマーApp
<img width="504" alt="スクリーンショット 2020-07-08 16 29 25" src="https://user-images.githubusercontent.com/30229356/86891056-2ec23e80-c139-11ea-9c53-4a467333bd9a.png">  

### スタイリストApp
<img width="662" alt="スクリーンショット 2020-07-08 16 29 13" src="https://user-images.githubusercontent.com/30229356/86891105-40a3e180-c139-11ea-8e8f-a8d3b97562bb.png">

## API
### Stylist-Beta  API

#### ＜エンドポイント一覧 - List of Endpoint＞
ホーム(Home)　/api.stylist.beta/home/<username>
B/A写真(Edit B/A photos)　/api.stylist.beta/edit-catalogs/<username>
スケジュール管理(Manage Schedule)　/api.stylist.beta/schedule/<username>?year=●●&month=●●&day=●●
———
名前とメアドの変更(Change name and email address)　/api.stylist.beta/users/<username>    # Djangoのモデル上の制約
パスワードの変更(Change Password)　/api.stylist.beta/password-fresh/<username>
メニューを追加(Add a menu)　/api.stylist.beta/menus
メニューを編集・削除(Edit/Delete a menu)　 /api.stylist.beta/menus/<uuid>
B/A写真を追加(Add a B/A photo)　/api.stylist.beta/catalogs
B/A写真を編集・削除(Edit/Delete a B/A photo)　/api.stylist.beta/catalogs/<uuid>
予約を追加(Add a reservation)　/api.customer.beta/reserve-and-history/
予約を編集・削除(Edit/Delete a reservation)　/api.customer.beta/reserve-and-history/<uuid>
———
ユーザー登録(Register)　/api.stylist.beta/register
トークン発行(ログイン)(Generate a Token—Login)   /api.stylist.beta/auth-token



#### ＜エンドポイント別データ一覧 - List of data on each Endpoint＞
[] はその中の内容でリスト形式を作るという意味
[] means List which is made with data in [].

ホーム(Home)
/api.stylist.beta/home/<username>  (GET, PUT)
GET
@first_name
@last_name
@img
@year
@phone_number
@rate_average
@menus[
	@menu_name
	@menu_img
	@price
	@time
	@api
]
@salon_name
@place
@access
@salon_img
@next_api[
	@/api.stylist.beta/edit-catalogs/<username>
	@/api.stylist.beta/schedule/<username>
	@/api.stylist.beta/menus
	@/api.stylist.beta/users/<username>
	@/api.stylist.beta/password-fresh/<username>
]

PUT
@img
@year
@phone_number
@salon_name
@place
@access
@salon_img


名前とメアドの変更(Change name and email address)
/api.stylist.beta/users/<username>  (PUT)
PUT
@last_name
@first_name
@email


パスワードの変更(Change Password)
/api.stylist.beta/users/<username>  (PUT)
PUT
@old_password
@new_password


メニューの追加(Add a new menu)
/api.stylist.beta/menus   (POST)
POST
@menu_name
@price
@time
@img
@color        #Bool data which color or an another(True=Color, False=Damage hair)


メニューの変更・削除(Edit a menu)
/api.stylist.beta/menus/<uuid>  (PuT, DELETE)
PUT
@menu_name
@price
@time
@img
@color        #Bool data which color or an another(True=Color, False=Damage hair)

DELETE


B/A写真(Edit B/A photos)
/api.stylist.beta/edit-catalogs/<username>  (GET)
GET
@catalogs[
	@before_img
	@after_img
	@menu
	@year
	@male
	@api
]
@next_api[
	@/api.stylist.beta/home/<username>
	@/api.stylist.beta/schedule/<username>
	@/api.stylist.beta/catalogs
]


B/A写真の追加(Add a B/A photo)
/api.stylist.beta/catalogs   (POST)
POST
@before_img
@after_img
@menu
@year
@male            #Bool data which Male or an another(True=Male, False=Female)


B/A写真の編集・削除(Edit/Delete a B/A photo)
/api.stylist.beta/catalogs/<uuid>   (PUT, DELETE)
PUT
@before_img
@after_img
@menu
@year
@male            #Bool data which Male or an another(True=Male, False=Female)

DELETE


スケジュール(Manage Schedule)
/api.stylist.beta/schedule/<username>?year=●●&month=●●&day=●●  (GET)
GET
@reserves[
	@menu_name
	@price
	@customer_name
	@datetime
	@place
	@phone
	@api
]
@<Some data for Reservation system which Roman made.>
@next_api[
	@/api.stylist.beta/home/<username>
	@/api.stylist.beta/edit-catalogs/<username>
	@/api.stylist.beta/reserve-and-history
	@/api.stylist.beta/<URI to a resource for Reservation system which Roman made.>       # To make an Un-Reserved space.
	@/api.stylist.beta/catalogs
]


予約の追加(Add a Reservstion)
/api.stylist.beta/reserve-and-history   (POST)
POST
@menu
@datetime


予約を編集する・キャンセルする(Edit/Cancel a Reservation)
/api.customer.beta/reserve-and-history/<uuid>  (PUT, DELETE)
PUT
@menu
@datetime

DELETE


ユーザー登録(Register)
/api.stylist.beta/register   (POST)
POST
@username
@email
@password


トークン発行(ログイン)(Generate Token—Login)
/api.stylist.beta/auth-token  (POST)
POST
@username
@password


### Customer-Beta  API

#### ＜エンドポイント一覧 - List of Endpoint＞
ホーム(未ログイン)(Home—not logged in)　/api.customer.beta/home/
———
ホーム(Home)　/api.customer.beta/home/<username>
予約確認(Check Reserves)　/api.customer.beta/reserves/<username>
予約履歴(Reservation Logs)　/api.customer.beta/logs/<username>
ユーザー設定(User Setting)　/api.customer.beta/setting/<username>
———
名前とメアドの変更(Change name and email address)　/api.customer.beta/users/<username>    # Djangoのモデル上の制約
パスワードの変更(Change Password)　/api.customer.beta/password-fresh/<username>
予約(Make a Reservation)　/api.customer.beta/reserve-and-history
———
ユーザー登録(Register)　/api.customer.beta/register
トークン発行(ログイン)(Generate a Token—Login)   /api.customer.beta/auth-token



#### ＜エンドポイント別データ一覧 - List of data on each Endpoint＞
[] はその中の内容でリスト形式を作るという意味
[] means List which is made with data in [].

ホーム(Home)
/api.customer.beta/home  (GET)
GET
@catalogs[
	@before_img
	@after_img
	@stylist_name
	@rate_average
	@year
	@menus[
		@menu_name
		@img
		@price
		@time
	]
	@salon_name
	@place
	@access
	@salon_img
]
@next_api[
	@/api.customer.beta/register
]

/api.customer.beta/home/<username>  (GET)
GET
@catalogs[
	@before_img
	@after_img
	@stylist_name
	@rate_average
	@year
	@menus[
		@menu_name
		@img
		@price
		@time
	]
	@salon_name
	@place
	@access
	@salon_img
]
@next_api[
	@/api.customer.beta/reserves/<username>
	@/api.customer.beta/logs/<username>
	@/api.customer.beta/setting/<username>
	＠/api.customer.beta/reserve-and-history
]


予約する(Make a Reservation)
/api.customer.beta/reserve-and-history  (POST)
POST
@menu
@datetime


予約確認(Check Reserves)
/api.customer.beta/reserves/<username>  (GET)
GET
@stylist_name
@menu_name
@proce
@time(何時 - 何時)
@place
@phone_number
@next_api[
	@/api.customer.beta/home/<username>
	@/api.customer.beta/logs/<username>
	@/api.customer.beta/setting/<username>
	@/api.customer.beta/reserve-and-history/<uuid>        #予約キャンセル用
]


予約をキャンセルする(Cancel a Reservation)
/api.customer.beta/reserve-and-history/<uuid>  (DELETE)
DELETE


予約履歴(Reservation Logs)
/api.customer.beta/logs/<username>  (GET)
GET
@logs[
	@stylist_name
	@rate_average
	@place
	@menu_name
	@datetime
	@place
	@phone_number
]
@next_api[
	@/api.customer.beta/home/<username>
	@/api.customer.beta/reserves/<username>
	@/api.customer.beta/setting/<username>
]


ユーザー設定(User Setting)
/api.customer.beta/logs/<username>  (GET,  PUT)
GET
@last_name
@first_name
@email
@img
@age
@gender
@phone_number
@next_api[
	@/api.customer.beta/home/<username>
	@/api.customer.beta/reserves/<username>
	@/api.customer.beta/logs/<username>
	@/api.customer.beta/users/<username>
	@/api.customer.beta/password-fresh/<username>
]

PUT
@img
@age
@gender
@phone_number


名前とメアドの変更(Change name and email address)
/api.customer.beta/users/<username>  (PUT)
PUT
@last_name
@first_name
@email


パスワードの変更(Change Password)
/api.customer.beta/users/<username>  (PUT)
PUT
@old_password
@new_password


ユーザー登録(Register)
/api.customer.beta/register   (POST)
POST
@username
@email
@password


トークン発行(ログイン)(Generate Token—Login)
/api.customer.beta/auth-token  (POST)
POST
@username
@password