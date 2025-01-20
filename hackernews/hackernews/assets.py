import requests
from dagster import AssetOut, IOManager, asset, io_manager, multi_asset
import pandas as pd
from sklearn.model_selection import train_test_split

asset_group_name = "hackernews"

class LocalCSVIOManager(IOManager):
     def handle_output(self, context, obj):
        # insert you custome method
        obj.to_csv(f"{context.asset_key.path[-1]}.csv")

     def load_intput(self, context):
        return pd.read_csv(f"{context.asset_key.path[-1]}.csv")

@io_manager
def local_csv_io_manager():
     return LocalCSVIOManager()        

@asset(group_name=asset_group_name, compute_kind="pandas",
       io_manager_key="local_csv_io_manager")
def hackernews_stories():
    latest_item = requests.get("https://hacker-news.firebaseio.com/v0/maxitem.json").json()
    results = []
    scope = range(latest_item - 200, latest_item - 10)
    for item_id in scope:
        item = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{item_id}.json").json()
        results.append(item)

    df = pd.DataFrame(results)
    if len(df) > 0:
            df = df[df.type == "story"]
            df = df[~df.title.isna()]
    return df

@multi_asset(
     group_name=asset_group_name,
     compute_kind="scikit-learn",
     outs={"training_data" : AssetOut(), "test_data": AssetOut()}
)
def training_test_data(hackernews_stories):
     X = hackernews_stories.title
     y = hackernews_stories.descendants

     X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
     return (X_train, y_train), (X_test, y_test)