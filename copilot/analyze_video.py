
# =====================================================
# Usecase#2 : Program Development Copilot - Autism Hackathon 2024
# https://github.com/fsi-hack4autism/program-development-copilot/tree/main
# (1) Analyze Video Data and extract insights
# (2) Design an AI co-pilot to generate a personalized plan based on the insights
# (3) Use the AI co-pilot with recorded history to recommend a plan for the new subject 
# created by: Noha Elprince
# created on: April 03, 2024
# last updated on: April 04, 2024
#
# ================== START SCRIPT =================
#%%
# import required libraries
import azure.core.credentials
from azure.storage.blob import BlobServiceClient
import requests
import os
from azure.core.credentials import AzureKeyCredential
from azure.storage.blob import BlobServiceClient, BlobClient

import re
import pandas as pd
#%%
# Acess Azure Blob Storage from Python
# get the connection string from the Azure portal, under the Access keys section
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
# List all containers
all_containers = blob_service_client.list_containers(include_metadata=True)
for container in all_containers:
    print(container['name'])
    # Additional metadata about the container can also be accessed if needed.
#%%
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
# Container clients
videos_container_client = blob_service_client.get_container_client("videos")
data_container_client = blob_service_client.get_container_client("data")
ablls_data_container_client = blob_service_client.get_container_client("ablls-data")
#%%
# Process videos
blobs = videos_container_client.list_blobs()
for blob in blobs:
    print("Processing video:", blob.name)
    # Add code to process videos here
# Process PDFs and docs
blobs = data_container_client.list_blobs()
for blob in blobs:
    print("Processing file:", blob.name)
    # Add code to process PDFs and doc files here
# Process ABLLS assessment data
blobs = ablls_data_container_client.list_blobs()
for blob in blobs:
    print("Processing ABLLS data:", blob.name)
    # Add code to process ABLLS data here
#%% # Analyze video using Azure Video Indexer
# Set up your Azure Blob Storage connection
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
blob_service_client = BlobServiceClient.from_connection_string(connect_str)
container_client = blob_service_client.get_container_client("videos")
#%%
def get_access_token(subscription_key, location, account_id):
    url = f'https://api.videoindexer.ai/auth/{location}/Accounts/{account_id}/AccessToken'
    headers = {'Ocp-Apim-Subscription-Key': subscription_key}
    params = {'allowEdit': 'true'}
    response = requests.get(url, headers=headers, params=params)
    token = response.json()
    return token

# Get the access token : https://api-portal.videoindexer.ai/profile
subscription_key = os.getenv('VIDEO_INDEXER_SUBSCRIPTION_KEY')
location =   "trial"
account_id = os.getenv('VIDEO_INDEXER_ACCOUNT_ID')

access_token = get_access_token(subscription_key, location, account_id)

#%% 
#===========  (1) Analyze Video Data and extract insights ==============


# upload videos on Video Indexer 
def get_video_insights(access_token, location, account_id, video_id):
    url = f'https://api.videoindexer.ai/{location}/Accounts/{account_id}/Videos/{video_id}/Index'
    params = {'accessToken': access_token}
    response = requests.get(url, params=params)
    return response.json()

# get video insights
def extract_key_information_from_insights(insights):
    # Initialize all variables to ensure they are defined even if parts of the structure are missing
    keywords, sentiments, named_people, labels, topics, emotions, languages, transcript_lines = ([] for i in range(8))
    duration = 0

    # Check and extract summarized insights if available
    if 'summarizedInsights' in insights:
        summarized_insights = insights['summarizedInsights']
        
        keywords = [keyword['name'] for keyword in summarized_insights.get('keywords', [])]
        
        sentiments_list = summarized_insights.get('sentiments', [])
        sentiments = sentiments_list[0]['sentimentKey'] if sentiments_list else "Unknown"
        
        named_people = [person['name'] for person in summarized_insights.get('namedPeople', [])]
        
        labels = [label['name'] for label in summarized_insights.get('labels', [])]
        
        topics = [topic['name'] for topic in summarized_insights.get('topics', [])]

        emotions = set()
        for emotion in summarized_insights.get('emotions', []):
            emotion_type = emotion.get('type')
            if emotion_type:  # Ensure emotion_type is not None
                emotions.add(emotion_type)
        
        duration = summarized_insights.get('duration', {}).get('seconds', 0)
        
        languages = summarized_insights.get('languages', [])

    # Extracting transcripts from videos insights
    if 'videos' in insights:
        for video in insights['videos']:
            video_insights = video.get('insights', {})
            if isinstance(video_insights, dict):  # Proceed if video_insights is a dictionary
                for transcript in video_insights.get('transcript', []):
                    line = transcript.get('text', '')
                    instances = transcript.get('instances', [{}])[0]
                    start_time = instances.get('start', '')
                    end_time = instances.get('end', '')
                    speaker_id = transcript.get('speakerId', None)

                    transcript_line = {
                        'text': line,
                        'start_time': start_time,
                        'end_time': end_time,
                        'speaker_id': speaker_id
                    }
                    transcript_lines.append(transcript_line)

    # Compiling all extracted information into a single dictionary
    key_information = {
        'keywords': keywords,
        'sentiments': sentiments,
        'named_people': named_people,
        'labels': labels,
        'topics': topics,
        'emotions': list(emotions),
        'duration_in_seconds': duration,
        'languages': languages,
        'transcript': transcript_lines
    }

    return key_information

