import json
import sys
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import operator


def show_work_status(singleCount, totalCount, currentCount=0):
    if totalCount > 0:
        currentCount += singleCount
        percentage = 100.0 * currentCount / totalCount
        status = '>' * int(percentage) + '-' * (100 - int(percentage))
        sys.stdout.write('\r[{0}] {1:.2f}% '.format(status, percentage))
        sys.stdout.flush()
        if percentage >= 100:
            print('\n')


all_games_list = []
all_users_list = []
means_file = open("data/app_means.txt", "r")
for line in means_file:
    mean_game_props = json.loads(line.strip())
    all_games_list.append(mean_game_props)
df_all_games_list = pd.DataFrame(all_games_list)

user_id = open("data/steam_user_id.txt", "r")
for line in user_id:
    user = line.strip()
    all_users_list.append(user)

df = pd.read_csv('data/player_ratings.csv')
df = df.fillna(0)


##########
#Collaborative Filtering---User Score Based
##########

def similar_users(user_id, matrix, k=3):
    # Secilen kullaniciya ait df yaratilir
    user = matrix[matrix.index == user_id]

    # Kalan kullanicilarin df'i yaratilir
    other_users = matrix[matrix.index != user_id]

    # Kullanicilarin benzerligi cosine similarity ile hesaplanir
    similarities = cosine_similarity(user, other_users)[0].tolist()

    # diger kullanicilarin index leri alinir
    indices = other_users.index.tolist()

    # indisler benzerlikler ile hashlenir
    index_similarity = dict(zip(indices, similarities))

    # benzerlik puanina gore siralama islemi
    index_similarity_sorted = sorted(index_similarity.items(), key=operator.itemgetter(1))
    index_similarity_sorted.reverse()

    # en cok benzeyen 3 kullanici secilir
    top_users_similarities = index_similarity_sorted[:k]
    users = [u[0] for u in top_users_similarities]

    return users


def recommend_item(user_index, similar_user_indices, matrix, items=5):
    # en benzer kullanicilarin puanlari getirilir
    similar_users = matrix[matrix.index.isin(similar_user_indices)]
    # ortalama puanlar hesaplanir
    similar_users = similar_users.mean(axis=0)
    # elde edilen veri df ye cevrilir
    similar_users_df = pd.DataFrame(similar_users, columns=['mean'])

    # secilen kullanicinin puanlari getirilir
    user_df = matrix[matrix.index == user_index]
    # transpoze
    user_df_transposed = user_df.transpose()
    # kolon ismi rating yapilmasi
    user_df_transposed.columns = ['rating']
    # oynanmayan oyunlar filtrelenir
    user_df_transposed = user_df_transposed[user_df_transposed['rating'] == 0]

    games_unplayed = user_df_transposed.index.tolist()

    # secilen kullanicinin oynamadigi oyunun ortalama puaninin benzer kullanicilardan getirilmesi
    similar_users_df_filtered = similar_users_df[similar_users_df.index.isin(games_unplayed)]
    # df siralanir
    similar_users_df_ordered = similar_users_df_filtered.sort_values(by=['mean'], ascending=False)

    # en benzer 5 oyun getirilir
    top_n_game = similar_users_df_ordered.head(items)
    top_n_game_indices = top_n_game.index.tolist()
    # diger df den isimler getirilir
    game_rec_information = df_all_games_list[df_all_games_list['name'].isin(top_n_game_indices)]

    return game_rec_information


total_count = len(all_users_list)
show_work_status(0, total_count, 0)
recommended = []
for user_index in range(0, total_count):
    similar_user_indices = similar_users(user_index, df)
    recommended.append(recommend_item(user_index, similar_user_indices, df).values.tolist())
    show_work_status(1, total_count, user_index)

recommended_df = pd.DataFrame(recommended)
recommended_df.index = all_users_list
recommended_df.to_csv('data/recommendation.csv')
