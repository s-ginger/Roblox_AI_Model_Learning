import pandas as pd
from datasets import load_dataset
import matplotlib.pyplot as plt

# Загружаем датасет
ds = load_dataset(
    "Erik606/roblox-rivals-gameplay-dataset",
    split="train"
)

df: pd.DataFrame = ds.to_pandas()  # type: ignore


print(len(df))

print(df.shape)  
    
print(df.info())      

print(df["key_shift"].describe())
print(df["key_ctrl"].describe())

"""Summary
3826

(3826, 13)

<class 'pandas.DataFrame'>

RangeIndex: 3826 entries, 0 to 3825
Data columns (total 13 columns):
 #   Column       Non-Null Count  Dtype  
---  ------       --------------  -----  
 0   image        3826 non-null   object 
 1   timestamp    3826 non-null   float64
 2   mouse_x      3826 non-null   int32  
 3   mouse_y      3826 non-null   int32  
 4   mouse_left   3826 non-null   bool   
 5   mouse_right  3826 non-null   bool   
 6   key_w        3826 non-null   bool   
 7   key_a        3826 non-null   bool   
 8   key_s        3826 non-null   bool   
 9   key_d        3826 non-null   bool   
 10  key_space    3826 non-null   bool   
 11  key_shift    3826 non-null   bool   
 12  key_ctrl     3826 non-null   bool   
dtypes: bool(9), float64(1), int32(2), object(1)
memory usage: 123.4+ KB

None

count      3826
unique        1
top       False
freq       3826
Name: key_shift, dtype: object

count      3826
unique        1
top       False
freq       3826
Name: key_ctrl, dtype: object
"""
