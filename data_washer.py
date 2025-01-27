
"""

This is the final iteration of code that will be used to clean the faunal data for Laurel's Zincirli dissertation
Created: May 4, 2022
Updated: February 2, 2023

"""

#%% PRELIMINARY SETUP: 1) IMPORT PACKAGES, 2) OCHRE-PRODUCED FILE, 3) ASSIGN BASIC VARIABLES, AND 4) CREATE EMPTY DATAFRAME FOR RESULTS

#region import necessary packages

import datetime
import os
import re
import string

import numpy as np
import pandas as pd

#endregion

# get cwd
og_cwd = os.getcwd()
os.chdir('/Users/laurelpoolman/PycharmProjects/BoneWasher')
cwd = os.getcwd()
print("YOUR CURRENT WORKING DIRECTORY:", cwd)

# assign output path for inspection files
inspection_output = cwd + '/inspection_outputs'

# assign today's date and time
today = datetime.datetime.now()
date_today = today.strftime("%d_%m_%Y")
right_now = today.strftime("%H:%M, %d_%m_%Y")

# read in the original excel file
area = 'A8'
og_faunal_file = cwd + '/og_datasets/faunal_data/%s_fauna_export.xlsx' % area
og_locus_file = cwd + '/og_datasets/locus_data/%s_locus_export.xlsx' % area
og_df = pd.read_excel(og_faunal_file)

## create an empty data frame to receive cleaning results
final_df = pd.DataFrame(
    columns=['observer', 'taxon', 'element1', 'element2', 'tooth', 'tooth_p/d', 'tws', 'side', 'fusion', 'd&r',
             'portion', '%pe', '%ps', '%ms', '%ds', '%de', '%complete', 'sex', 'age', 'bsm', 'burn', 'weather_stage',
             'butchery', 'Notes'])

print("INITIAL IMPORTS AND VARIABLE ASSIGNMENTS COMPLETE")



#%% STEP 1: GET BASIC INFORMATION ABOUT YOUR ORIGINAL DATAFRAME


# get a description of your dirty dataframe
og_df_shape = og_df.shape
print("DATA FRAME DESCRIPTION\n")
print("\nSHAPE (ROWS, COLUMNS):", og_df_shape)

# drop empty columns for efficient processing
empty_cols = [col for col in og_df if og_df[col].isnull().all()]
og_df = og_df.drop(empty_cols, axis = 1)

# define column headings as a string for later searches
og_column_names = list(og_df.columns.values)



#%% STEP 2: CREATE DICTIONARIES FROM THE ORIGINAL DATAFRAME COLUMNS

#%% 2A. EXPORT VALUES FOR TRANSLATION

        # region TAXON EXPORT


# get the taxon values that you'll need to translate
tax_df = og_df.filter(regex='taxon')
tax_cols = list(tax_df.columns.values)
og_tax_vals = set(np.concatenate(tax_df.values))
og_tax_vals = list(map(lambda x: str(x), og_tax_vals))
og_tax_vals.sort()
ntax_vals = len(og_tax_vals)

# export taxon values to an excel file for inspection, manual translation, and level assignment before copy+pasting it to the working taxon dictionary entitled working_taxon_dict.xlsx
taxon_translation_df = pd.DataFrame(og_tax_vals, columns=['og_taxon_term'])
taxon_translation_df = taxon_translation_df.reindex(
    columns=taxon_translation_df.columns.tolist() + ['final_tax_term', 'search_level'])
taxon_translation_df.to_excel(inspection_output + '/og_taxon_values_%s' % date_today + '.xlsx', index=False)
print("SUCCESSFUL EXPORT OF %s TAXON TERMS FOR MANUAL TRANSLATION, " % ntax_vals, right_now)

        # endregion

        # region ELEMENT EXPORT

# get the element values that you'll need to translate
element_df = og_df.filter(regex='Skeletal element$')
element_cols = list(element_df.columns.values)
og_element_vals = set(np.concatenate(element_df.values))
og_element_vals = list(map(lambda x: str(x), og_element_vals))
og_element_vals.sort()
nelement_vals = len(og_element_vals)

#export element terms to excel for manual translation
element_translation = pd.DataFrame(og_element_vals, columns=['og_element_val'])
element_translation = element_translation.reindex(
    columns=element_translation.columns.tolist() + ['element1', 'element2'])
element_translation.to_excel(inspection_output + "/og_element_values_%s" % date_today + ".xlsx", index=False)

print("SUCCESSFUL EXPORT OF %s ELEMENT TERMS FOR MANUAL TRANSLATION, " % nelement_vals, right_now)

        #endregion

        #region TOOTH CLASS EXPORT

# pull out tooth-related information in a separate df
tooth_df = og_df.filter(regex='Tooth')
tooth_df.columns = tooth_df.columns.str.replace('/Skeletal element/Tooth/Tooth, ', '', regex=True)
toothclass_df = tooth_df.filter(regex='Tooth, class')
tooth_df = tooth_df.rename(columns={'class.1': 'molar_class'})
tooth_df_shape = tooth_df.shape
tooth_cols = list(tooth_df.columns.values)
tooth_vals = set(np.concatenate(tooth_df.values))
tooth_vals = list(map(lambda x: str(x), tooth_vals))
tooth_vals.sort()

# add extra tooth information from description and notes columns
description_notes_cols = og_df[["Description", "Notes"]]
tooth_df = pd.concat([tooth_df, description_notes_cols], axis=1)

# try to figure out what values you need to translate in your tooth class column
toothclass_vals = set(np.concatenate(toothclass_df.values))
toothclass_vals = list(map(lambda x: str(x), toothclass_vals))
toothclass_vals = list(map(lambda x: x.split(';'), toothclass_vals))
toothclass_vals = [term for sublist in toothclass_vals for term in sublist]
toothclass_vals = list(set(toothclass_vals))
toothclass_vals.sort()
ntclass_vals = len(toothclass_vals)

# export the terms to an excel file for translation.  Note that these 'translations' will be implemented by means of find and replace, so they will be applied to substrings that we want to get rid of.

toothclass_translation_df = pd.DataFrame(toothclass_vals, columns=['og_toothclass_term'])
toothclass_translation_df = toothclass_translation_df.reindex(
    columns=toothclass_translation_df.columns.tolist() + ['replacement_value'])