# upload videos from local storage
def upload_video_local(access_token, location, account_id, video_path, video_name):
    video_id = None
    url = f'https://api.videoindexer.ai/{location}/Accounts/{account_id}/Videos'
    params = {
        'accessToken': access_token,
        'name': video_name,
        'privacy': 'Public',  # or 'Private'
        'videoUrl': '',       # Leave empty if uploading a file
    }
    with open(video_path, 'rb') as video_file:
        files = {'file': video_file}
        response = requests.post(url, params=params, files=files)
        response_json = response.json()

        if 'ErrorType' in response_json and response_json['ErrorType'] == 'ALREADY_EXISTS':
            # Improved extraction of video_id from the error message
            video_id = response_json.get('Message').split("'")[1]
        else:
            video_id = response_json.get('id')

    return video_id


# List to collect data before creating DataFrame
data = []

video_folder_path = '/data/video_01'

# Iterate over video files in the specified directory
for filename in os.listdir(video_folder_path):
    if filename.endswith('.mp4'):  # Check if the file is a video
        video_path = os.path.join(video_folder_path, filename)
        video_id = upload_video_local(access_token, location, account_id, video_path, filename)
        video_insights = get_video_insights(access_token, location, account_id, video_id)
        print(f'Video insights for {filename}: {video_insights}')
        key_information = extract_key_information_from_insights(video_insights)
        
        # Corrected way to add key_information's content to the data list
        data.append({
            'Video Name': filename, 
            'Video ID': video_id, 
            'keywords': ', '.join(key_information['keywords']),  # Join list items into a string
            'sentiments': key_information['sentiments'],
            'named_people': ', '.join(key_information['named_people']),  # Join list items into a string
            'labels': ', '.join(key_information['labels']),  # Join list items into a string
            'topics': ', '.join(key_information['topics']),  # Join list items into a string
            'emotions': ', '.join(key_information['emotions']),  # Join list items into a string
            'duration_in_seconds': key_information['duration_in_seconds'],
            'languages': ', '.join(key_information['languages']),  # Join list items into a string
            'transcript': ' | '.join([f"{t['text']} ({t['start_time']}-{t['end_time']})" for t in key_information['transcript']])  # Format transcript entries
        })

# Create DataFrame from collected data
df = pd.DataFrame(data)

# Save the DataFrame to a CSV file
df.to_csv('out/video_insights.csv', index=False)
#print("DataFrame saved to 'out/video_insights.csv'.")

#%%
# =============== (2) Design an AI assistant to generate a personalized plan based on the insights ===============
# %%
from openai import OpenAI
import pandas as pd

# Set your OpenAI API key here
api_key = os.get_env('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)


def create_ai_assistant(dataframe):
    """
    Simulates an AI assistant that uses insights from video analysis to generate responses,
    :param dataframe: A DataFrame containing video insights.
    """
    responses = []  # Initialize a list to store responses
    # Iterate through each row in the DataFrame (each video's insights)
    for index, row in dataframe.iterrows():
        # Construct a prompt using insights extracted from a video
        prompt = construct_prompt_from_insights(row)
        
        # Query the OpenAI API with the prompt to generate a response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Adjust the model as necessary
            messages=[
                {"role": "system", "content": "You are a helpful assistant that uses insights from video analysis to generate a plan for autistic children"},
                {"role": "user", "content": prompt}
            ]
        )
        
        #print(f"Response to insights from video {row['Video Name']}: {response.choices[0].message.content}")
         # Extracting the response text
        ai_response = response.choices[0].message.content.strip()
        responses.append(ai_response)  # Add the response to the list
    
    # Add the responses as a new column to the DataFrame
    dataframe['AI Response'] = responses
    return dataframe

