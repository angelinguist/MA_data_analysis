import pandas as pd

df = pd.read_csv('sex_role.csv', encoding='utf-8') #file with data in a wide format, columns: CODE, Q1, Q2, Q3, Q4, Q5, ... Qn

sex_role_answer_mapping = {'zupełnie taka nie jestem':1, 'odrobinę taka jestem': 2, 'ani taka nie jestem, ani jestem':3, 'trochę taka jestem':4, 'właśnie taka jestem' :5} #answers to Qs were recorded as text, recode them to numbers
df.iloc[:, 1:df.shape[1]]=df.iloc[:,1:36].replace(sex_role_answer_mapping) #replaces text with digit

neutral_items =['odpowiedzialna', 'przyjacielska', 'wiarygodna','tolerancyjna','sympatyczna']
feminine_items = ['wrażliwa','troskliwa','angażująca się w sprawy innych','łagodna','kokieteryjna','dbająca o swój wygląd','gospodarna','mająca poczucie estetyki','gderliwa','czuła','uczuciowa','wrażliwa na potrzeby innych','zdolna do poświęceń','delikatna','naiwna']
masculine_items = ['dominująca','niezależna','rywalizująca','nastawiona na sukces','mająca siłę przebicia','łatwo podejmująca decyzję','arogancka','mająca dobrą kondycję fizyczną','z poczuciem humoru','mająca zdolność przekonywania','pewna siebie','samowystarczalna','otwarta na świat zdarzeń zewnętrznych','eksperymentująca w życiu seksualnym','sprytna']

df['masculinity_score']=0 #add a column for masculinity score of the participant
df['femininity_score']=0 #add a column for femininity score of the participant
df.drop(columns=neutral_items, inplace=True) #drop neutral items as they are not taken into account when scoring later

for nr in range(0,df.shape[0]): #go through whole dataframe
    row = df.iloc[nr] #establish the row you're in

    sum_fem = row[feminine_items].sum() #get a sum of feminine items (femininity score)
    sum_masc = row[masculine_items].sum() #get a sum of masculine items (masculinity score)

    df.at[nr, 'femininity_score'] = sum_fem #insert these scores in their columns in the correct row
    df.at[nr, 'masculinity_score'] = sum_masc

df['psychological_gender'] ='' #create a column for the psychological gender variable

for nr in range(0,df.shape[0]): #go through the dataframe
    row = df.iloc[nr]

    if df.at[nr, 'femininity_score'] <=51 and df.at[nr, 'masculinity_score'] <=48: #assign a psychological gender based on scores
        df.at[nr, 'psychological_gender'] = 'non-binary person'
    elif df.at[nr, 'femininity_score'] >=52 and df.at[nr, 'masculinity_score'] <=48:
        df.at[nr, 'psychological_gender'] = 'feminine person'
    elif df.at[nr, 'femininity_score'] <=51 and df.at[nr, 'masculinity_score'] >=49:
        df.at[nr, 'psychological_gender'] = 'masculine person'
    elif df.at[nr, 'femininity_score'] >=52 and df.at[nr, 'masculinity_score'] >=49:
        df.at[nr, 'psychological_gender'] = 'androgynous person'

df['CODE']=df['CODE'].str.lower() #normalize codes
df = df.loc[:, ['CODE', 'psychological_gender']] #overwrite the dataframe with just the two columns that are relevant

df.to_csv('sex_role_scored.csv',index=False) #save

