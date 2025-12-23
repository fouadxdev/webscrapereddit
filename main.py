import requests
import json
import csv
import time
from bs4 import BeautifulSoup

# Function main scraper to get content from reddit
def scrape_reddit() -> list[dict]:
    subreddits = [
        'https://www.reddit.com/r/cscareerquestions',
        'https://www.reddit.com/r/programming',
        'https://www.reddit.com/r/coding'
    ]

    all_data = []
    for url in subreddits:
        headers = {
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    subreddit_name = url.split('/')[-1]
    print(f'Scraping for {subreddit_name}')
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')


        subreddit_data = {
            'subreddit_name' :subreddit_name ,
            'url': url,
            'title': soup.title.string if soup.title else 'No title', 
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),

        }

        topics = []
        for heading in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            text = heading.get_text(strip=True)

            if text and len(text) > 3:
                if any(keyword in text.lower() for keyword in ['jobs', 'interview', 'AI', 'Programming', 'Computer Science', 'Data', 'coding']):
                    topics.append({
                        'title': text,
                        'type': 'topic'
                    })

        discussions = []
        seen_urls = set()

        for link in soup.find_all('a', href=True):
            text = link.get_text(strip=True)
            href = link['href']

            if text and len(text) > 1 and '/comments/' in href and href not in seen_urls:
                seen_urls.add(href)

                discussions.append({
                    'title': text[:100] + '...' if len(text) > 100 else text,
                    'url':href,
                    'type': 'discussion'
                })

        subreddit_data['topics'] = topics
        subreddit_data['discussions'] = discussions

        all_data.append(subreddit_data)
        time.sleep(2)

    except Exception as e:
        print(f'Error: {e}')

    return all_data

#Save data to Json and Csv
#Json
def save_scraped_data(data, filename_json='reddit_topics.json', filename_csv='reddit_topics.csv'):
    if not data:
        print(f'No Data')
        return
    
    try:
        with open(filename_json, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=True)
            print(f'Topics saved: {filename_json}')
    except Exception as e:
        print("ERROR:", e)


#CSv

    try:
        with open(filename_csv, 'w', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Subreddit', 'Type', 'Title', 'URL', 'Scraped_at'])
            for subreddit_data in data:
                subreddit = subreddit_data['subreddit_name']
                scraped_at = subreddit_data['scraped_at']

                for topic in subreddit_data.get('topics', []):
                    writer.writerow([subreddit, topic['type'], topic['title'],'', scraped_at])

                for discussion in subreddit_data.get('discussions', []):
                    writer.writerow([subreddit, discussion['type'], discussion['title'], discussion['url'], scraped_at])

            print(f'All topics Save to Respective Files')
    except Exception as e: 
        print("ERROR:", e)

            
            
            
    #Execution
def main() -> None:
    data = scrape_reddit()

    if data:
        print(f'Processing data....')
        total_topics = 0
        total_discussions = 0

        for subreddit_data in data:
            topics_count = len(subreddit_data.get('topics' , []))
            discussions_count = len(subreddit_data.get('discussions' , []))


            total_topics += topics_count
            total_discussions += discussions_count

        print(f'\nTotal {total_topics}: Topics, {discussions_count}L Discussions')
        save_scraped_data(data)
    else:
        print('No Data Returned')

if __name__ == "__main__":
    main()