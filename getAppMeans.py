import requests
import json
import time
import sys

###
# app-detail.txt icerisindeki id name pairini alir
###

def show_work_status(singleCount, totalCount, currentCount=0):
    if totalCount > 0:
        currentCount += singleCount
        percentage = 100.0 * currentCount / totalCount
        status = '>' * int(percentage) + '-' * (100 - int(percentage))
        sys.stdout.write('\r[{0}] {1:.2f}% '.format(status, percentage))
        sys.stdout.flush()
        if percentage >= 100:
            print('\n')

temp = []
f = open("data/app_detail.txt", "r")
for x in f:
    x = x.encode("windows-1252", "ignore").decode("windows-1252")
    y = json.loads(x)
    if list(y.items())[0][1]['success']:
        temp.append((list(y.items())[0][0], list(y.items())[0][1]['data']['name']))

app_means = open('data/app_means.txt', "w", encoding="utf-8")
i = 0
show_work_status(0, len(temp), i)

###
# oyunun id'sini yollayarak median playtime alir ve id name median triplet'ini
# app_means dosyasina her satir ayri bir JSON nesnesi olacak sekilde kaydeder
###
print("Toplam uzunluk: ",len(temp))
for x in temp:
    ploads = {'request': 'appdetails', 'appid': temp[i][0]}
    r = requests.get('http://steamspy.com/api.php', params=ploads)

    temp_dict = {
        'appid': temp[i][0],
        'name': temp[i][1],
        'median': r.json().get('median_forever')
    }
    i += 1
    show_work_status(1, len(temp), i)
    json.dump(temp_dict, app_means)
    app_means.write("\n")
    time.sleep(1)
app_means.close()