def construct_prompt_from_insights(row):
    """
    Constructs a detailed prompt for the AI model based on video insights, adapted for openai>=1.0.0.
    
    :param row: A row from the DataFrame containing insights for a single video.
    :return: A string prompt for the AI model.
    """
    
    prompt = (f"Based on the following insights from the video {row['Video Name']} of an Autism assessment therapy:\n"
              f"Keywords: {row['keywords']}\n"
              f"Sentiments: {row['sentiments']}\n"
              f"Topics: {row['topics']}\n"
              f"labels: {row['labels']}\n"
              f"emotions: {row['emotions']}\n"
              f"Subject names: {row['named_people']}\n"
              f"Duration in seconds: {row['duration_in_seconds']}\n"
              f"Please provide an analysis or suggest activities that could enhance engagement or educational value includes possible implications for future research or children mental development")
    return prompt
#
# %%
# read data
df = pd.read_csv('out/video_insights.csv')
df.shape
#%%
# Call the function with your DataFrame
df_response = create_ai_assistant(df)
df_response
#%%
df_response.to_csv('out/video_insights_with_AI_response.csv', index=False)
#%%
df_response.head()
#%%
df_response.columns
# %%
# ========== (3) Use the AI assistant with recorded history to recommend a plan for the new subject ==========

# step#1 - start with a summary of the new child's assessment. This summary should encapsulate key observations and findings from the assessment.
# example of a summary given by a terapist as an initial assesment
new_child_summary = "The child shows a keen interest in visual stimuli, responds well to auditory cues, \
and exhibits mild discomfort with sudden changes in environment. Prefers structured activities over free play."

#%% Step 2: Prepare the AI Interaction with History
def prepare_ai_interaction_with_history(new_child_summary, df_response):
    # Construct a prompt for the AI model based on the new child's summary and historical data
    prompt = construct_prompt_with_history(new_child_summary, df_response)
    
    # Query the OpenAI API with the prompt to generate a response
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Adjust the model as necessary
        messages=[
            {"role": "system", "content": "You are a helpful assistant that uses insights from video analysis to generate a plan for autistic children"},
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extracting the response text
    ai_response = response.choices[0].message.content.strip()
    return ai_response

def construct_prompt_with_history(new_child_summary, df_response):
    """
    Constructs a prompt for the AI model based on the new child's summary and historical data.
    
    :param new_child_summary: A summary of the new child's assessment.
    :param df_response: A DataFrame containing historical video insights and AI responses.
    :return: A string prompt for the AI model.
    """
    # Extracting the latest video insights and AI responses
    latest_insights = df_response.iloc[-1]
    latest_ai_response = latest_insights['AI Response']
    
    # Constructing the prompt
    prompt = (f"Based on the following insights from the latest video assessment:\n"
              f"Keywords: {latest_insights['keywords']}\n"
              f"Sentiments: {latest_insights['sentiments']}\n"
              f"Topics: {latest_insights['topics']}\n"
              f"Labels: {latest_insights['labels']}\n"
              f"Emotions: {latest_insights['emotions']}\n"
              f"Subject Name: {latest_insights['named_people']}\n"
              f"Duration (seconds): {latest_insights['duration_in_seconds']}\n"
              f"AI Response: {latest_ai_response}\n\n"
              f"New Child Summary: {new_child_summary}\n"
              f"Please provide a plan or activities that could enhance engagement or educational value for the new child. Also consider referring to previous plans (like mention previously assesed subject names) and illustrate how similar strategies could be applied.")
    return prompt
#%%
#  df_response is our DataFrame containing historical data
ai_recommendation = prepare_ai_interaction_with_history(new_child_summary, df_response)

#%%
print("AI Recommendation:", ai_recommendation)
#%%
data = {
    'New Child Summary': [new_child_summary],
    'AI Recommendation': [ai_recommendation]
}

df_recommendation = pd.DataFrame(data)

# Saving to CSV
df_recommendation.to_csv('out/ai_recommendation_for_new_child.csv', index=False)
# %%
df_recommendation.columns
# %%
# =============== END SCRIPT =======================