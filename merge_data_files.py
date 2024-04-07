import pandas as pd

#open files
sex_role = pd.read_csv('sex_role_scored.csv', encoding='utf-8') #file containing columns: CODE(normalized), psychological_gender

LEX = pd.read_csv('lextale.csv', encoding='utf-8') #file with columns: CODE, LEXTALE
LEX['CODE'] = LEX['CODE'].str.lower() #normalize CODE

IAT = pd.read_csv('IAT.csv', encoding='utf-8') #file containing columns: CODE, LG, BLOCK, ACCURACY, RT - long format data, with 185 rows per participant (185 trials)
IAT['CODE']=IAT['CODE'].str.lower() #normalize codes

participants = list(sex_role['CODE']) #list participants that completed the sex role inventory (i.e. those who completed the whole study)

rows_to_drop = IAT[~IAT['CODE'].isin(participants)].index #list of rows to drop from IAT data - rows belonging to participants who are NOT in the list of participants who completed the sex role inventory
IAT.drop(index=rows_to_drop, inplace=True) #drop participants that didn't do the sex role inventory

rows_to_drop1 = IAT[IAT['BLOCK'] =='Intro'].index #don't need the intro block for anything
IAT.drop(index=rows_to_drop1, inplace=True)

### INJECT THE PARTICIPANT'S MEAN FOR A BLOCK IN CASE THEIR ANSWER WAS INCORRECT IN THE IAT TRIAL ###

for nr in range(0,IAT.shape[0]): #go through each row
    row = IAT.iloc[nr]
    result = (None if row['ACCURACY'] == '0' else row['RT']) #put value as None if the answer was inaccurate, this means that when calculating means later it will not be taken into account
    IAT.at[nr, 'RT'] = result #assign new value or leave it the same

means_to_inject = IAT.groupby(['CODE', 'BLOCK'])['RT'].agg(lambda x: round(x.mean(skipna=True), 2)).reset_index() #calculate the means without inaccurate response RTs

for nr in range(0,IAT.shape[0]):
    row = IAT.iloc[nr]
    thecode = row['CODE']
    theblock = row['BLOCK']
    filtered_df = means_to_inject[(means_to_inject['CODE'] == thecode) & (means_to_inject['BLOCK'] == theblock)] # access the mean RT for the correct participant and block
    rt_values = filtered_df['RT'] #this is the mean RT
    result = (rt_values if row['RT'] == None else row['RT']) #inject the mean RT if the value had been removed, else leave it as is
    IAT.at[nr, 'RT'] = result #assign

#demographic info
dem = pd.read_csv('demographic_q.csv', encoding='utf-8') # file with columns: CODE, LGBT
dem['CODE']=dem['CODE'].str.lower() #normalize code
rows_to_drop = dem[~dem['CODE'].isin(participants)].index #drop data for participants that did not complete the sex role inventory
dem.drop(index=rows_to_drop, inplace=True)
dem.loc[dem['LGBT'] == 'nie chcę udzielać odpowiedzi na to pytanie', 'LGBT'] = 'no answer' #recode people who did not want to answer the question as 'no answer', for simplicity

### calculate means for each block, grouped by participant and by block ###

grouped_means = IAT.groupby(['CODE', 'BLOCK'])['RT'].agg(lambda x: round(x.mean(), 2)).reset_index() #group by code, block, then aggregate the RTs into a mean function, and round to two decimals
grouped_means.rename(columns={'RT': 'RT_m'}, inplace=True) #rename the variable so it indicates that this is the calculated mean

grouped_accuracy = IAT.groupby(['CODE', 'BLOCK'])['ACCURACY'].agg(lambda x: round(x.mean(), 2)).reset_index() #same thing for accurracy
grouped_accuracy.rename(columns={'ACCURACY': 'ACCURACY_m'}, inplace=True)

OUT = pd.merge(grouped_accuracy, grouped_means, on=('CODE','BLOCK'), how='inner') #merge the two resulting dataframes on code and block

lg_info = IAT.loc[:, ['CODE', 'LG']].reset_index(drop=True) #create a dataframe with two columns: CODE, LG
lg_info = lg_info.drop_duplicates() #IAT is a long format so drop duplicates
OUT = pd.merge(OUT, lg_info, on='CODE') #merge

### calculate participant age based on their code ###

OUT['AGE'] = 0 #create a column to hold the values

for nr in range(0,OUT.shape[0]): #go through each row of the dataframe
    row = OUT.iloc[nr]
    nineteen = 2024-(int("19"+row['CODE'][4:])) #the age calculated for someone born in a year starting with '19'
    twenty = 2024-(int("20"+row['CODE'][4:])) #the age calculated for someone born in a year starting with '20'
    age = (twenty if row['CODE'][4] == '0' else nineteen) #the code is the last two digits of birth year, this checks which equation to use
    OUT.at[nr, 'AGE'] = age #assign value to variable


### final edits ###

#add lextale scores
OUT  = pd.merge(OUT, LEX, how='left', on='CODE') #add to our main dataframe

#add sex role results
OUT = pd.merge(OUT, sex_role,how='left',on='CODE')

#add demographic info
OUT = pd.merge(OUT, dem,how='left', on='CODE')

#sort by language
OUT = OUT.sort_values(by=['LG', 'CODE']) #easier to read in excel

#save new file
OUT.to_csv('merged_data_1.csv',index=False) #index False because there is no need for it to be numbered