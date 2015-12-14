
import numpy as np
import pandas as pd
from sklearn.naive_bayes import GaussianNB

def concat_scores(seasons):
    frames = []
    for k in seasons.keys():
        scores = seasons[k]['features']['scores']
        time_line = np.sort(scores.keys())
        for t in time_line:
            df = scores[t]
            df['season'] = k
            df['time'] = t
            frames.append(df)
    df = pd.concat(frames).reset_index(drop=True)
    df['contestant_id'] = [':'.join(i) for i in zip(df['name'], df['season'])]
    return df

def build_training_data(data, current_time):
    available_times = data.time.unique()
    times_to_use = np.sort(available_times[available_times <= current_time])[::-1]
    frames = []
    active_contestants = set(data.contestant_id)
    ignore_cols = ['name', 'season', 'contestant_id', 'place']
    for t in times_to_use:
        df_t = data.loc[data.time == t, :]
        active_contestants = active_contestants.intersection(df_t.contestant_id)
        ac_filter = [i in active_contestants for i in df_t.contestant_id]
        df_min = df_t.loc[ac_filter, :]
        df_min.columns = [i if i in ignore_cols else i + '-' + str(t) 
                          for i in df_min.columns]
        frames.append(df_min)
    df = frames.pop()
    while len(frames) > 0:
        df_m = frames.pop()
        df = pd.merge(df, df_m.drop(['name', 'season', 'place'], 1), on='contestant_id')
    return df
    
def model_nb(data):
    ignore_cols = ['name', 'season', 'contestant_id'] + \
        [i for i in data.columns if 'time' in i]
    Y = data.place
    X = data.drop(ignore_cols + ['place'], axis=1)
    nb = GaussianNB()
    nb.fit(X, Y)
    predictions = nb.predict_proba(X)
    return {'model': nb, 'predictions': predictions}

def predict_winners(models):
    for t in models.keys():
        model_data = models[t]['data']
        # add predictions col
        model_data['predictions'] = models[t]['nb']['predictions'][:, 1]
        
        models[t]['accuracy'] = {}
        seasons = model_data.groupby('season')
        for season in seasons:
            k = season[0]
            df = season[1]

            models[t]['accuracy'][k] = {}
            return_dict = models[t]['accuracy'][k]
            
            actual_winner = df['name'][df['place'] == 1].values[0]
            predicted_winner = df['name'][df['predictions'] == df['predictions'].max()]
            # solve ties alphabetically (for consitency)
            predicted_winner = sorted(predicted_winner)[0]
            
            return_dict['actual_winner'] = actual_winner
            return_dict['predicted_winner'] = predicted_winner
            return_dict['match'] = actual_winner == predicted_winner

def predict_season_winners(seasons):
    combined_data = concat_scores(seasons)
    season_times = combined_data.time.unique()
    models = {}
    for t in season_times:
        model_data = build_training_data(combined_data, t)
        trained_model = model_nb(model_data)
        models[t] = {'data': model_data,
                     'nb': trained_model}
    predict_winners(models)
    return models