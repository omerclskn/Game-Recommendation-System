import requests, json, os, sys, time, re
from datetime import datetime
from multiprocessing import Pool
#%%
## split the long list for multiprocessing
def split_list(lst_long, n):
    lst_splitted = []
    if len(lst_long) % n == 0:
        totalBatches = int(len(lst_long) / n)
    else:
        totalBatches = int(len(lst_long) / n + 1)
    for i in range(totalBatches):
        lst_short = lst_long[i*n:(i+1)*n]
        lst_splitted.append(lst_short)
    return lst_splitted

## create work status bar
def show_work_status(singleCount, totalCount, currentCount=0):
    if totalCount > 0:
        currentCount += singleCount
        percentage = 100.0 * currentCount / totalCount
        status =  '>' * int(percentage)  + '-' * (100 - int(percentage))
        sys.stdout.write('\r[{0}] {1:.2f}% '.format(status, percentage))
        sys.stdout.flush()
        if percentage >= 100:
            print ('\n')

path_user_id = 'data/steam_user_id.txt'
with open(path_user_id, 'r') as f:
    lst_user_id = f.readlines()

def worker(user_id):
    dic_temp = {}
    base_url = 'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'
    params = {
        'key' : 'C039C46919B6152200FF6FCD42241897', # Steam web API key
        'steamid' : user_id.strip(),
        'format' : 'json' }
    r = requests.get(base_url, params = params)
    user_inventory = r.json().get('response').get('games')
    dic_temp.update({user_id.strip():user_inventory})
    time.sleep(1)
    return dic_temp

total_count = len(lst_user_id)
current_count = 0
show_work_status(0, total_count, current_count)

dic_master = {}
for i in lst_user_id:
    lst_temp_dic = worker(i)
    dic_master.update(lst_temp_dic)
    show_work_status(1, total_count, current_count)
    if current_count % 100==0:
        time.sleep(5)
    current_count += 1

with open('data/user_inventory.txt', 'w') as f:
    for user_id, user_inventory in dic_master.items():
        f.write(json.dumps({user_id:user_inventory}))
        f.write('\n')