toothclass_translation_df.to_excel(inspection_output + "/og_toothclass_values_%s" % date_today + ".xlsx", index=False)

print("SUCCESSFUL EXPORT OF %s TOOTH CLASS TERMS FOR MANUAL TRANSLATION, " % ntclass_vals, right_now)

        #endregion

        #region TOOTH WEAR STAGE EXPORT

# pull wear stage information for cleaning. We know for Zincirli data that this exists in the Notes column as well as other designated columns
wear_stage_df = og_df.filter(regex='wear stage$')
wear_stage_df['Notes'] = og_df['Notes']

tws_vals = list(set(np.concatenate(wear_stage_df.values)))
ntws_vals = len(tws_vals)

# export the messy tws values to an excel for translation evaluation and entry into tws_strip. Note that these 'translations' will be implemented by means of find and replace, so they will be applying to substrings that we want to get rid of

tws_val_df = pd.DataFrame(tws_vals, columns=['og_tws_vals'])
tws_val_df = tws_val_df.reindex(columns=tws_val_df.columns.tolist() + ['new_val'])
find_tws_list = ['G[a-z]', 'TWS']
tws_contains_filter = '|'.join(find_tws_list)
tws_val_df = tws_val_df[tws_val_df['og_tws_vals'].str.contains(tws_contains_filter, na=False, regex=True)]
tws_val_df.to_excel(inspection_output + '/og_tws_values_%s' % date_today + '.xlsx', index=False)
print("SUCCESSFUL EXPORT OF %s TWS TERMS FOR STRIP DICT CREATION, " % ntws_vals, right_now)

#endregion

        #region SYMMETRY EXPORT

# find the symmetry values that we want to export in a column with the word symmetry in it
sym_col = pd.Series(og_df.filter(regex='symmetry').columns.format()).get(0)
og_sym_vals = list(set(og_df[sym_col].values))
nsym_vals = len(og_sym_vals)

# export these values to an excel for manual translation before being copied and pasted into the working_sym_strip.xlsx
og_sym_df = pd.DataFrame(og_sym_vals, columns=['og_sym_term'])
og_sym_df = og_sym_df.reindex(columns=og_sym_df.columns.tolist() + ['new_val'])
og_sym_df.to_excel(inspection_output + '/og_sym_values_%s' % date_today + '.xlsx', index=False)

print("SUCCESSFUL EXPORT OF %s SYMMETRY TERMS FOR STRIP DICT CREATION, " % nsym_vals, right_now)

#endregion

        #region PORTION EXPORT

# get the portion values that you'll need to tranlsate
og_port_vals = list(set(og_df['RF/Skeletal element portion'].values))
nport_vals =len(og_port_vals)

og_port_df = pd.DataFrame(og_port_vals, columns=['og_port_term'])
og_port_df = og_port_df.reindex(columns=og_port_df.columns.tolist() + ['new_val'])
og_port_df.to_excel(inspection_output + '/og_port_values_%s' % date_today + '.xlsx', index=False)

print("SUCCESSFUL EXPORT OF %s PORTION TERMS FOR REPLACEMENT DICTIONARY CREATION, " %nport_vals, right_now)

#endregion

#region BURN EXPORT
burn_col = pd.Series(og_df.filter(regex="burn").columns.format()).get(0)
og_burn_vals = list(set(og_df[burn_col].values))




#endregion


        #region LOCUS EXPORT

# create a final locus df for easy reference
final_loci_df = pd.DataFrame(columns=['locus', 'phase', 'type', 'agent', 'description'])

# read in the original locus file
og_loci_df = pd.read_excel(og_locus_file).astype(str)

# pull the information you'll need into your new locus dataframe
final_loci_df['locus'] = og_loci_df['Name']
final_loci_df['phase'] = og_loci_df['Periods']
final_loci_df['type'] = og_loci_df['Type locus']
final_loci_df['agent'] = og_loci_df['Agent']
final_loci_df['description'] = og_loci_df['Description']

# export locus types to an excel for reference and priority assignment
loci_types = set(final_loci_df['type'].unique())
loci_types = list(map(lambda x: str(x), loci_types))
loci_types.sort()
loci_priorities = pd.DataFrame(loci_types, columns=['loci_type'])
loci_priorities.to_excel(inspection_output + "/%s_loci_types_%s" % (area, date_today) + ".xlsx", index = False)

# export locus agents to an excel for reference and priority assignment
loci_agents = set(final_loci_df['agent'].unique())
loci_agents = list(map(lambda x: str(x), loci_agents))
loci_agents.sort()
loci_agent_priorities = pd.DataFrame(loci_agents, columns=['loci_agent'])
loci_agent_priorities.to_excel(inspection_output + "/%s_loci_agents_%s" % (area, date_today) + ".xlsx", index = False)

# filter your df to only include columns that have the word bone in them
bone_mask = og_loci_df.apply(lambda col: col.str.contains('bone', flags=re.IGNORECASE).any(), axis=0)
bone_loci_df = og_loci_df.loc[:, bone_mask]
locus_col = og_loci_df['Name']
phase_col = og_loci_df['Periods']
type_col = og_loci_df['Type locus']
bone_loci_df.insert(0, 'locus', locus_col)
bone_loci_df.insert(1, 'phase', phase_col)
bone_loci_df.insert(2, 'type', type_col)

# filter the manual locus dataframe to only those loci that contain the word bone and export it for inspection
bone_loci_df = bone_loci_df[bone_loci_df.apply(lambda r: r.str.contains('bone', case=False).any(), axis=1)]
bone_loci_df.to_excel(inspection_output + '/loci_manual_inspection%s' % date_today + '.xlsx')

print("SUCCESSFUL EXPORT OF LOCI TYPES, AGENTS, AND BONE CONTAINERS FOR TRANSLATION, ", right_now)

#endregion

#region PHASE EXPORT

# get unique values from phase column for export

phase_vals = list(set(phase_col.unique()))
og_phase_df = pd.DataFrame(phase_vals, columns=['og_phase_val'])
og_phase_df.to_excel(inspection_output + '/%s_og_phases' % area + '.xlsx')

