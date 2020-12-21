######################## CONFIG ########################

# Madmin
db_host = 'localhost'
db_user = 'user'
db_pass = 'pass'
db_base = 'mapadroid'
db_port = 3306

instance_id = 1     # madmin instance
timeout_sek = 600   # seconds when a device is marked as offline
sleeptime   = 300   # seconds when the data is updated

# Telegram
telegram    = True
token       = '940537113:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
chat_id     = '@group_name'   # @username or id

# Discord
discord     = True
d_token     = 'NzkwMjEyNTM3NzQ4MTYwNTUy.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
d_channel   = 786657783185879044   # discord channel id

# Display Options
option_raids   = True
option_mon     = True
option_quest   = True
option_idle    = False
option_other   = False

# Display Options Detail
deteil_raids   = True
deteil_mon     = True
deteil_quest   = True
detail_idle    = False
detail_other   = False

area_exclude   = ['hidden_area_1', 'hidden_area_2']   # these areas are hidden

update_message = True   # if false, editing will only take place if changes are detected, with true specification of the sleeptime
pinned_message = True   # only Telegram

########################################################