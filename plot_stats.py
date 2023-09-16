import json
import pandas  as pd
import seaborn as sns
import matplotlib.pyplot as plt

def get_data():
    with open('stats.txt','r') as file:
        data  = file.readlines()
        data  = [_json.strip() for _json in data]

    data = [json.loads(string) for string in data]
    df = pd.DataFrame(data)
    print(df.describe())
    print("+--------------------------+")
    return df    

while True:
    df = get_data()    
    df = df.drop(['freq_penalty_10','gen_count'],axis=1)
    plt.plot(df)
    plt.legend(df.columns)
    plt.draw()
    plt.pause(2)
    plt.clf()