#og_phase_vals = list(set(og_df['Periods (inherited/related)'].values))
#og_phase_df = pd.DataFrame(og_phase_vals, columns = ['og_phase_val'])
#og_phase_df.to_excel(inspection_output + '/og_phase_values_%s' % date_today + '.xlsx', index=False)

print("SUCCESSFUL EXPORT OF PHASES FOR SIMPLIFICATION AND TRANSLATION")

print("PRELIMINARY EXPORTS FOR INSPECTION COMPLETE. PLEASE INSPECT AND DEFINE NEW TRANSLATIONS AND STRIP DICTIONARIES THEN ADD TO THE WORKING DICTIONARIES")


#%% 2B. IMPORT EXCELS AND CREATE WORKING DICTIONARIES/SEARCHES


# assign excel file dictionaries to values
taxon_dict_excel = cwd + '/dictionaries/working_taxon_dict.xlsx'
element_dict_excel = cwd + '/dictionaries/working_element_dict.xlsx'
portion_dict_excel = cwd + '/dictionaries/working_port_dict.xlsx'
toothclass_dict_excel = cwd + '/dictionaries/working_toothclass_dict.xlsx'
tws_dict_excel = cwd + '/dictionaries/working_tws_strip.xlsx'
sym_dict_excel = cwd + '/dictionaries/working_sym_strip.xlsx'
burn_dict_excel = cwd + '/dictionaries/working_burn_dict.xlsx'
locus_type_excel = cwd + '/dictionaries/loci_type_dict.xlsx'
locus_agent_excel = cwd + '/dictionaries/loci_agent_dict.xlsx'
keep_code_excel = cwd + '/dictionaries/keep_code_dict.xlsx'
manual_keep_excel = cwd + '/dictionaries/manual_keep_dict.xlsx'
manual_keep_xl = pd.ExcelFile(manual_keep_excel)
period_dict_excel = cwd + '/dictionaries/working_period_dict.xlsx'


# convert the excel files to dictionaries

#region TAXON DICTIONARIES

tax_dict_df = pd.read_excel(taxon_dict_excel)
tax_dict_df = tax_dict_df.astype(str)

# create first search dictionary
tax_dict_df1 = tax_dict_df[tax_dict_df.search_level == '1']
tax_dict1 = dict([(i, a) for i, a in zip(tax_dict_df1.og_taxon_term, tax_dict_df1.final_tax_term)])

# create second search dictionary
tax_dict_df2 = tax_dict_df[tax_dict_df.search_level == '2']
tax_dict2 = dict([(i, a) for i, a in zip(tax_dict_df2.og_taxon_term, tax_dict_df2.final_tax_term)])

# create third search dictionary
tax_dict_df3 = tax_dict_df[tax_dict_df.search_level == '3']
tax_dict3 = dict([(i, a) for i, a in zip(tax_dict_df3.og_taxon_term, tax_dict_df3.final_tax_term)])

# group the taxon dictionaries
tax_search_dictionaries = [tax_dict1, tax_dict2, tax_dict3]

print("TAXON DICTIONARY CREATION COMPLETE ", right_now)

#endregion

#region ELEMENT DICTIONARIES

# read in the element excel
elementdict_df = pd.read_excel(element_dict_excel)

# create element1 dictionary
element1_dict = dict([(i, a) for i, a in zip(elementdict_df.og_element_val, elementdict_df.element1)])

# drop rows with no element2 values
no_emptyel2 = elementdict_df.dropna(axis=0, subset='element2')

# create element2 dictionary
element2_dict = dict([(i, b) for i, b in zip(no_emptyel2.og_element_val, no_emptyel2.element2)])

print("ELEMENT DICTIONARY CREATION COMPLETE, ", right_now)

#endregion

#region TOOTHCLASS DICTIONARY

# read in the toothclass excel
toothclass_dict_df = pd.read_excel(toothclass_dict_excel)
toothclass_dict_df.fillna('', inplace=True)

# create toothclass dictionary
toothclass_dict = dict(
    [(i, a) for i, a in zip(toothclass_dict_df.og_toothclass_term, toothclass_dict_df.replacement_value)])

print("TOOTHCLASS DICTIONARY CREATION COMPLETE, ", right_now)

#endregion

#region TWS STRIP DICTIONARY

# read in tws strip excel
tws_dict_df = pd.read_excel(tws_dict_excel)
tws_dict_df.fillna('', inplace=True)

# create tws strip dictionary
tws_strip_dict = dict(
    [(i, a) for i, a in zip(tws_dict_df.og_tws_val, tws_dict_df.replace_val)])

print("TWS STRIP DICTIONARY CREATION COMPLETE, ", right_now)

# endregion

# region SYMMETRY STRIP DICTIONARY

# read in the symmetry strip excel
sym_dict_df = pd.read_excel(sym_dict_excel)
sym_dict_df.fillna('', inplace=True)

# create a symmetry strip dictionary
sym_strip_dict = dict(
    [(i, a) for i, a in zip(sym_dict_df.og_sym_term, sym_dict_df.new_sym)])

print("SYMMETRY STRIP DICTIONARY CREATION COMPLETE, ", right_now)

# endregion

# region PORTION DICTIONARY

# read in the portion dictionary excel
port_dict_df = pd.read_excel(portion_dict_excel)
port_dict_df.fillna('', inplace=True)

# create the portion dictionary
port_dict = dict(
    [(i,a) for i, a in zip(port_dict_df.og_term, port_dict_df.replacement)])

# endregion

# region BURN DICTIONARY

# read in the burn dictionary excel
burn_dict_df = pd.read_excel(burn_dict_excel)
burn_dict_df.fillna('', inplace=True)

# create the burn dictionary
burn_dict = dict(
    [(i,a) for i, a in zip(burn_dict_df.og_value, burn_dict_df.replacement)])

# endregion

# region LOCUS TYPE AND AGENT DICTIONARIES

# create locus type dictionary
type_dict_df = pd.read_excel(locus_type_excel)
type_dict_df['assignment'] = type_dict_df['assignment'].astype(str)
#type_dict_df['assignment'] = type_dict_df['assignment'].str[0]
type_dict = dict([(i, a) for i, a in zip(type_dict_df.loci_type, type_dict_df.assignment)])

