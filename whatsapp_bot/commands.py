import os
import requests
from django.conf import settings
from .whatsapp_integration import send_whatsapp_file, construct_whatsapp_url  # Replace with your WhatsApp integration logic
import time
import feedparser
# from urllib.parse import urlsplit, urlunsplit
# from concurrent.futures import ThreadPoolExecutor

def classify_file_type(content_type):
    if content_type.startswith('audio'):
        return 'audio'
    elif content_type.startswith('video'):
        return 'video'
    elif content_type.startswith('image'):
        return 'image'
    else:
        return 'document'  # Default to document if type is unknown

def download_file(url, phone_number, businessPhoneNumberId, businessPhoneNumberDisplay):
    try:

        return "Downloading file. Please wait..."

    except requests.exceptions.RequestException as e:
        print("Error downloading file: {e}".format(e))
        return "Error downloading file: {e}".format(e)

def exchange_voucher(data, phone_number, businessPhoneNumberId, businessPhoneNumberDisplay):
    try:

        return "Exchanging Voucher. Please wait..."

    except requests.exceptions.RequestException as e:
        print("Error downloading file: {e}".format(e))
        return "Error downloading file: {e}".format(e)

# def download_youtube(url, phone_number, businessPhoneNumberId, businessPhoneNumberDisplay):
#     try:
#         ydl_opts = {
#             'outtmpl': os.path.join(settings.MEDIA_ROOT, '%(title)s.%(ext)s'),
#         }

#         with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#             result = ydl.extract_info(url, download=True)
#             file_name = ydl.prepare_filename(result)

#         return "YouTube video downloaded: {file_name}".format(file_name)
#     except Exception as e:
#         return f"Error downloading YouTube video: {str(e)}"

# def download_rss(url=None, phone_number='', businessPhoneNumberId='', businessPhoneNumberDisplay='',markdown=False):
#     try:
#         url = url if url else 'https://iono.fm/rss/chan/1940'
#         feed = feedparser.parse(url)

#         if 'bozo_exception' in feed:
#             raise feed.bozo_exception

#         markdown_content = ""
#         rss_link = construct_whatsapp_url(businessPhoneNumberDisplay, f"/rss {url}")
#         title = feed.get('feed')['title']
#         summary = feed.get('feed')['summary']
#         markdown_content += f"*{title}*\n {summary} \n\n"
        
#         file_name = f"{title}_{phone_number}_feed.txt"
#         file_path = f"{settings.MEDIA_ROOT}/{file_name}"
#         file_type = "document"
                
#         for entry in feed.entries:
#             title = entry.get('title', 'No Title')
#             summary = entry.get('summary', 'No Summary')
#             try:
#                 # links = [link['href'] for link in entry.get('links')]
#                     available_links = [(i, link['href']) for i, link in enumerate(entry.get('links', []))]
#                 # link = entry['links'][0]['href']
#                 # link_2 = entry['links'][1]['href'].replace('high', 'low').replace('?p=rss', '') if entry.get('links') else entry.get('link', '#')
#             except Exception as e:
#                 pass
#             markdown_content += f"__________\n- *Download {title}* \n {summary}... \n\n"
#             for i,link in available_links:
#                 # Strip query parameters
#                 # breakpoint()
#                 split_url = urlsplit(link)
#                 clean_link = urlunsplit((split_url.scheme, split_url.netloc, split_url.path, '', '')).replace('medium','low')
#                 command_link = construct_whatsapp_url(businessPhoneNumberDisplay, f"/download {clean_link}")
#                 # command_link = construct_whatsapp_url(businessPhoneNumberDisplay, f"/download {link}")
#                 markdown_content += f"Link {i+1}: \n  `{command_link}` \n"

        

#         with open(file_path, 'w') as file:
#             file.write(markdown_content)


#         # Send the markdown file via WhatsApp
#         # send_whatsapp_file(phone_number, file_path, file_type, businessPhoneNumberId)


#         markdown_content += f"{markdown_content}\n\n\n *Looking for more entries?*\n {file_name} above contains All Available Entries."
#         markdown_content += f"Copy & Share link for fast access:\n`{rss_link}`"
#         return markdown_content[:4090]
#     except Exception as e:
#         return f"Error processing RSS feed: {str(e)}"

# def search_podcasts(query, phone_number='', businessPhoneNumberId='', businessPhoneNumberDisplay=''):
#     url = 'https://castos.com/wp-admin/admin-ajax.php'
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
#     }
#     data = {
#         'search': query,
#         'action': 'feed_url_lookup_search'
#     }

#     response = requests.post(url, headers=headers, data=data)

    
#     file_name = f"{query}_{phone_number}_results.txt"
#     file_path = f"{settings.MEDIA_ROOT}/{file_name}"
#     file_type = "document"

#     if response.status_code == 200:
#         markdown_content = f"# Podcast Results for *{query}*\n\n"
#         for entry in response.json()['data']:
#             title = entry.get('title', 'No Title')
#             summary = entry.get('description', 'No Description')
#             link = entry.get('url', 'No URL')
#             command_link = construct_whatsapp_url(businessPhoneNumberDisplay, f"/rss {link}")
#             markdown_content += f">>> \n- *View {title}* \n {summary} \n `{command_link}`\n\n"        

#         with open(file_path, 'w') as file:
#             file.write(markdown_content)


#         # Send the markdown file via WhatsApp
#         # send_whatsapp_file(phone_number, file_path, file_type, businessPhoneNumberId)

#         return markdown_content[:4090]
#     else:
#         return {'error': 'Failed to fetch podcasts'}
