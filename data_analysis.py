### DEPENDENCIES ###
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

### LOAD DATA AND PREPROCESS ###
DATA = pd.read_csv('merged_data_1.csv', encoding='utf-8') #file with columns: CODE, BLOCK, ACCURACY_m, RT_m, LG, AGE, LEXTALE, psychological_gender, LGBT; each CODE (participant) takes 7 rows

DATA.loc[DATA['BLOCK'] == 'Block1Proc', 'BLOCK'] = '1' #for simplicity's sake
DATA.loc[DATA['BLOCK'] == 'Block2Proc', 'BLOCK'] = '2'
DATA.loc[DATA['BLOCK'] == 'Block3Proc', 'BLOCK'] = '3'
DATA.loc[DATA['BLOCK'] == 'Block4Proc', 'BLOCK'] = '4'
DATA.loc[DATA['BLOCK'] == 'Block5Proc', 'BLOCK'] = '5'
DATA.loc[DATA['BLOCK'] == 'Block6Proc', 'BLOCK'] = '6'
DATA.loc[DATA['BLOCK'] == 'Block7Proc', 'BLOCK'] = '7'

# separate wide format data
uniques = DATA.drop_duplicates(subset='CODE') #leaves the first row of each CODE, leaving the wide format data
uniques = uniques.drop(columns=['RT_m','ACCURACY_m','BLOCK']) #drop the rows that need long format

#just English data
EN_DATA = DATA.loc[:, ['CODE', 'RT_m', 'ACCURACY_m', 'LG', 'BLOCK']].reset_index(drop=True) #takes only specified columns
rowstodrop = DATA[DATA['LG'].isin(['GSOIAT_Polish'])].index #choose what to drop
EN_DATA.drop(index = rowstodrop, inplace=True) #drop it

#just Polish data
PL_DATA = DATA.loc[:, ['CODE', 'RT_m', 'ACCURACY_m', 'LG', 'BLOCK']].reset_index(drop=True) #takes only specified columns
rowstodrop = DATA[DATA['LG'].isin(['GSOIAT_English'])].index #choose what to drop
PL_DATA.drop(index = rowstodrop, inplace=True) #drop it

### STATISTICS FOR REPORTING ###

## mean participant age
AGE_m = round(np.mean(uniques['AGE']),2)
AGE_m_summary = f'age M = {AGE_m}'

## SD for participant age
AGE_sd = round(uniques['AGE'].std(),2)
AGE_sd_summary = f'age SD = {AGE_sd}'

## mean LEXTALE score
LEXTALE_m = round(np.mean(uniques['LEXTALE']),2)
LEXTALE_m_summary = f'Lextale score M = {LEXTALE_m}'

## SD for LEXTALE score
LEXTALE_sd = round(uniques['LEXTALE'].std(),2)
LEXTALE_sd_summary = f'Lextale score SD = {LEXTALE_sd}'

## LGBT community counts
LGBT_c = uniques['LGBT'].value_counts() #now count
LGBT_c_summary = f'LGBT community stats: {LGBT_c}'

## mean ACCURACY overall
ACC_m = round(DATA['ACCURACY_m'].mean(),2)
ACC_m_summary = f'accuracy overall M = {ACC_m}'

# SD ACCURACY overall
ACC_sd = round(DATA['ACCURACY_m'].std(),2)
ACC_sd_summary = f'accuracy overall SD = {ACC_sd}'

# mean ACCURACY for each block, grouped by language
ACC_by_block = DATA.groupby(['LG', 'BLOCK'])['ACCURACY_m'].agg(lambda x: round(x.mean(), 2)).reset_index()
ACC_by_block_summary = f'accuracy by block \n{ACC_by_block}'

# mean RT for each block, grouped by language
RT_by_block = DATA.groupby(['LG', 'BLOCK'])['RT_m'].agg(lambda x: round(x.mean(), 2)).reset_index() #aggregate function takes each group and performs a func - mean calculation
RT_by_block_summary = f'reaction time by block \n{RT_by_block}'                                     #also rounds to two places after decimal

# SD for each block, grouped by language
RT_by_block_sd = DATA.groupby(['LG', 'BLOCK'])['RT_m'].agg(lambda x: round(x.std(), 2)).reset_index()
RT_by_block_sd.rename(columns={"RT_m": "RT_sd"}, inplace=True)
RT_by_block_sd_summary = f'reaction time by block SD \n{RT_by_block_sd}'  

# generate a simple report
reports = [AGE_m_summary,AGE_sd_summary,LEXTALE_m_summary,LEXTALE_sd_summary,LGBT_c_summary,ACC_m_summary, ACC_sd_summary, ACC_by_block_summary, RT_by_block_summary, RT_by_block_sd_summary]