# create locus agent dictionary
agent_dict_df = pd.read_excel(locus_agent_excel)
agent_dict_df['assignment'] = agent_dict_df['assignment'].astype(str)
#agent_dict_df['assignment'] = agent_dict_df['assignment'].str[0]
agent_dict = dict([(i, a) for i, a in zip(agent_dict_df.loci_agent, agent_dict_df.assignment)])

# create manual keep-locus dictionary

# endregion

# region KEEP DICTIONARIES

keep_dict_df = pd.read_excel(keep_code_excel).astype(str)
keep_dict = dict([(i, a) for i, a in zip(keep_dict_df.code, keep_dict_df.keep)])

# endregion


#region MANUAL KEEP DICTIONARY

# import the manual keep dictionary and simplify it into a new dataframe
bone_loci_df = pd.read_excel(manual_keep_xl, area)
extra_bone_df2 = pd.DataFrame()
extra_bone_df2['locus'] = bone_loci_df['locus']
extra_bone_df2['keep2'] = bone_loci_df['keep']

#endregion


#region AREA PERIOD DICTIONARY

# import the period dictionary
period_dict_xl = pd.ExcelFile(period_dict_excel)
period_dict_df = pd.read_excel(period_dict_xl, area)
period_dict_df['og_phase'] = period_dict_df['og_phase'].replace(r'\n', ' ', regex = True)
period_dict = dict(
    [(i,a) for i,a in zip(period_dict_df.og_phase, period_dict_df.period)])




#endregion

# assign .txt files for searches
age_search = open(cwd + '/term_searches/age_search.txt')
age_search = age_search.read().split(',')
bsm_search = open(cwd + '/term_searches/bsm_search.txt')
bsm_search = bsm_search.read().split(',')
fus_search = open(cwd + '/term_searches/fus_search.txt')
fus_search = fus_search.read().split(',')
tws_search = open(cwd + '/term_searches/fus_search.txt')
tws_search = tws_search.read().split(',')
toothclass_search = open(cwd + '/term_searches/toothclass_search.txt')
toothclass_search = toothclass_search.read().split(',')

print("SEARCH LISTS IMPORTED, ", right_now)

print("DICTIONARIES AND LISTS IMPORTED, ", right_now)

#%% STEP 3: GRAB NOTES AND DESCRIPTION COLUMNS AND PUT IN COMBINED NOTES COLUMN IN FINAL_DF

final_df['Notes'] = og_df['Notes'] + '|' + og_df['Description']



#%% STEP 4: INSERT CONTEXT INFORMATION
# Insert context information into new area, locus, and pail columns. ORIGINAL EXCEL FILE MUST HAVE PATH -1, PATH -2, AND PATH -3 COLUMNS IN ORDER FOR THIS SECTION TO WORK!

context_cols = ['area', 'locus', 'pail']
pail_col = og_df['Path -1']
final_df.insert(0, "pail", pail_col)

locus_col = og_df['Path -2']
final_df.insert(0, 'locus', locus_col)

area_col = og_df['Path -3']
final_df.insert(0, 'area', area_col)

phase_col = og_df['Periods (inherited/related)']
final_df.insert(0, 'phase', phase_col)

# corrections for some of the context information being in the wrong columns
correct_pail = final_df['pail'].str.contains("^P[012]", regex=True)
final_df.loc[~correct_pail, context_cols] = final_df.loc[~correct_pail, context_cols].astype(str).shift(axis=1)
final_df['area'].fillna(value="Area 8", inplace=True)

print("CONTEXT INFORMATION CLEANING COMPLETE, ", right_now)


#%% STEP 5: TAXON CLEANING

tax_df = og_df.filter(regex='taxon')
tax_cols = list(tax_df.columns.values)
ntax_cols = len(tax_cols)
tax_index = 0
unique_vals = set(np.concatenate(tax_df.values))


# execute a search of each row according to the defined dictionary levels.

tax_result_count = 0
tax_no_result_count = 0
tax_results_col_temp = []

for index, row in tax_df.iterrows():
    result = None
    found_flag = 0
    search_columns = [row[0],
                      row[1],
                      row[2],
                      row[3],
                      row[4],
                      row[5],
                      row[6],
                      row[7],
                      row[8],
                      row[10]]

    for search_level in tax_search_dictionaries:
        if found_flag == 0:
            for search_term in search_level:
                for items in row.iteritems():
                    if search_term in items:
                        found_flag = 1
                        result = search_level[search_term]
                        break

    if found_flag == 0:
        tax_no_result_count += 1
        result = "FAILED_CLEANUP"
    else:
        tax_result_count += 1

    # save the results of the search to tax_results_col_temp
    tax_results_col_temp.append(result)

# save the tax_results_col_temp to the final dataframe
final_df['taxon'] = tax_results_col_temp

print('\nTAXON ENTRIES SUCCESSFULLY CLEANED:', tax_result_count, '\nFAILED TAXON ROWS:', tax_no_result_count)
print('\nTAXON CLEANING COMPLETE')




#%% STEP 6: ELEMENT CLEANING
element_df = og_df.filter(regex='Skeletal element$')
og_element_vals = set(np.concatenate(element_df.values))
el_cols = list(element_df.columns.values)
nel_cols = len(el_cols)

# region build and execute a search device for the element1 column
element1_result_count = 0
element1_no_result_count = 0
element1_results_col_temp = []

for index, row in element_df.iterrows():
    result = None
    found_flag = 0

    for search_term in element1_dict:
        if found_flag == 0:
            for items in row.iteritems():
                if search_term in items:
                    found_flag = 1
                    result = element1_dict[search_term]
                    break

    if found_flag == 0:
        element1_no_result_count += 1
        result = "FAILED_CLEANUP"
    else:
        element1_result_count += 1

    element1_results_col_temp.append(result)

final_df['element1'] = element1_results_col_temp  # this will later be appended to the final_df

print('\nELEMENT1 ENTRIES SUCCESSFULLY CLEANED:', element1_result_count, '\nFAILED ELEMENT1 ROWS:', element1_no_result_count)
print()

# endregion

# region build and execute a search device for the element2 column


element2_result_count = 0
element2_no_result_count = 0
element2_results_col_temp = []

