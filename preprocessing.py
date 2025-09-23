import json
import sqlparse
import re

def load_dataset(file_path):
    # Loading JSON dataset
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)
    
def normalize_sql(query):
    # Formatting sql queries
    # It adds all the /n where necessary, transforms sql statements in upper case
    normalized_query = sqlparse.format(query, reindent=True, keyword_case="upper")
    return normalized_query

def remove_duplicates(dataset):
    #Removing duplicate quesions or queries from dataset
    seen = set() # this set will contain all questions which have been already read
    cleaned_data = [] #this list will cotain all questions which we accept
    for item in dataset:
        key = (item["question"].lower(), item["sql_query"].lower())
        # If the question was not seen previously add it to the final dataset
        if key not in seen:
            seen.add(key)
            cleaned_data.append(item)

    return cleaned_data

def preprocess_dataset(input_file,output_file):
    dataset = load_dataset(input_file)

    for item in dataset:
        item["sql_query"] = normalize_sql(item["sql_query"])

    dataset = remove_duplicates(dataset)

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(dataset, file, indent=4)

    print(f"Processed dataset saved to {output_file}")

if __name__=="__main__":
    preprocess_dataset("../data/sample_queries.json","../data/processed_queries.json")