import json
import sys
import pandas as pd

def my_max(arr):
    temp=-999
    for i in arr:
        if i is None:
            continue
        if i>temp:
            temp=i
    return temp


def my_min(arr):
    temp = 0
    for i in arr:
        if i is None:
            continue
        if i < temp:
            temp = i
    return temp


def normalize(arr, t_min, t_max):
    if my_max(arr)==0:
        return arr
    if arr==[]:
        return []
    norm_arr = []
    diff = t_max - t_min
    diff_arr = my_max(arr) - my_min(arr)
    for i in arr:
        if i is not None:
            temp = (((i - my_min(arr)) * diff) / diff_arr) + t_min
            norm_arr.append(temp)
        else:
            norm_arr.append(None)
    return norm_arr

def show_work_status(singleCount, totalCount, currentCount=0):
    if totalCount > 0:
        currentCount += singleCount
        percentage = 100.0 * currentCount / totalCount
        status = '>' * int(percentage) + '-' * (100 - int(percentage))
        sys.stdout.write('\r[{0}] {1:.2f}% '.format(status, percentage))
        sys.stdout.flush()
        if percentage >= 100:
            print('\n')


################################
# Oyuncunun oyuna harcadigi zamani, insanlarin ortalama harcama zamanina bol, oyuncunun skorunu bul ve csv olarak yazdir
################################

all_player_ratings = open("data/player_ratings.txt", "w")
player_details_file = open("data/user_inventory.txt")
flag = False
i=0
show_work_status(0,1000,i)
arrayOfRatings=[]
player_ids=[]
game_names=[]
for player_line in player_details_file:
    show_work_status(1, 1000, i)
    i += 1
    player_common_games = []
    player_game_ratings = []
    player_games = json.loads(player_line.strip())
    player_ids.append(list(player_games)[0])
    player_games = list(player_games.items())[0][1]
    means_file = open("data/app_means.txt")
    for mean_line in means_file:  # oyunlari appmeansten al
        flag = False
        mean_game_props = json.loads(mean_line.strip())
        mean_line_appid = list(mean_game_props.items())[0][1]  # Oyunun appid
        mean_line_median_amount = list(mean_game_props.items())[2][1]  # Oyunun median degeri
        if player_games is None:
            continue
        for game in player_games:  # oyuncunun oyunlarini al
            if game['appid'] == int(mean_line_appid):
                if mean_line_median_amount == 0:
                    player_game_ratings.append(None)
                else:
                    player_game_ratings.append(game['playtime_forever'] / mean_line_median_amount)
                    player_common_games.append(game['appid'])
                    flag = True
                    break
        if flag == False:
            player_game_ratings.append(None)
            player_common_games.append(None)
    means_file.close()
    arrayOfRatings.append(normalize(player_game_ratings,1,100))
    all_player_ratings.write(str(normalize(player_game_ratings,1,100)))
    all_player_ratings.write("\n")

means_file=open("data/app_means.txt","r")
for line in means_file:
    mean_game_props=json.loads(line.strip())
    game_names.append(mean_game_props['name'])

df=pd.DataFrame(arrayOfRatings)
game_names.append("player")
df.columns=game_names
del df['player']
df.to_csv("data/player_ratings.csv", index=False)