for index, row in element_df.iterrows():
    result = None
    found_flag = 0

    for search_term2 in element2_dict:
        if found_flag == 0:
            for items in row.iteritems():
                if search_term2 in items:
                    found_flag += 1
                    result = element2_dict[search_term2]
                    break

    if found_flag == 0:
        element2_no_result_count += 1
        result = ''
    else:
        element2_result_count += 1

    element2_results_col_temp.append(result)

final_df['element2'] = element2_results_col_temp

print('\nELEMENT2 ENTRIES SUCCESSFULLY CLEANED:', element2_result_count, '\nFAILED ELEMENT2 ROWS:',
      element2_no_result_count)
# endregion





#%% STEP 7: DENTISTRY/TOOTH CLEANING

tooth_df.columns = tooth_df.columns.str.replace('Skeletal element/Tooth/Tooth, ', '')


# use string replacements in order to clean up perm/decid column
tooth_df['type'] = tooth_df['type'].str.replace("Permanent", "p")
tooth_df['type'] = tooth_df['type'].str.replace("Deciduous", "d")
tooth_df['type'] = tooth_df['type'].str.replace(";", ",")


# pull tooth data from the tooth class columns
tooth_df['new_tooth_class'] = tooth_df['class']
tooth_df = tooth_df.rename(columns={'class.1': 'molar_class'})
tooth_df["new_tooth_class"].fillna(tooth_df['molar_class'], inplace=True)

# also pull tooth data from description column based on if it contains any of your toothclass search terms
contains_filter = '|'.join(toothclass_search)
tooth_df.loc[tooth_df["Description"].str.contains(contains_filter, na=False), "new_tooth_class"] = tooth_df[
    "Description"]

# clean up the data with your toothclass dictionary as well as some standard string corrections
tooth_df["new_tooth_class"] = tooth_df["new_tooth_class"].replace(toothclass_dict, regex=True)
tooth_df["new_tooth_class"] = tooth_df["new_tooth_class"].replace(".~", "", regex=True)
tooth_df["new_tooth_class"] = tooth_df["new_tooth_class"].str.lower()
tooth_df['new_tooth_class'] = tooth_df['new_tooth_class'].replace('m2/m1', 'm1/2', regex=False)
tooth_df['new_tooth_class'] = tooth_df['new_tooth_class'].replace('mm', 'm', regex=False)

# put wear stage info into new tws column
tooth_df['tws'] = ''
# tooth_df["tws"] = tooth_df["Grant wear stage"]
# tooth_df["tws"].fillna(tooth_df["Payne wear stage"], inplace=True)

# grab values from notes column with TWS or G. information
tooth_df.loc[tooth_df["Notes"].str.contains(tws_contains_filter, na=False), "tws"] = tooth_df["Notes"]

# clean up new tws column
tooth_df['tws'] = tooth_df['tws'].replace(tws_strip_dict, regex=True)
tooth_df['tws'] = tooth_df['tws'].replace(r'\r+|\n+|\t+', '', regex=True)
tooth_df['tws'] = tooth_df['tws'].replace(r'MW...', '', regex=True)
tooth_df['tws'] = tooth_df['tws'].str.strip()

# get rid of weird G- prefixes on the Grant wear stages
for letter in string.ascii_lowercase:
    tooth_df['tws'] = tooth_df['tws'].replace("G%s" % letter, letter, regex=True)

for letter in string.ascii_letters:
    tooth_df['tws'] = tooth_df['tws'].replace("Payne %s" % letter, "P%s |" % letter, regex=True)

# paste all of this onto the final_df
final_df['tooth'] = tooth_df['new_tooth_class']
final_df['tooth_p/d'] = tooth_df['type']
final_df['tws'] = tooth_df['tws']

print("DENTISTRY CLEANING COMPLETE")

#%% STEP 8: SYMMETRY CLEANING

# put symmetry values from original data frame into final data frame
final_df['side'] = og_df["RF/Faunal symmetry"]

# use strip dictionary to standardize the notation of the symmetry values
final_df['side'] = final_df['side'].str.lower()
final_df['side'] = final_df['side'].replace(sym_strip_dict, regex=True)

# simplify the notation of symmetry values
simple_sym_dict = {"right": "r",
                   "left": "l",
                   "central (median)": "med"}

final_df['side'] = final_df['side'].replace(simple_sym_dict, regex=False)

# shorten symmetry strings to get rid of weird trailing characters
final_df['side'] = final_df['side'].str[0:5]

print("SYMMETRY CLEANING COMPLETE")


#%% STEP 9: FUSION CLEANING

# pull fusion data from columns that contain fusion information
contains_fusion_filter = '|'.join(fus_search)
og_df = og_df.astype(str)
fus_mask = og_df.apply(lambda col: col.str.contains(contains_fusion_filter, flags = re.IGNORECASE).any(), axis=0)
fus_cols = og_df.loc[:, fus_mask].columns.format()

# put this fusion data into a new fusion dataframe
fus_temp = pd.DataFrame()
for column in fus_cols:
    fus_temp[str(column)] = og_df[column].str.findall(contains_fusion_filter, re.IGNORECASE)

# get rid of the weird brackets and non-alphabetic characters
fus_temp = fus_temp.astype(str)
fus_temp = fus_temp.replace(r'\[|\]', '', regex = True)
fus_temp = fus_temp.replace(r'\W', '', regex = True)

# create a new column to collapse all the fusion data into
fus_temp['new_fusion'] = ''
fus_temp = fus_temp.replace('', np.NaN, regex=True)

#get rid of the notes column because we want to skip it in our backfill
# fus_cols.remove('Notes')

# fill the new fusion column with fusion data from each column using the backfill function that fills the na with the neareast non-na from the next column in the list
for col in fus_cols:
    fus_temp['new_fusion'] = fus_temp['new_fusion'].fillna(fus_temp[col])

# make everything lowercase
fus_temp['new_fusion'] = fus_temp['new_fusion'].str.lower()

# get rid of repeating strings of characters
fus_temp['new_fusion'] = fus_temp['new_fusion'].str.replace(r'(\w+)\1+', r'\1', regex = True)

final_df['fusion'] = fus_temp['new_fusion']


