from bardapi import Bard, bard_api_key

# The Bard API Key is set via the environment variable
# No need to set it again in the script.

# Create an instance of Bard
bard = Bard(token=bard_api_key, timeout=30)

# Get an answer from the Bard
response = bard.get_answer("나와 내 동년배들이 좋아하는 뉴진스에 대해서 알려줘")
print(response['content'])

# Continue the conversation
response = bard.get_answer("What is my last prompt??")
print(response['content'])