with open('report_statistics.txt', 'w') as f:
    for r in reports:
        f.write(r + '\n\n')

### DATA VISUALIZATION ###

## mean RT for each block, grouped by language - graphs

#POLISH - matplotlib solution
x = PL_DATA['BLOCK'] #x-axis data
y = PL_DATA['RT_m'] #y-axis data

plt.bar(x, y, color=['red' if val in ['3','4','6','7'] else 'blue' for val in x]) #color the BLOCKS that are of interest
plt.xlabel('Block')
plt.ylabel('RT')
plt.title('mean Reaction Time by block - Polish')

plt.savefig('Polish_RTs.png')

#ENGLISH - matplotlib solution

x = EN_DATA['BLOCK'] #x-axis data
y = EN_DATA['RT_m'] #y-axis data

plt.bar(x, y, color=['red' if val in ['3','4','6','7'] else 'blue' for val in x]) #color the BLOCKS that are of interest
plt.xlabel('Block')
plt.ylabel('RT')
plt.title('mean Reaction Time by block - English')

plt.savefig('English_RTs.png')

#combined lgs - seaborn solution

c = sns.catplot(data=DATA, kind='bar', x="BLOCK", y="RT_m", hue="LG", palette=['dodgerblue', 'limegreen'], legend=True, errorbar='sd') #visualize means and SD
c.set(xlabel='Block', ylabel='Reaction Time') #change axis labels

#change legend labels
n_title = 'Language'
c._legend.set_title(n_title)

n_labels = ['English', 'Polish']
for t, l in zip(c._legend.texts, n_labels):
    t.set_text(l)

plt.savefig('combined_RTs.png')

### STATISTICAL TESTS ###

# t-tests

from scipy.stats import ttest_ind #t-test for independent samples
from scipy.stats import ttest_rel #t-test for dependent samples / paired samples t-test

# independent samples t-test for difference in Reaction Times in the same block BETWEEN languages
for nr in ['3','4','6','7']:
    t_stat, p_value = ttest_ind(EN_DATA[EN_DATA['BLOCK']==nr]['RT_m'], PL_DATA[PL_DATA['BLOCK']==nr]['RT_m'])
    with open('report_statistical_tests.txt', 'a') as f:
        f.write(f'For block nr {nr} (comparison between languages): \np-value: {p_value} \nt-test: {t_stat}\n\n')

#combine the RTs for BLOCKS with same task (3,4) and (6,7)
EN_combined_blocks_3_4 = pd.concat((EN_DATA[EN_DATA['BLOCK']=='3']['RT_m'], EN_DATA[EN_DATA['BLOCK']=='4']['RT_m']), ignore_index=True) 
EN_combined_blocks_6_7 = pd.concat((EN_DATA[EN_DATA['BLOCK']=='6']['RT_m'], EN_DATA[EN_DATA['BLOCK']=='7']['RT_m']), ignore_index=True)
PL_combined_blocks_3_4 = pd.concat((PL_DATA[PL_DATA['BLOCK']=='3']['RT_m'], PL_DATA[PL_DATA['BLOCK']=='4']['RT_m']), ignore_index=True)
PL_combined_blocks_6_7 = pd.concat((PL_DATA[PL_DATA['BLOCK']=='6']['RT_m'], PL_DATA[PL_DATA['BLOCK']=='7']['RT_m']), ignore_index=True)

# paired samples t-test for comparison of blocks WITHIN a language
t_stat, p_value = ttest_rel(EN_combined_blocks_3_4, EN_combined_blocks_6_7)
with open('report_statistical_tests.txt', 'a') as f:
    f.write(f'For block nr 3+4 and 6+7 (English): \np-value: {p_value} \nt-test: {t_stat}\n\n')

t_stat, p_value = ttest_rel(PL_combined_blocks_3_4, PL_combined_blocks_6_7)
with open('report_statistical_tests.txt', 'a') as f:
    f.write(f'For block nr 3+4 and 6+7 (Polish): \np-value: {p_value} \nt-test: {t_stat}\n\n')

# independent samples t-test for comparison of blocks BETWEEN languages
t_stat, p_value = ttest_ind(PL_combined_blocks_3_4, EN_combined_blocks_3_4)
with open('report_statistical_tests.txt', 'a') as f:
    f.write(f'For block nr 3+4 (between languages): \np-value: {p_value} \nt-test: {t_stat}\n\n')

t_stat, p_value = ttest_ind(PL_combined_blocks_6_7, EN_combined_blocks_6_7)
with open('report_statistical_tests.txt', 'a') as f:
    f.write(f'For block nr 6+7 (between languages): \np-value: {p_value} \nt-test: {t_stat}\n\n')