print("FUSION CLEANING COMPLETE")

#%% STEP 10: PULL D&R VALUES

# simply pull out the the Dobney and Reilly values from the original dataframe
final_df['d&r'] = og_df.filter(regex='Dobney & Rielly')

# pull out lingering fusion data from the D&R column and put it in the fusion column
final_df['d&r'] = final_df['d&r'].astype(str)
final_df.loc[(final_df['d&r'].str.contains("UNFUSED", case="False")), 'fusion'] = "unfused"
final_df['d&r'] = final_df['d&r'].replace("~UNFUSED", "", regex=True)
final_df.loc[(final_df['d&r'].str.contains("FUSED", case="False")), 'fusion'] = "fused"
final_df['d&r'] = final_df['d&r'].replace("~FUSED", "", regex=True)

#clean off any weird trailing characters
final_df['d&r'] = final_df['d&r'].replace(".[a-zA-Z]+\s?[a-zA-Z]+$", "", regex=True)

print("DOBNEY AND REILLY CLEANING COMPLETE")


#%% STEP 11: CLEAN PORTION COLUMN

# pull portion information
final_df['portion'] = og_df['RF/Skeletal element portion']
final_df['portion'] = final_df['portion'].str.lower()

# quickly standardize terminology for shafts and ends
port_prep_dict = {"diaphysis": "end",
                  "metaphysis": "shaft"}
final_df['portion'] = final_df['portion'].replace(port_prep_dict, regex=True)

# use portion dictionary and replace phrases to standardize portions
final_df['portion'] = final_df['portion'].replace(port_dict, regex=True)
final_df['portion'] = final_df['portion'].replace("fragment(s)", "frag", regex=False)
final_df['portion'] = final_df['portion'].replace("[\(]\w*[\)]", "", regex=True)
final_df['portion'] = final_df['portion'].replace("\d", "", regex=True)
final_df['portion'] = final_df['portion'].replace("~", "", regex=False)

print("PORTION CLEANING COMPLETE")

#%% STEP 12: CLEAN PORTION PERCENTAGE INFORMATION


# pull out the percentage-related columns
perc_df = og_df.filter(regex="Percentage")

# simplify column names to make things clearer
perc_df.columns = perc_df.columns.str.replace("Skeletal element portion/", "", regex=True)
perc_df.columns = perc_df.columns.str.replace("/Percentage preserved (%)", "", regex=False)
perc_df.columns = perc_df.columns.str.strip()
perc_df = pd.concat([perc_df, final_df['portion']], axis=1)

# assuming all of the percentages are conglomerated in all of the columns, grab the string out of the first column and clean it up
perc_df['allpercents'] = perc_df['/P'].str.replace(";", ",", regex=False)

# turn each cell of percent lists into a string for cleaning
perc_df['allpercents'] = perc_df['allpercents'].astype('str')

# get rid of weird space characters and split again to re-make it a list for zipping
perc_df['allpercents'] = perc_df['allpercents'].str.replace('\s', '', regex=True).str.split(',')

# grab the lists of portions present and turn them into strings for cleaning
perc_df['portion'] = perc_df['portion'].astype('str')

# get rid of weird space characters and split again to make it a list for zipping
perc_df['portion'] = perc_df['portion'].str.replace('\s', '', regex=True).str.split(',')

# zip the lists of portions and percents together
percents_zip = list(list(zip(a, b)) for a, b in zip(perc_df['portion'], perc_df['allpercents']))

# turn that zipped list into a dataframe with portions as cleaned column headers
cleaned_percents = pd.DataFrame(map(dict, percents_zip))
cleaned_percents.columns = cleaned_percents.columns.str.strip()

# move the cleaned percent columns into the final dataframe
final_df['%pe'] = cleaned_percents['pe']
final_df['%ps'] = cleaned_percents['ps']
final_df['%ms'] = cleaned_percents['ms']
final_df['%ds'] = cleaned_percents['ds']
final_df['%de'] = cleaned_percents['de']


#alternative percentage cleaning for when its already sorted in the exported OCHRE file
#final_df['%pe'] = perc_df['P']
#final_df['%ps'] = perc_df['PS']
#final_df['%ms'] = perc_df['MS']
#final_df['%ds'] = perc_df['DS']
#final_df['%de'] = perc_df['D']

print("PORTION PERCENTAGE CLEANING COMPLETE")

#%% STEP 13: PULL AND CLEAN METRIC INFORMATION

# create a dataframe to hold the clean, sorted metrics
metrics_df = pd.DataFrame()

# pull all metric columns and drop the empty ones
og_metrics = og_df.filter(regex="Metrics")
og_metrics.dropna(axis=1, how="all", inplace=True)

# clean the names of the remaining metric columns
og_metrics.columns = og_metrics.columns.str.replace("Faunal analysis/Metrics/", "")
og_metrics.columns = og_metrics.columns.str.replace("(mm)", "")
og_metrics.columns = og_metrics.columns.str.replace('\W', '', regex=True)

# convert the values into integers
og_metrics.astype('float', errors='ignore')
og_metrics = og_metrics.add_suffix('(mm)')
metric_col_names = list(og_metrics.columns)

# append these metric columns to the metrics dataframe, giving it the name we want
metrics_df = pd.concat([metrics_df, og_metrics], axis=1)

# look for potential metric values in Notes or Description columns
extra_metric_names = ["DEM", "DEL", "DVL", "DVM", "WT", "BC", "DLS", "Dd", "Bd", "GB", 'Bb', 'Bd', 'Bp', 'Dd', "Dp",
                      'Dl', 'Dm', 'GB', 'GLl', 'GLm', 'Glpe', 'CH']

# create and fill a column with the extra metric observations found in Notes or Description
og_df['extra_metrics'] = ''
metric_contains_filter = '|'.join(metric_col_names + extra_metric_names)
og_df.loc[og_df["Notes"].str.contains(metric_contains_filter, na=False), "extra_metrics"] = og_df["Notes"]
og_df.loc[og_df["Description"].str.contains(metric_contains_filter, na=False), "extra_metrics"] = og_df["Description"]

