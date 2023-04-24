import json
import requests
from time import sleep
from tqdm import tqdm
from collections import Counter

from utils.auth_data import token


def write_json(data, filename, mode='w', overwrite=False, encoding='utf-8'):
    """Writes JSON data to a file.

    Args:
        data (dict): The data to write as JSON.
        filename (str): The file path to write to.
        mode (str, optional): File open mode. Either 'w' or 'a'. Defaults to 'w'. 
        overwrite (bool, optional): Whether to overwrite the file. Defaults to False.
        encoding (str, optional): The file encoding. Defaults to 'utf-8'.
    """
    mode = 'w' if overwrite else 'a'
    with open(filename, mode, encoding=encoding) as file:  
        json.dump(data, file, indent=2, ensure_ascii=False)


def get_posts_likes(
    owner_id: int,
    item_id: int, 
    count: int = 1000, 
    offset_step: int = 1000,
    max_likes: int = 10000  
) -> list:
    """Retrieves a list of users who liked a VK post.

    Args:
        owner_id (int): The ID of the post owner.
        item_id (int): The ID of the post.
        count (int, optional): The number of likes to retrieve per request. Defaults to 1000.
        offset_step (int, optional): The offset increment on each request. Defaults to 1000.  
        max_likes (int, optional): The maximum number of likes to retrieve. Defaults to 10000.

    Returns:
        list: A list of user's ids who liked the post.
        None if API limit is reached.
    """   

    result_likes = []
    stop = 0
    for offset in range(0, max_likes, offset_step):
        if stop%3 == 0:  
            sleep(1)  

        url = f"https://api.vk.com/method/likes.getList"
        request_params = {  
                'type': 'post',
                'access_token': token,
                'owner_id': owner_id,
                'count': count,
                'item_id': item_id,
                'offset': offset, 
                'v':5.131  
                }
        req = requests.get(url, params=request_params)
        stop += 1
        response = req.json()
        likes = response.get('response', {}).get('items', [])
        num_likes = response.get('response', {}).get('count', None)  

        result_likes.extend(likes)
        # if there is less than 1000 likes it means there is no need  
        # to do requests further. you already collected all the likes of the post
        if num_likes < 1000:       
            break      

    return result_likes 


def get_group_info(group_name: str, number_of_posts: int) -> list:
    """Gets a specified number of posts from a VK group.

    Args:
        group_name (str): The name of the VK group.
        number_of_posts (int): The number of posts to retrieve.

    Returns:
        list: A list of dictionaries containing post info.
    """

    # only 100 posts for 1 requests we can get from VK 
    count = 100  

    # number of counts needed to parse such number of posts
    counts_amount = number_of_posts // count + 1  

    raw_posts = get_posts(group_name, count=count, counts_amount=counts_amount)  
    posts_data = [get_post_data(post) for post in raw_posts]

    return posts_data


def get_posts(
    group_name: str, 
    count: int = 100, 
    counts_amount: int = 5,
    offset_step: int = 100,  
) -> list:
    """Retrieves posts from a VKontakte group.

    Args:
        group_name (str): The name of the VK group.  
        count (int, optional): The number of posts to retrieve per API request. Defaults to 100.
        counts_amount (int, optional): The number of API requests to make. Defaults to 5.
        offset_step (int, optional): The offset increment on each API request. Defaults to 100.

    Returns:
        list: A list of all posts retrieved from the group.
    """

    all_posts = []
    for offset in tqdm(range(0, count*counts_amount, offset_step)):
        url = "https://api.vk.com/method/wall.get"
        req = requests.get(url, params={
            'domain': group_name,  
            'count': count,
            'access_token': token,
            'offset': offset,
            'extended': 1,
            'fields': 'id',
            'v':5.131  
            })
        posts = req.json()['response']['items']
        all_posts.extend(posts)
    return all_posts


def get_post_data(post: dict) -> dict:
    """Returns a dictionary of parsed data for a single VK post.

    Args:
        post (dict): A dictionary representing one post from the VK API response.

    Returns: 
        dict: A dictionary containing the following post info:
            - id: The post ID. Defaults to -1 if missing from response.
            - owner_id: The ID of the post's owner. Defaults to -1 if missing. 
            - date: The date the post was published. Defaults to -1 if missing.
            - text: The text content of the post. Defaults to -1 if missing. 
            - likes: The number of likes for the post. Defaults to -1 if missing. 
            - reposts: The number of reposts for the post. Defaults to -1 if missing.
            - attachments: The IDs of any attached media. Defaults to -1 if missing.
            - marked_as_ads: Whether the post is marked as an ad. Defaults to -1 if missing.
    """
    post_data = {
        'id': post.get('id', -1),
        'owner_id': post.get('owner_id', -1),
        'date': post.get('date', -1),
        'text': post.get('text', -1),
        'likes': post.get('likes', {}).get('count', -1),
        'reposts': post.get('reposts', {}).get('count', -1),
        'attachments': post.get('attachments', -1),
        'marked_as_ads': post.get('marked_as_ads', -1)
    }
    return post_data 


def get_user_location(user_id: int, token: str) -> tuple:
    """Retrieves a user's city and country based on their friends' locations.

    Args:
        user_id (int): The ID of the user.
        token (str): An access token for the VK API.

    Returns:
        tuple: A tuple containing:
            user_city (str): The most commonly occurring city among the user's friends.
            user_country (str): The most commonly occurring country among the user's friends.
            None if API limit is reached or error occurs. 
    """
    url = f'https://api.vk.com/method/friends.get?user_id={user_id}&fields=city,country&access_token={token}&v=5.131'
    req = requests.get(url)  
    response = req.json()  
    
    cities = []  
    countries = []
    if response.get('error'):       
        if response.get('error')['error_code'] == 6:      
            print('Too many requests per second')
            sleep(1)            
            req = requests.get(url) 
            response = req.json()         
             
        if response.get('error')['error_code'] == 29:       
            print('Limit has reached')
            return None, None        
        else:       
            return None, None   
    
    for friend in response['response']['items']:       
        friend_city = friend.get('city')       
        if friend_city:          
            cities.append(friend['city']['title'])       
        friend_country = friend.get('country')       
        if friend_country:          
            countries.append(friend['country']['title'])  

    user_city = Counter(cities).most_common(1)[0][0] if cities else None       
    user_country = Counter(countries).most_common(1)[0][0] if countries else None     
    
    return user_city, user_country