# pull out measurement observations with regex expression and put them in a new data frame
metrics_df = pd.concat([metrics_df, og_df['extra_metrics']], axis=1)
m = metrics_df['extra_metrics'].str.findall(r'([\w]+)\s?[=|-]\s?([\d\d..?]+)')
from_notes_df = pd.DataFrame(map(dict, m))
from_notes_df = from_notes_df.add_suffix('(mm)')
from_notes_df = from_notes_df.astype('float', errors='ignore')

# combine the pulled measurement observations with the metrics holding dataframe
metrics_df = metrics_df.combine_first(from_notes_df)
metrics_df.drop(columns="extra_metrics", inplace=True)

# append all measurement observations to final dataframe
final_df = pd.concat([final_df, metrics_df], axis=1)

print("METRICS CLEANING COMPLETE")

#%% STEP 14: PULL AND CLEAN WEATHERING INFORMATION

# find columns with specific weathering information

weather_col = og_df.filter(regex='Weather').columns.format()[0]
final_df['weather_stage'] = og_df[weather_col].str.extract('(\d)')

print("WEATHERING CLEANING COMPLETE")


#%% STEP 15: PULL AND CLEAN SEX-RELATED INFORMATION

#define the regex that will find sex-related information
sex_regex = "(\w*?male)"

# find columns that contain the sex-related information, these are only the Notes and RF/Sex columns in our dataset
sex_mask = og_df.apply(lambda col: col.str.contains(sex_regex).any(), axis=0)
sex_cols = og_df.loc[:, sex_mask].columns.format()

# put sex-related info from the RF/Sex column in the final data frame and replace any nan-strings with an actual NaN value
#final_df['sex'] = og_df[sex_cols[0]].replace('nan', np.NaN)
final_df['sex'] = ''

# pull out the sex-related information from the Notes column
final_df.loc[final_df['Notes'].str.contains(sex_regex, na=False), 'sex2'] = final_df['Notes']

# combine the Notes sex-related information
final_df['sex'] = final_df['sex'].combine_first(final_df['sex2'])
final_df.drop('sex2', axis=1, inplace=True)

#clean up the sex-related information in the final dataframe
final_df['sex'] = final_df['sex'].str.lower()
final_df['sex'] = final_df['sex'].str.extract(sex_regex)

print("SEX INFO CLEANING COMPLETE")


#%% STEP 16: PULL AND CLEAN AGE-RELATED INFORMATION

# find columns with age-related information
age_filter = '|'.join(age_search)
age_mask = og_df.apply(lambda col: col.str.contains(age_filter, re.IGNORECASE).any(), axis=0)
age_cols = og_df.loc[:, age_mask].columns.format()

# pull our age terms from these columns and put them in a temporary df
age_temp = pd.DataFrame()
for column in age_cols:
    age_temp['age' + str(age_cols.index(column))] = og_df[column].str.findall(age_filter, re.IGNORECASE)

# combine these values into a single column and take out any non-alphanumeric values
age_temp['combined'] = age_temp.values.tolist()
age_temp['combined'] = age_temp['combined'].astype(str).replace(r'\W', '', regex=True)
final_df['age'] = age_temp['combined']

print("AGE INFO CLEANING COMPLETE")



#%% STEP XX: ASSIGN FRACTURE CODES

og_df['f1'] = ''
og_df['f2'] = ''
og_df['f3'] = ''


dir_col = [i for i in og_column_names if 'direction' in i]
style_col = [i for i in og_column_names if 'style' in i]
js_col = [i for i in og_column_names if 'jagged' in i]

og_df.loc[og_df[dir_col[0]].str.contains('Oblique', na=False), 'f1'] = 'o'
og_df.loc[og_df[dir_col[0]].str.contains('Right', na=False), 'f1'] = 'r'

og_df.loc[og_df[style_col[0]].str.contains("Curved", na=False), 'f2'] = 'c'
og_df.loc[og_df[style_col[0]].str.contains("Transverse", na=False), 'f2'] = 't'

og_df.loc[og_df[js_col[0]].str.contains("Jagged", na=False), 'f3'] = 'j'
og_df.loc[og_df[js_col[0]].str.contains("smooth", na=False), 'f3'] = 's'

og_df['fracture'] = og_df['f1'] + og_df['f2'] + og_df['f3']
final_df['fracture'] = og_df['fracture']


#%% STEP 17: PULL AND CLEAN ANY BSM INFORMATION

# define the terms that you'll be searching for
mod_filter = '|'.join(bsm_search)
mod_mask = og_df.apply(lambda col: col.str.contains(mod_filter, flags=re.IGNORECASE).any(), axis=0)
mod_df = og_df.loc[:, mod_mask]
mod_df = mod_df.loc[:, ~mod_df.columns.str.contains("Fracture")]
mod_cols = mod_df.columns.format()

# pull and translate the burn values from the column that is supposed to hold burning data
burn_col = pd.Series(og_df.filter(regex="burn").columns.format()).get(0)
mod_df['burning'] = og_df[burn_col].replace(burn_dict, regex=False)
mod_df['burning'] = mod_df['burning'].replace(r'^\s*$', np.nan, regex=True)

# now pull out BSM information into a separate dataframe before collapsing it and cleaning it
mod_temp = pd.DataFrame()
for column in mod_cols:
    mod_temp['%s' % column + str(mod_cols.index(column))] = og_df[column].str.findall(mod_filter, re.IGNORECASE)

# collapse it into a single column
mod_df['concat'] = mod_temp.values.tolist()
mod_df['concat'] = mod_df['concat'].astype(str)

# clean up weird brackets and single-quotes and make it all lowercase
mod_df['concat'] = mod_df['concat'].str.replace(r"'\]\['", ', ', regex=True)
mod_df['concat'] = mod_df['concat'].str.replace(r"\[|\]|'", '', regex=True)
mod_df['concat'] = mod_df['concat'].str.replace(r'\b(\w+)(.+\1)+\b', r'\1', regex=True)
mod_df['concat'] = mod_df['concat'].str.replace(r'(^,\W*)|(\W?\W?,\W?$)', '', regex=True)
mod_df['concat'] = mod_df['concat'].str.replace(r'(\W \W)', '', regex=True)
mod_df['concat'] = mod_df['concat'].str.lower()

# pull extra burn information that might be lying around in the concatenated column

mod_df.loc[(mod_df['burning'].str.contains('nan', na=False) & mod_df['concat'].str.contains('burn', na=False, flags=re.IGNORECASE)), 'burning'] = mod_df['concat']

# put it in the final dataframe
final_df['burn'] = mod_df['burning']
final_df['bsm'] = mod_df['concat']

print("BSM INFO CLEANING COMPLETE")

#%% STEP 18: PULL BUTCHERY INFORMATION

butchery_col = og_df['/Bone modification/Cutmark(s)/Butchery notation']
final_df['butchery'] = butchery_col

print("BUTCHERY INFO CLEANING COMPLETE")

#%% STEP 19: PULL AND CLEAN OBSERVER INFORMATION

final_df['observer'] = og_df['Observer'].str.extract(r'[^Observer(s):]\s(\w*)(?=,)')

print("OBSERVER INFO CLEANING COMPLETE")

#%% STEP 20: ASSIGN LOCI PRIORITIES

# create a new column based on type and use a replace function to put in the priority code
final_loci_df['type_code'] = final_loci_df['type']
final_loci_df['type_code'] = final_loci_df['type_code'].replace(type_dict, regex=False)
final_loci_df['type_code'] = final_loci_df['type_code'].str[0]

# create a new column based on agent and use a replace function to put in the priority code
final_loci_df['agent_code'] = final_loci_df['agent']
final_loci_df['agent_code'] = final_loci_df['agent_code'].replace(agent_dict, regex=False)
final_loci_df['agent_code'] = final_loci_df['agent_code'].str[0]

#create a column that combines the type and agent codes
final_loci_df['priority_code'] = final_loci_df['type_code'] + final_loci_df['agent_code']
final_loci_df = final_loci_df.drop(['type_code', 'agent_code'], axis=1)

# use keep dictionaries to label which loci to keep
final_loci_df['keep'] = final_loci_df['priority_code'].replace(keep_dict, regex=True)
final_loci_df = pd.concat([final_loci_df, extra_bone_df2], ignore_index=True)
final_loci_df.loc[final_loci_df['keep2'].str.contains('yes|no', na=False), 'keep'] = final_loci_df['keep2']

#create a keep column for dictionary creation
final_loci_df.drop_duplicates(subset = ['locus'], keep='first', inplace=True)
keep_locus_dict = dict([(i,a) for i, a in zip(final_loci_df.locus, final_loci_df.keep)])
final_df['keep'] = final_df['locus']
#final_df.insert(3, 'keep', final_df['locus'], allow_duplicates=True)
#final_df.insert(1, 'priority_code', final_loci_df['priority_code'], allow_duplicates=True)
final_df['keep'].replace(keep_locus_dict, regex=False, inplace=True)
priority_code_dict = dict([(i,a) for i, a in zip(final_loci_df.locus, final_loci_df.priority_code)])
final_df['priority_code'] = final_df['locus']
final_df['priority_code'].replace(priority_code_dict, regex=False, inplace=True)
final_df['keep'].replace(r"L.*", "no", regex=True, inplace=True)





print("LOCI CLEANING RUN COMPLETE %s, " % right_now)


#%% STEP 21: ASSIGN PERIOD INFORMATION

final_df['period'] = final_df['phase']
final_df['period'] = final_df['period'].replace('r(\s)', 'r(\v')
final_df['period'] = final_df['period'].replace(period_dict)

print("PERIODS ASSIGNED, %s " % right_now)

#%% STEP 22: FINAL CLEANING

# reindex the columns
metric_col_names = list(metrics_df.columns)

final_col_order = ['area','phase', 'period', 'priority_code', 'keep', 'observer', 'locus', 'pail', 'taxon', 'element1', 'element2', 'tooth', 'tooth_p/d', 'tws', 'side', 'fusion', 'd&r', 'portion', '%pe', '%ps', '%ms', '%ds', '%de', '%complete', 'sex', 'age', 'bsm', 'burn', 'weather_stage', 'butchery', 'fracture', 'Notes', *metric_col_names]
final_df = final_df.reindex(columns = final_col_order)

# basic cleaning and standardization
final_df = final_df.replace('', np.nan, regex=True)
final_df = final_df.replace('<unassigned>', '', regex=True)
final_df = final_df.replace('^/s*$', '', regex=True)
final_df = final_df.replace('nan', np.nan, regex=True)
final_df = final_df.replace('<unassigned>', np.nan, regex=True)

print("FINAL CLEANING COMPLETE")

#%% STEP 23: EXPORT FINAL DATAFRAME TO EXCEL

final_df.to_excel(cwd + '/clean_datasets/%s_clean_faunal_data.xlsx' % area)

print("FINAL DATAFRAME EXPORTED")

print("OCHRE CLEANING RUN COMPLETE")


'''
#%% STEP 24: COMBINE THIS WITH MANUALLY COLLECTED DATA

import glob
import pandas as pd

#combine all the cleaned OCHRE datasets into a single dataset

OCHRE_cleaned_folder = "/Users/laurelpoolman/PycharmProjects/BoneWasher/clean_datasets"
OCHRE_filenames = glob.glob(OCHRE_cleaned_folder + "/*.xlsx")

excel_list = []

for file in OCHRE_filenames:
    excel_list.append(pd.read_excel(file))

combined_df = pd.concat(excel_list, ignore_index=True)


# import all the manually collected datasets

manual_folder = '/Users/laurelpoolman/PycharmProjects/BoneWasher/manual_collections'
manual_filenames = glob.glob(manual_folder + '/*.xlsx')
num_man_files = len(manual_filenames)
manual_excel_list = []

for file in manual_filenames:
    data = pd.read_excel(file, )
    manual_excel_list.append(data)



clean_manual_df = pd.DataFrame(columns = ['area','phase', 'period', 'priority_code', 'keep', 'observer', 'locus', 'pail', 'taxon', 'element1', 'element2', 'tooth', 'tooth_p/d', 'tws', 'side', 'fusion', 'd&r', 'portion', '%pe', '%ps', '%ms', '%ds', '%de', '%complete', 'sex', 'age', 'bsm', 'burn', 'weather_stage', 'butchery', 'Notes'])

#insert pail information




print("COMBINATION RUN COMPLETE")



'''